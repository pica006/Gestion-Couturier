import streamlit as st
from controllers.auth_controller import AuthController
from services.database_service import ensure_db_or_fail_gracefully

def afficher_page_connexion():
    st.title("Connexion")

    with st.form("login"):
        code = st.text_input("Code")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")

    if not submit:
        return

    db_ok, db_error = ensure_db_or_fail_gracefully(st.session_state, max_retries=1)
    db_connection = st.session_state.get("db_connection")
    if not db_ok or db_connection is None:
        st.error(db_error or "Base de données indisponible.")
        return

    st.session_state.db_ready = True
    st.session_state.db = db_connection

    auth = AuthController(db_connection)
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