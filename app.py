import streamlit as st

# ================= CONFIG =================
st.set_page_config(
    page_title="SpiritStitch",
    page_icon="🧵",
    layout="wide",
)

# ================= SESSION INIT =================
def init_session():
    defaults = {
        "authenticated": False,
        "user": None,
        "page": "login",
        "db": None,
        "db_connection": None,
        "db_initialized": False,
        "db_last_error": None,
        "db_available": False,
        "db_ready": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ================= IMPORTS =================
from services.database_service import ensure_db_or_fail_gracefully
from utils.permissions import est_super_admin
from utils.role_utils import est_admin

from views.auth_view import afficher_page_connexion
from views.dashboard_view import afficher_page_dashboard
from views.commande_view import afficher_page_commande
from views.liste_view import afficher_page_liste_commandes

# ================= SIDEBAR =================
def render_sidebar():
    with st.sidebar:
        user = st.session_state.user
        st.success(f"{user['prenom']} {user['nom']}")
        st.caption(f"Rôle : {user['role']}")

        def go(label, page):
            if st.button(label, use_container_width=True):
                st.session_state.page = page

        go("📊 Dashboard", "dashboard")
        go("➕ Commande", "commande")
        go("📜 Liste", "liste")

        if est_admin(user):
            go("👑 Admin", "admin")

        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ================= ROUTER =================
def router():
    page = st.session_state.page

    if page == "dashboard":
        afficher_page_dashboard()
    elif page == "commande":
        afficher_page_commande()
    elif page == "liste":
        afficher_page_liste_commandes()
    else:
        afficher_page_dashboard()

# ================= MAIN =================
def main():

    # ---------- LOGIN ----------
    if not st.session_state.authenticated:
        afficher_page_connexion()
        return

    # ---------- DB (UNE SEULE FOIS) ----------
    if not st.session_state.db_ready:
        ok, db_error = ensure_db_or_fail_gracefully(st.session_state)
        st.session_state.db_ready = ok
        st.session_state.db = st.session_state.get("db_connection")
        st.session_state.db_last_error = db_error

    if not st.session_state.db_ready:
        st.error(st.session_state.get("db_last_error") or "Base de données indisponible.")
        return

    # ---------- APP ----------
    render_sidebar()
    router()

main()