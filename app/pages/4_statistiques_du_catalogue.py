import streamlit as st
import streamlit.components.v1 as components

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-section-title"> Profil</div>', unsafe_allow_html=True)
    username = st.session_state.get("username", "Invité")
    st.markdown(f"Bienvenue **{username}**")
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    if st.button("Se déconnecter", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.set_page_config(page_title="Statistiques du catalogue", layout="wide")


url = "https://app.powerbi.com/view?r=eyJrIjoiNTU2ZWUzM2QtODA1Ni00OWFjLWIwYjEtMzdiOWY3MzFkZDY4IiwidCI6Ijc1ZWUxZTA3LTA2OTItNGQwNS1hOTkxLWUxYjU2NjE5YmYzOCJ9"


# passer l'URL directement à components.iframe
components.iframe(
    src=url,
    width=2200,     
    height=1050,     
    scrolling=True)

