import streamlit as st
import pandas as pd
import unicodedata
import ast
import re
import html as html_module
from pathlib import Path



def load_css():
    css_path = Path(__file__).resolve().parent.parent / "app/style.css"
    if not css_path.exists():
        css_path = Path(__file__).resolve().parent.parent / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()

st.set_page_config(layout="wide")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / "data" / "processed" / "movies_fr_final.parquet"
    df = pd.read_parquet(data_path)
    if "id_film" in df.columns:
        df["id_film"] = df["id_film"].astype(str)
    return df

def strip_accents(s):
    if s is None: return ""
    s = str(s)
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def norm(s): return strip_accents(s).lower().strip()

def parse_genres_list(x):
    if x is None or (isinstance(x, float) and pd.isna(x)): return []
    if isinstance(x, list): return [str(g).strip() for g in x if str(g).strip()]
    s = str(x).strip()
    if s == "" or s.lower() in {"none", "nan", "null"}: return []
    try:
        v = ast.literal_eval(s)
        if isinstance(v, list): return [str(g).strip() for g in v if str(g).strip()]
    except Exception: pass
    s2 = s.strip("[]").replace("'", "").replace('"', "")
    return [p.strip() for p in re.split(r"[|,;]", s2) if p.strip()]

def truncate_synopsis(text, max_words=40):
    """Return first max_words words + ... if truncated."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    s = str(text).strip()
    if s == "" or s.lower() in {"none", "nan", "null"}:
        return ""
    words = s.split()
    if len(words) <= max_words:
        return s
    return " ".join(words[:max_words]) + " ..."

def poster_with_synopsis(img_url, synopsis_text, small=False):
    """Generate HTML for a poster with darkening + synopsis overlay on hover."""
    safe_text = html_module.escape(synopsis_text)
    sm = " poster-sm" if small else ""
    return f'''<div class="poster-hover-wrap{sm}">
        <img src="{img_url}" alt="poster" onerror="this.style.display='none'">
        <div class="poster-synopsis-overlay">
            <div class="poster-synopsis-text">{safe_text}</div>
        </div>
    </div>'''

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "favorites" not in st.session_state: st.session_state["favorites"] = set()
if "film_id" not in st.session_state: st.session_state["film_id"] = None
if "page" not in st.session_state: st.session_state.page = 1

# --------------------------------------------------
# DATA
# --------------------------------------------------
df = load_data()
df["genres_list_parsed"] = df.get("genres_list", pd.Series([[]] * len(df))).apply(parse_genres_list)
df["genres_norm_set"] = df["genres_list_parsed"].apply(lambda lst: {norm(g) for g in lst})
df["annee_sortie"] = df["date_sortie"].apply(lambda x: x.year if pd.notna(x) else None)

GENRES_WANTED = ['Action',
 'Animation',
 'Aventure',
 'Biographie',
 'Comédie',
 'Comédie musicale',
 'Crime',
 'Documentaire',
 'Drame',
 'Famille',
 'Fantastique',
 'Film noir',
 'Guerre',
 'Histoire',
 'Musique',
 'Mystère',
 'Romance',
 'Science-fiction',
 'Thriller',
 'Western']
zones_disponibles = sorted(df["zone_de_production"].dropna().unique().tolist()) if "zone_de_production" in df.columns else []

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown('<div class="sidebar-section-title"> Profil</div>', unsafe_allow_html=True)
    username = st.session_state.get("username", "Invité")
    st.markdown(f"Bienvenue **{username}**")
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    if st.button("Se déconnecter", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==================================================
# PAGE HEADER
# ==================================================
st.markdown('<div class="page-title"> A l\'affiche dans votre Cinéma Creusois</div>', unsafe_allow_html=True)
st.markdown('<hr style="border:none; height:2px; background:linear-gradient(90deg, transparent, rgba(255,45,120,0.5), transparent); margin:16px 0;">', unsafe_allow_html=True)

# ==================================================
# FILTRES & TRI – Valeurs par défaut
# ==================================================
search_query = ""
selected_genres = []
selected_zones = []
note_min_filter = 0.0
annee_range = None
TRI_OPTIONS = {"Note décroissante":("note_moyenne",False),"Note croissante":("note_moyenne",True),"Nombre de votes":("nombre_votes",False),"Plus récents d'abord":("date_sortie",False),"Plus anciens d'abord":("date_sortie",True), "Alphabetique A-Z":("titre_francais",True),
"Alphabetique Z-A":("titre_francais",False)}
tri_choisi = "Note décroissante"

with st.expander("Filtres", expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        search_query = st.text_input("Rechercher", "", placeholder="Titre / réalisateur / acteur", key="search_main")
        selected_genres = st.multiselect("Genre", options=GENRES_WANTED, default=[], placeholder="Choisir des genres...", key="genres_main")
    with fc2:
        selected_zones = st.multiselect("Zone de production", options=zones_disponibles, default=[], placeholder="Choisir des zones...", key="zones_main") if zones_disponibles else []
        note_min_filter = st.slider("Note minimum", 0.0, 10.0, 0.0, 0.5, format="%.1f", key="note_main") if "note_moyenne" in df.columns else 0.0
    with fc3:
        annees_disponibles = df["annee_sortie"].dropna()
        if not annees_disponibles.empty:
            min_a, max_a = int(annees_disponibles.min()), int(annees_disponibles.max())
            annee_range = st.slider("Année de sortie", min_a, max_a, (min_a, max_a), key="annee_main")
    appliquer_filtres = st.button("Appliquer les filtres")
    reset_filtres = st.button("↺ Réinitialiser les filtres", key="reset_filters_btn")
with st.expander("Tri", expanded=False):
    tri_choisi = st.selectbox("Trier par", list(TRI_OPTIONS.keys()), index=0, key="tri_main")
    appliquer_tri = st.button("Appliquer le tri")

# ==================================================
# RESET FILTRES
# ==================================================

if reset_filtres:

    keys_to_reset = [
        "search_main",
        "genres_main",
        "zones_main",
        "note_main",
        "annee_main",
        "tri_main"
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    if "apply_filters" in st.session_state:
        st.session_state.apply_filters = False

    st.rerun()
# ==================================================
# FILTERING
# ==================================================

if "apply_filters" not in st.session_state:
    st.session_state.apply_filters = False

if appliquer_filtres:
    st.session_state.apply_filters = True

if appliquer_tri:
    st.session_state.apply_filters = True


filtered_df = df.copy()

if st.session_state.apply_filters:

    # Recherche
    if search_query:
        q = norm(search_query)
        mask = filtered_df["titre_francais"].fillna("").map(norm).str.contains(q, na=False)

        if "noms_realisateurs" in filtered_df.columns:
            mask |= filtered_df["noms_realisateurs"].fillna("").map(norm).str.contains(q, na=False)

        if "principaux_acteurs" in filtered_df.columns:
            mask |= filtered_df["principaux_acteurs"].fillna("").map(norm).str.contains(q, na=False)

        filtered_df = filtered_df[mask]

    # Année
    if annee_range is not None:
        filtered_df = filtered_df[
            (filtered_df["annee_sortie"] >= annee_range[0]) &
            (filtered_df["annee_sortie"] <= annee_range[1])
        ]

    # Genres
    if selected_genres:
        sel_n = {norm(g) for g in selected_genres}
        filtered_df = filtered_df[
            filtered_df["genres_norm_set"].apply(
                lambda s: bool(s & sel_n) or any(sg in fg or fg in sg for fg in s for sg in sel_n)
            )
        ]

    # Note
    if "note_moyenne" in filtered_df.columns and note_min_filter > 0.0:
        filtered_df = filtered_df[filtered_df["note_moyenne"] >= note_min_filter]

    # Zone
    if selected_zones and "zone_de_production" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["zone_de_production"].isin(selected_zones)]


# ==================================================
# TRI
# ==================================================

tri_col, tri_asc = TRI_OPTIONS[tri_choisi]

if tri_col in filtered_df.columns:
    filtered_df = filtered_df.sort_values(tri_col, ascending=tri_asc, na_position="last")


# ==================================================
# INFO NOMBRE DE FILMS
# ==================================================

st.markdown(
    f'<div class="filter-count">{len(filtered_df)} film{"s" if len(filtered_df)>1 else ""} après filtrage</div>',
    unsafe_allow_html=True
)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)


# ==================================================
# PAGINATION SETUP
# ==================================================
PER_PAGE = 21
total_pages = max(1, (len(filtered_df) + PER_PAGE - 1) // PER_PAGE)
st.session_state.page = max(1, min(st.session_state.page, total_pages))
start = (st.session_state.page - 1) * PER_PAGE
page_movies = filtered_df.iloc[start:start + PER_PAGE]

# ==================================================
# MOVIE CARDS – poster with synopsis overlay
# ==================================================
for row_start in range(0, len(page_movies), 3):
    cols = st.columns(3, gap="small")
    for j, col in enumerate(cols):
        idx = row_start + j
        if idx < len(page_movies):
            movie = page_movies.iloc[idx]
            mid = movie["id_film"]
            title = movie.get("titre_francais", "")
            genres = ", ".join(movie.get("genres", []))
            date = movie.get("date_sortie", "")
            url = movie.get("url_affiche", "")
            note = movie.get("note_moyenne", None)
            synopsis = movie.get("synopsis_fr", "") or movie.get("synopsis", "")
            year = str(date)[:4] if pd.notna(date) else ""
            is_fav = mid in st.session_state["favorites"]
            syn_text = truncate_synopsis(synopsis, 40)
            

            with col:
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    if pd.notna(url) and url:
                        st.markdown(poster_with_synopsis(url, syn_text), unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div style='min-height:75px;'><strong>{title}</strong></div>", unsafe_allow_html=True)
                    st.caption(genres)
                    st.caption(year)
                    if pd.notna(note): st.caption(f"⭐ {note:.1f}")
                    b1, b2 = st.columns([1.8, 1])
                    with b1:
                        if st.button("Infos", key=f"nav_{mid}", use_container_width=True):
                            st.session_state["film_id"] = mid
                            st.switch_page("pages/Noussuggestions.py")
                    with b2:
                        if username != "Invité":
                            heart = "💖" if is_fav else "🤍"
                            if st.button(heart, key=f"fav_{mid}", use_container_width=True):
                                if is_fav: st.session_state["favorites"].discard(mid)
                                else: st.session_state["favorites"].add(mid)
                                st.rerun()
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ==================================================
# PAGINATION – compact ‹ 1 2 ... N ›
# ==================================================
def build_page_numbers(current, total):
    pages = set()
    for p in range(1, min(5, total+1)): pages.add(p)
    for p in range(max(1, total-3), total+1): pages.add(p)
    for p in range(max(1, current-1), min(total+1, current+2)): pages.add(p)
    pages = sorted(pages)
    result = []
    for i, p in enumerate(pages):
        if i > 0 and p - pages[i-1] > 1: result.append("...")
        result.append(p)
    return result

st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="neon-sep"></div>', unsafe_allow_html=True)

cur = st.session_state.page
pnums = build_page_numbers(cur, total_pages)

n_slots = len(pnums) + 2
pad = max(2, (14 - n_slots) // 2)
layout = [pad] + [1]*n_slots + [pad]
all_c = st.columns(layout)

with all_c[1]:
    if st.button("‹", key="pag_prev", use_container_width=True):
        if cur > 1: st.session_state.page = cur - 1; st.rerun()

for i, pn in enumerate(pnums):
    with all_c[i+2]:
        if pn == "...":
            st.markdown('<div style="text-align:center;padding-top:5px;color:#a89bb5;font-size:0.75rem;">···</div>', unsafe_allow_html=True)
        else:
            if st.button(str(pn), key=f"pag_{pn}", disabled=(pn==cur), use_container_width=True):
                st.session_state.page = pn; st.rerun()

with all_c[-2]:
    if st.button("›", key="pag_next", use_container_width=True):
        if cur < total_pages: st.session_state.page = cur + 1; st.rerun()

st.markdown(f'<div style="text-align:center;color:#a89bb5;font-size:0.78rem;margin-top:-180px;">Page {cur} / {total_pages}</div>', unsafe_allow_html=True)

# ==================================================
# FAVORITES
# ==================================================
if st.session_state["favorites"] and username != "Invité":
    st.markdown('<div class="neon-sep"></div>', unsafe_allow_html=True)
    st.write("### 💖 Vos films favoris")
    fav_movies = df[df["id_film"].isin(st.session_state["favorites"])]
    for _, m in fav_movies.iterrows():
        st.write(f"- {m['titre_francais']} ({str(m['date_sortie'])[:4]})")