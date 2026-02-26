import streamlit as st
from controllers.auth_controller import AuthController

def afficher_page_connexion():
    st.title("Connexion")

    with st.form("login"):
        code = st.text_input("Code")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")

    if not submit:
        return

    auth = AuthController(st.session_state.db)
    ok, data, msg = auth.authentifier(code, password)

    if not ok:
        st.error(msg)
        return

    st.session_state.authenticated = True
    st.session_state.user = {
        "id": data["id"],
        "prenom": data["prenom"],
        "nom": data["nom"],
        "role": data["role"],
    }
    st.session_state.page = "dashboard"
    st.rerun()