import streamlit as st
import pandas as pd
import numpy as np
import ast
import html as html_module
from pathlib import Path

from sklearn.neighbors import NearestNeighbors
from scipy.sparse import load_npz
from deep_translator import GoogleTranslator

# ==================================================
# CSS
# ==================================================
def load_css():
    css_path = Path(__file__).resolve().parent.parent / "app/style.css"
    if not css_path.exists():
        css_path = Path(__file__).resolve().parent.parent / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()

st.markdown("""
<style>
[data-testid="stSidebarNav"] a[href$="/fiche"],
[data-testid="stSidebarNav"] a[href*="/fiche"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def traduire_texte(texte):
    if texte:
        try: return GoogleTranslator(source='auto', target='fr').translate(texte)
        except Exception: return texte
    return ""

# ==================================================
# HELPERS
# ==================================================
def clean_text(x, fallback="—"):
    if x is None: return fallback
    x = str(x).strip()
    return fallback if x == "" or x.lower() in {"none","nan","null"} else x

def format_genres_list(x, fallback="—"):
    if x is None or (isinstance(x, float) and pd.isna(x)): return fallback
    if isinstance(x, list):
        genres = [str(g).strip() for g in x if str(g).strip()]
    else:
        s = str(x).strip()
        if s == "" or s.lower() in {"none","nan","null"}: return fallback
        s = s.strip("[]").replace("'","").replace('"',"")
        genres = [g.strip() for g in s.split(",") if g.strip()]
    seen = set()
    unique = []
    for g in genres:
        gl = g.lower()
        if gl not in seen:
            seen.add(gl)
            unique.append(g)
    return ", ".join(unique) if unique else fallback

def parse_pylist(x):
    if x is None or (isinstance(x, float) and pd.isna(x)): return []
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, list): return x
    s = str(x).strip()
    if s == "" or s.lower() in {"none","nan","null"}: return []
    try:
        v = ast.literal_eval(s)
        return v if isinstance(v, list) else []
    except Exception:
        return [p.strip() for p in s.strip("[]").replace("'","").replace('"',"").split(",") if p.strip()]

def truncate_synopsis(text, max_words=40):
    if text is None or (isinstance(text, float) and pd.isna(text)): return ""
    s = str(text).strip()
    if s == "" or s.lower() in {"none","nan","null"}: return ""
    words = s.split()
    if len(words) <= max_words: return s
    return " ".join(words[:max_words]) + " ..."

def poster_with_synopsis(img_url, synopsis_text, small=False):
    safe_text = html_module.escape(synopsis_text)
    sm = " poster-sm" if small else ""
    return f'''<div class="poster-hover-wrap{sm}">
        <img src="{img_url}" alt="poster" onerror="this.style.display='none'">
        <div class="poster-synopsis-overlay">
            <div class="poster-synopsis-text">{safe_text}</div>
        </div>
    </div>'''

def get_base_dir():
    return Path(__file__).resolve().parent.parent.parent

# ==================================================
# LOADERS
# ==================================================
@st.cache_data
def load_movies_parquet():
    df = pd.read_parquet(get_base_dir() / "data" / "processed" / "movies_fr_final.parquet")
    if "id_film" in df.columns: df["id_film"] = df["id_film"].astype(str)
    return df

@st.cache_data
def load_knn_encoded_parquet():
    df = pd.read_parquet(get_base_dir() / "data" / "processed" / "knn_df_encoded.parquet")
    if "id_film" in df.columns: df["id_film"] = df["id_film"].astype(str)
    return df

# ==================================================
# ML PIPELINE — chargement direct de X_final (sauvegardé depuis le notebook)
# ==================================================
OVERSAMPLE = 80

@st.cache_resource
def load_knn_pipeline(knn_encoded_df):
    df = knn_encoded_df.copy()
    df["id_film"] = df["id_film"].astype(str)
    df["nombre_votes"] = pd.to_numeric(df["nombre_votes"], errors="coerce").fillna(0).astype(int)

    # Parse genres_list (le parquet peut stocker comme listes ou strings)
    df["genres_list"] = df["genres_list"].apply(parse_pylist)

    # Charger X_final identique au notebook
    X_final = load_npz(get_base_dir() / "data" / "processed" / "X_final.npz")

    # Fit KNN (même config que le notebook)
    knn_model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=OVERSAMPLE)
    knn_model.fit(X_final)
    print(f"STREAMLIT - X_final chargé: {X_final.shape}")

    # Pop globale pour re-ranking
    pop_global_log = np.log1p(df["nombre_votes"].fillna(0).astype(float).values)
    pop_global_max = pop_global_log.max()

    return df, X_final, knn_model, pop_global_log, pop_global_max


def recommend_from_film_id(film_id, df_knn, X_final, knn_model, df_display, pop_global_log, pop_global_max, k=5, oversample=OVERSAMPLE, alpha_pop=0.26):
    film_id = str(film_id)
    match = df_knn.index[df_knn["id_film"] == film_id]
    if len(match) == 0:
        return df_display.iloc[0:0].copy()
    idx = int(match[0])

    n = min(oversample, X_final.shape[0])
    distances, indices = knn_model.kneighbors(X_final[idx], n_neighbors=n)
    distances, indices = distances.ravel(), indices.ravel()

    # Exclure le film lui-même
    mask = indices != idx
    distances, indices = distances[mask], indices[mask]
    if len(indices) == 0:
        return df_display.iloc[0:0].copy()

    # Re-ranking avec bonus popularité (même logique que le notebook — AVANT le filtrage genres)
    if alpha_pop > 0 and "nombre_votes" in df_knn.columns:
        pop_norm = pop_global_log[indices] / (pop_global_max + 1e-9)
        sim = 1 - distances
        sim_norm = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)
        final = (1 - alpha_pop) * sim_norm + alpha_pop * pop_norm
        order = np.argsort(final)[::-1]
        indices = indices[order]
        distances = distances[order]

    # Filtrer genres incompatibles (APRÈS le re-ranking, comme le notebook)
    GENRE_EXCLUSIONS = {
        "Action": ["Comédie", "Romance", "Famille", "Fantastique"],
        "Crime" : ["Comédie","Famille"],
        "Drame": ["Animation", "Famille"],
        "Thriller": ["Comédie", "Famille"],
        "Horreur": ["Animation", "Comédie", "Romance", "Famille"],
        "Science-fiction": ["Comédie", "Romance", "Famille"],
        "Comédie": ["Horreur", "Guerre"],
        "Animation": ["Horreur", "Guerre", "Crime"],
        "Romance": ["Horreur",],
        "Famille": ["Horreur", "Guerre", "Crime", "Thriller"],
    }

    source_main_genre = df_knn.loc[idx, "main_genre"]
    excluded = GENRE_EXCLUSIONS.get(source_main_genre, [])
    
    if excluded:
        excluded_set = set(excluded)
        rec_genres = df_knn.loc[indices, "genres_list"]
        mask_compatible = rec_genres.apply(
            lambda g: len(set(g).intersection(excluded_set)) == 0 if isinstance(g, list) else True
        )
        indices = indices[mask_compatible.values]
        distances = distances[mask_compatible.values]
    if len(indices) == 0:
        return df_display.iloc[0:0].copy()

    rec_ids = df_knn.loc[indices[:k * 3], "id_film"].astype(str).tolist()
    out = df_display[df_display["id_film"].isin(rec_ids)].copy()
    out["__rank"] = out["id_film"].map({mid: i for i, mid in enumerate(rec_ids)})
    return out.sort_values("__rank").drop(columns="__rank").head(k).reset_index(drop=True)

# ==================================================
# SESSION / DATA
# ==================================================
if "favorites" not in st.session_state:
    st.session_state["favorites"] = set()

df_movies = load_movies_parquet()
knn_encoded_df = load_knn_encoded_parquet()
df_knn, X_final, knn_model, pop_global_log, pop_global_max = load_knn_pipeline(knn_encoded_df)

# ==================================================
# FILM SELECTION
# ==================================================
film_id = st.session_state.get("film_id")
if not film_id:
    qp = st.query_params.get("film_id")
    film_id = qp[0] if isinstance(qp, list) and qp else qp

if not film_id:
    st.warning("Aucun film sélectionné.")
    if st.button("Retour à l'affiche"):
        st.switch_page("pages/1_a_l_affiche.py")
    st.stop()

film_id = str(film_id)
row = df_movies[df_movies["id_film"] == film_id]
if row.empty:
    st.error("Film introuvable.")
    if st.button("Retour à l'affiche"):
        st.switch_page("pages/1_a_l_affiche.py")
    st.stop()

movie = row.iloc[0]

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown('<div class="sidebar-section-title"> Profil</div>', unsafe_allow_html=True)
    username = st.session_state.get("username", "Invité")
    st.markdown(f"Bienvenue **{username}**")
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    if st.button("Se déconnecter", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==================================================
# FICHE FILM
# ==================================================
st.markdown(f'<div class="page-title">{html_module.escape(clean_text(movie.get("titre_francais"), fallback="Fiche film"))}</div>', unsafe_allow_html=True)
st.markdown('<div class="neon-sep"></div>', unsafe_allow_html=True)

if username != "Invité":
    is_fav = str(movie["id_film"]) in st.session_state["favorites"]
    fav_label = "💖 Retirer des favoris" if is_fav else "🤍 Ajouter aux favoris"
    if st.button(fav_label, key=f"fav_toggle_{movie['id_film']}"):
        mid = str(movie["id_film"])
        if is_fav:
            st.session_state["favorites"].discard(mid)
        else:
            st.session_state["favorites"].add(mid)
        st.rerun()

colA, colB = st.columns([1, 2], vertical_alignment="top")

with colA:
    url_affiche = movie.get("url_affiche", None)
    if pd.notna(url_affiche) and url_affiche:
        st.image(url_affiche, use_container_width=True)

langue = movie.get('langue_originale', "")
langue = str(langue) if langue else ""
langue = langue.strip("[]'\" ").replace("'", "").replace('"', '')
if "," in langue:
    langue = ", ".join(l.strip().capitalize() for l in langue.split(",") if l.strip())
else:
    langue = langue.strip().capitalize() if langue else "N/A"

with colB:
    st.markdown(f"**Titre :** {clean_text(movie.get('titre_francais'))}")

    knn_row = knn_encoded_df[knn_encoded_df["id_film"] == film_id]
    if not knn_row.empty:
        genres_val = knn_row.iloc[0].get("genres_list", [])
    else:
        genres_val = movie.get("genres_list")
        if genres_val is None or (isinstance(genres_val, float) and pd.isna(genres_val)):
            genres_val = movie.get("genres")
    st.markdown(f"**Genres :** {format_genres_list(genres_val)}")

    tagline_original = clean_text(movie.get("slogan"))
    tagline_final = traduire_texte(tagline_original) if movie.get("langue_originale") != "fr" else tagline_original
    st.markdown(f"**Tagline :** {tagline_final}")

    synopsis_final = clean_text(movie.get("synopsis_fr")) if movie.get("synopsis_fr") else clean_text(movie.get("synopsis"))
    st.markdown(f"**Synopsis :** {synopsis_final}")

    date_sortie = movie.get("date_sortie")
    date_formatee = pd.to_datetime(date_sortie).strftime("%d/%m/%Y") if pd.notna(date_sortie) else ""
    st.markdown(f"**Date de sortie :** {date_formatee}")
    st.markdown(f"**Réalisateur :** {clean_text(movie.get('noms_realisateurs'))}")
    st.markdown(f"**Acteurs :** {clean_text(movie.get('principaux_acteurs'))}")
    st.markdown(f"**Zone :** {clean_text(movie.get('zone_de_production'))}")
    st.markdown(f"**Langue originale :** {langue}")
    st.markdown(f"**Note moyenne :** {clean_text(movie.get('note_moyenne'))}")

st.markdown('<div class="neon-sep"></div>', unsafe_allow_html=True)

# ==================================================
# SUGGESTIONS
# ==================================================
st.markdown('<div class="page-title" style="font-size:1.2rem; margin-top:8px;">Films suggérés</div>', unsafe_allow_html=True)
st.markdown('<hr style="border:none; height:2px; background:linear-gradient(90deg, transparent, rgba(255,45,120,0.5), transparent); margin:16px 0;">', unsafe_allow_html=True)

rec_df = recommend_from_film_id(
    film_id=film_id, df_knn=df_knn, X_final=X_final,
    knn_model=knn_model, df_display=df_movies,
    pop_global_log=pop_global_log, pop_global_max=pop_global_max,
    k=5, oversample=OVERSAMPLE, alpha_pop=0.26,
)

if rec_df.empty:
    st.info("Aucune recommandation trouvée.")
else:
    cols_count = 5
    for row_start in range(0, len(rec_df), cols_count):
        cols = st.columns(cols_count, gap="medium")
        for j, col in enumerate(cols):
            idx = row_start + j
            if idx < len(rec_df):
                m = rec_df.iloc[idx]
                mid = str(m["id_film"])
                mt = m.get("titre_francais", "")
                mi = m.get("url_affiche", "")
                mi = mi if pd.notna(mi) else ""
                sfr = m.get("synopsis_fr", "")
                if sfr and str(sfr).strip().lower() not in {"", "none", "nan", "null"}:
                    synopsis_rec = str(sfr)
                else:
                    synopsis_rec = str(m.get("synopsis", "")) if pd.notna(m.get("synopsis", "")) else ""
                syn_rec = truncate_synopsis(synopsis_rec, 25)
                date_s = m.get("date_sortie")
                date_f = pd.to_datetime(date_s).strftime("%d/%m/%Y") if pd.notna(date_s) else ""

                with col:
                    if mi:
                        st.markdown(poster_with_synopsis(mi, syn_rec, small=True), unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;font-weight:700;font-size:0.85rem;margin-top:4px;min-height:40px;display:flex;align-items:center;justify-content:center;'>{html_module.escape(mt)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;font-size:0.75rem;color:#a89bb5 !important;margin-bottom:6px;'>{date_f}</div>", unsafe_allow_html=True)
                    if st.button("Voir la fiche", key=f"rec_{mid}", use_container_width=True):
                        st.session_state["film_id"] = mid
                        st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)

# ==================================================
# NAVIGATION
# ==================================================
col_l, _, _, _ = st.columns([1, 1, 1, 1])
with col_l:
    if st.button("⬅ Retour à l'affiche", key="back_btn"):
        st.switch_page("pages/1_a_l_affiche.py")