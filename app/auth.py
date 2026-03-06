from click import option
import streamlit as st
import pandas as pd
import bcrypt
import os


USER_FILE = "users.csv"


# --------------------------------------
# Initialisation du fichier users.csv
# --------------------------------------
def init_user_file():
    if not os.path.exists(USER_FILE):
        df = pd.DataFrame(columns=["username", "password", "email"])
        df.to_csv(USER_FILE, index=False)


def load_users():
    if not os.path.exists(USER_FILE):
        init_user_file()
    return pd.read_csv(USER_FILE)


# --------------------------------------
# Connexion
# --------------------------------------
def login_user(username, password):
    df_users = load_users()
    if username not in df_users["username"].values:
        st.error("Utilisateur introuvable.")
        return False


    stored_pw = df_users.loc[df_users["username"] == username, "password"].values[0]


    if bcrypt.checkpw(password.encode(), stored_pw.encode()):
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = "user"
        st.success(f"Bienvenue {username} !")
        return True
    else:
        st.error("Mot de passe incorrect.")
        return False


# --------------------------------------
# Inscription
# --------------------------------------
def register_user(username, password, email=""):
    df_users = load_users()
    if username in df_users["username"].values:
        st.error("Nom d'utilisateur déjà utilisé.")
        return False


    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = pd.DataFrame(
        {"username": [username], "password": [hashed_pw], "email": [email]}
    )
    df_users = pd.concat([df_users, new_user], ignore_index=True)
    df_users.to_csv(USER_FILE, index=False)


    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["role"] = "user"
    st.success("Inscription réussie !")
    return True

#--------------------------------------
#Connexion invité
#--------------------------------------
def login_guest():
    st.session_state["logged_in"] = True
    st.session_state["username"] = "Invité"
    st.session_state["role"] = "guest"

# --------------------------------------
# Déconnexion
# --------------------------------------
def logout():
    for key in ["logged_in", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# --------------------------------------
# Formulaire centralisé login / inscription
# --------------------------------------
def login_form():
    option = st.radio("", ["Se connecter", "S'inscrire"], label_visibility="collapsed")

    # ==================================================
    # CONNEXION
    # ==================================================
    if option == "Se connecter":

        username = st.text_input("Nom d'utilisateur", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Connexion", key="login_link"):
                if login_user(username, password):
                    st.rerun()

        with col2:
            if st.button("Invité", key="guest_link"):
                login_guest()
                st.rerun()

    # ==================================================
    # INSCRIPTION
    # ==================================================
    elif option == "S'inscrire":

        new_user = st.text_input("Nom d'utilisateur", key="reg_user")
        email = st.text_input("Adresse e-mail", key="reg_email")
        new_password = st.text_input("Mot de passe", type="password", key="reg_pass")
        confirm_password = st.text_input(
            "Confirmer le mot de passe", type="password", key="reg_pass_confirm"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Créer le compte", key="reg_btn"):
            if new_password != confirm_password:
                st.error("Les mots de passe ne correspondent pas !")
            elif not email or "@" not in email:
                st.error("Adresse e-mail invalide !")
            elif register_user(new_user, new_password, email=email):
                st.rerun()