import streamlit as st
import pandas as pd
import html as html_module
from pathlib import Path

def load_css():
    css_path = Path(__file__).resolve().parent.parent / "style.css"
    if not css_path.exists():
        css_path = Path(__file__).resolve().parent.parent / "app/style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
@st.cache_data
def load_movies():
    base_dir = Path(__file__).resolve().parent.parent.parent
    df = pd.read_parquet(base_dir / "data" / "processed" / "movies_fr_final.parquet")
    if "id_film" in df.columns:
        df["id_film"] = df["id_film"].astype(str)
    return df

def truncate_synopsis(text, max_words=40):
    if text is None or (isinstance(text, float) and pd.isna(text)): return ""
    s = str(text).strip()
    if s == "" or s.lower() in {"none", "nan", "null"}: return ""
    words = s.split()
    if len(words) <= max_words: return s
    return " ".join(words[:max_words]) + " (...)"

def poster_with_synopsis(img_url, synopsis_text, small=False):
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
if "favorites" not in st.session_state:
    st.session_state["favorites"] = set()
if "film_id" not in st.session_state:
    st.session_state["film_id"] = None

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-section-title"> Profil</div>', unsafe_allow_html=True)
    username = st.session_state.get("username", "Invité")
    st.markdown(f"Bienvenue **{username}**")
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    if st.button(" Se déconnecter", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --------------------------------------------------
# DATA
# --------------------------------------------------
df = load_movies()

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------
st.markdown('<div class="page-title"> Vos Favoris</div>', unsafe_allow_html=True)

fav_ids = list(st.session_state["favorites"])

if not fav_ids:
    st.markdown('<div class="page-subtitle">Aucun favori pour le moment</div>', unsafe_allow_html=True)
    st.stop()

fav_df = df[df["id_film"].isin(fav_ids)].copy()
fav_df = fav_df.sort_values("titre_francais")

nb = len(fav_df)
st.markdown(f'<div class="page-subtitle">{nb} film{"s" if nb > 1 else ""} dans vos favoris</div>', unsafe_allow_html=True)
st.markdown('<hr style="border:none; height:2px; background:linear-gradient(90deg, transparent, rgba(255,45,120,0.5), transparent); margin:16px 0;">', unsafe_allow_html=True)

# --------------------------------------------------
# MOVIE CARDS – same layout as a_laffiche
# --------------------------------------------------
cols_count = 3
for row_start in range(0, len(fav_df), cols_count):
    cols = st.columns(cols_count, gap="small")
    for j, col in enumerate(cols):
        idx = row_start + j
        if idx < len(fav_df):
            movie = fav_df.iloc[idx]
            mid = str(movie["id_film"])
            title = movie.get("titre_francais", "")
            genres = ", ".join(movie.get("genres", []))
            date = movie.get("date_sortie", "")
            url = movie.get("url_affiche", "")
            note = movie.get("note_moyenne", None)
            synopsis = movie.get("synopsis_fr", "") or movie.get("synopsis", "")
            year = str(date)[:4] if pd.notna(date) else ""
            syn_text = truncate_synopsis(synopsis, 40)

            with col:
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    if pd.notna(url) and url:
                        st.markdown(poster_with_synopsis(url, syn_text), unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div style='min-height:75px;'><strong>{title}</strong></div>", unsafe_allow_html=True)
                    st.markdown(genres)
                    st.caption(year)
                    if pd.notna(note):
                        st.caption(f"⭐ {note:.1f}")
                    b1, b2 = st.columns([1.8, 1])
                    with b1:
                        if st.button("Infos", key=f"nav_{mid}", use_container_width=True):
                            st.session_state["film_id"] = mid
                            st.switch_page("pages/Noussuggestions.py")
                    with b2:
                        if st.button("🗑", key=f"fav_rm_{mid}", use_container_width=True):
                            st.session_state["favorites"].discard(mid)
                            st.rerun()

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)