"""
Point d'entree Streamlit minimal.
- Initialisation session_state (IDEMPOTENTE)
- Connexion DB via service (1 tentative / session)
- Routing des vues
"""

import streamlit as st

from services.session_state_service import initialize_session_state, clear_user_session
from services.database_service import ensure_db_or_fail_gracefully
from utils.permissions import est_super_admin
from utils.role_utils import est_admin
from utils.bottom_nav import render_bottom_nav
from utils.logging_utils import get_logger
from utils.app_styles import (
    SIDEBAR_BG_PLAIN,
    _load_sidebar_bg_image,
    get_main_css,
    get_sidebar_styles_css,
    get_page_background_html,
)
from config import APP_CONFIG, PAGE_BACKGROUND_IMAGES

from views.auth_view import afficher_page_connexion
from views.commande_view import afficher_page_commande
from views.liste_view import afficher_page_liste_commandes
from views.comptabilite_view import afficher_page_comptabilite
from views.dashboard_view import afficher_page_dashboard
from views.mes_charges_view import afficher_page_mes_charges
from views.admin_view import afficher_page_administration
from views.fermer_commandes_view import afficher_page_fermer_commandes
from views.calendrier_view import afficher_page_calendrier
from views.super_admin_dashboard import afficher_dashboard_super_admin


logger = get_logger(__name__)
try:
    # FIX: dotenv reste optionnel en cloud; l'app démarre même sans python-dotenv.
    dotenv_module = __import__("dotenv")
    load_dotenv = getattr(dotenv_module, "load_dotenv", None)
    if callable(load_dotenv):
        load_dotenv()
except Exception:
    pass

st.set_page_config(
    page_title="Gestion Couturier",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_main_css(), unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
def _render_sidebar() -> None:
    with st.sidebar:
        if not st.session_state.get("authentifie", False):
            st.markdown("<div style='height: 100vh;'></div>", unsafe_allow_html=True)
            return

        user = st.session_state.get("couturier_data") or {}
        st.success(f"**Connecte:** {user.get('prenom', '')} {user.get('nom', '')}".strip())
        st.info(
            f"**Code:** {user.get('code_couturier', 'N/A')} | "
            f"**Role:** {user.get('role', 'employe')}"
        )
        st.markdown("---")

        if est_super_admin():
            st.markdown("### 🔧 SUPER ADMINISTRATION")
            if st.button("📊 Dashboard Super Admin", use_container_width=True):
                st.session_state.page = "super_admin_dashboard"
                st.rerun()
            st.markdown("---")

        st.markdown("### 📋 Navigation")
        routes = [
            ("📊 Tableau de bord", "dashboard"),
            ("➕ Nouvelle commande", "nouvelle_commande"),
            ("📜 Mes commandes", "liste_commandes"),
            ("💰 Comptabilité", "comptabilite"),
            ("📄 Mes charges", "charges"),
            ("🔒 Fermer mes commandes", "fermer_commandes"),
            ("📋 Modèles & Calendrier", "calendrier"),
        ]

        for label, page_id in routes:
            if st.button(label, use_container_width=True):
                st.session_state.page = page_id
                st.rerun()

        if est_admin(st.session_state.get("couturier_data")) and not est_super_admin():
            st.markdown("---")
            if st.button("👑 Administration", use_container_width=True):
                st.session_state.page = "administration"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Deconnexion", use_container_width=True):
            clear_user_session(st.session_state)
            st.session_state.authentifie = False
            st.session_state.page = "connexion"
            st.rerun()


# ---------------- ROUTING ----------------
def _route_authenticated_page() -> None:
    page = st.session_state.get("page", "dashboard")

    if page == "super_admin_dashboard":
        if est_super_admin():
            afficher_dashboard_super_admin()
        else:
            st.error("❌ Acces refuse.")
            st.session_state.page = "dashboard"
            st.rerun()

    elif page == "nouvelle_commande":
        afficher_page_commande()
    elif page == "liste_commandes":
        afficher_page_liste_commandes()
    elif page == "comptabilite":
        afficher_page_comptabilite()
    elif page == "charges":
        afficher_page_mes_charges()
    elif page == "fermer_commandes":
        afficher_page_fermer_commandes()
    elif page == "calendrier":
        afficher_page_calendrier(onglet_admin=False)
    elif page == "administration":
        if est_admin(st.session_state.get("couturier_data")):
            afficher_page_administration()
        else:
            st.error("❌ Acces refuse.")
            st.session_state.page = "dashboard"
            st.rerun()
    else:
        afficher_page_dashboard()


# ---------------- MAIN ----------------
def main() -> None:
    # ✅ Initialisation SAFE (ne reset jamais)
    if not st.session_state.get("_initialized", False):
        initialize_session_state(st.session_state)
        st.session_state._initialized = True

    sidebar_bg = _load_sidebar_bg_image()

    # ---------- LOGIN ----------
    if not st.session_state.get("authentifie", False):
        st.markdown(get_sidebar_styles_css(sidebar_bg), unsafe_allow_html=True)
        _render_sidebar()
        afficher_page_connexion()
        return  # ❌ aucun rerun ici

    # ---------- DB (1 tentative par session) ----------
    if not st.session_state.get("db_initialized", False):
        db_ready, _ = ensure_db_or_fail_gracefully(st.session_state, max_retries=1)
        st.session_state.db_initialized = True
        st.session_state.db_available = db_ready

    if not st.session_state.get("db_available", False):
        st.error("⚠️ Base de données indisponible. Rechargez la page.")
        return

    # ---------- APP ----------
    st.markdown(get_sidebar_styles_css(SIDEBAR_BG_PLAIN), unsafe_allow_html=True)
    _render_sidebar()

    page_bg_html = get_page_background_html(
        st.session_state.get("page", "dashboard"),
        PAGE_BACKGROUND_IMAGES,
    )
    if page_bg_html:
        st.markdown(page_bg_html, unsafe_allow_html=True)

    _route_authenticated_page()

    render_bottom_nav(
        {
            "app_name": APP_CONFIG.get("name", ""),
            "app_subtitle": APP_CONFIG.get("subtitle", ""),
        }
    )


if __name__ == "__main__":
    main()