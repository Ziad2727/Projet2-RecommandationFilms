from pathlib import Path
import streamlit as st
import base64
from auth import login_form, logout


# -------------------------------------------------
# CONFIG (TOUJOURS EN PREMIER)
# -------------------------------------------------
st.set_page_config(
    page_title="Popcorn Analytics",
    page_icon="assets/P_logo.png",
    layout="wide",
)


# -------------------------------------------------
# CHARGEMENT CSS (VERSION ULTRA SIMPLE)
# -------------------------------------------------
css_path = Path(__file__).parent / "style.css"

with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------------------------------
# LOGO
# -------------------------------------------------
LOGO_PATH = Path(__file__).parent / "assets" / "LogoProjet2.png"


def img_to_b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


if LOGO_PATH.exists():
    b64 = img_to_b64(LOGO_PATH)
    st.markdown(
        f"""
        <div class="top-logo-center">
            <img src="data:image/png;base64,{b64}">
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None


# -------------------------------------------------
# PAGE LOGIN
# -------------------------------------------------
if not st.session_state.logged_in:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display: none;}
        .block-container {
            max-width: 650px !important;
            margin: auto !important;
        }
        .top-logo-center {
            text-align: center !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        login_form()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# -------------------------------------------------
# SIDEBAR (UTILISATEUR CONNECTÉ) — juste le nom, pas de bouton ici
# -------------------------------------------------
with st.sidebar:
    pass


# -------------------------------------------------
# MASQUER PAGE FICHE DANS SIDEBAR
# -------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] a[href*="Noussuggestions"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# NAVIGATION OFFICIELLE STREAMLIT
# -------------------------------------------------
pages = [
    st.Page("pages/1_a_l_affiche.py", title="À l'affiche", url_path="affiche"),
    st.Page("pages/2_selection_patrimoniale.py", title="Sélection patrimoniale", url_path="patrimoine"),
    st.Page("pages/4_statistiques_du_catalogue.py", title="Statistiques du catalogue", url_path="stats"),
    st.Page("pages/5_popcorn_analytics.py", title="Popcorn Analytics", url_path="popcorn"),
    st.Page("pages/Noussuggestions.py", title="Fiche film", url_path="Noussuggestions"),
]

# Page Favoris uniquement si user connecté
if st.session_state.role == "user":
    pages.insert(
        2,
        st.Page("pages/3_vos_favoris.py", title="Vos favoris", url_path="favoris")
    )

pg = st.navigation(pages)
pg.run()