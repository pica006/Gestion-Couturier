"""
Point d'entree Streamlit minimal.
- Initialisation session_state
- Connexion DB via service
- Routing des vues
"""

from dotenv import load_dotenv
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


load_dotenv()

st.set_page_config(
    page_title="Gestion Couturier",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_main_css(), unsafe_allow_html=True)


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
            if st.button("📊 Dashboard Super Admin", width="stretch"):
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
            if st.button(label, width="stretch"):
                st.session_state.page = page_id
                st.rerun()

        if est_admin(st.session_state.get("couturier_data")) and not est_super_admin():
            st.markdown("---")
            if st.button("👑 Administration", width="stretch"):
                st.session_state.page = "administration"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Deconnexion", width="stretch"):
            clear_user_session(st.session_state)
            st.session_state.authentifie = False
            st.session_state.couturier_data = None
            st.session_state.page = "connexion"
            st.rerun()


def _route_authenticated_page() -> None:
    page = st.session_state.get("page", "dashboard")

    if page == "super_admin_dashboard":
        if est_super_admin():
            afficher_dashboard_super_admin()
        else:
            st.error("❌ Acces refuse. Cette page est reservee au Super Administrateur.")
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
            st.error("❌ Acces refuse. Cette page est reservee aux administrateurs.")
            st.session_state.page = "dashboard"
            st.rerun()
    else:
        afficher_page_dashboard()


def _invalidate_user_and_redirect_to_login(message: str) -> None:
    """
    Coupe proprement la session utilisateur si la DB est indisponible.
    """
    st.warning(f"⚠️ {message}")
    clear_user_session(st.session_state)
    st.session_state.authentifie = False
    st.session_state.couturier_data = None
    st.session_state.page = "connexion"
    st.session_state.db_connection = None
    st.session_state.db_initialized = False
    st.session_state.db_available = False
    st.rerun()


def main() -> None:
    initialize_session_state(st.session_state)

    sidebar_bg = _load_sidebar_bg_image()

    if not st.session_state.get("authentifie", False):
        st.markdown(get_sidebar_styles_css(sidebar_bg), unsafe_allow_html=True)
        _render_sidebar()
        afficher_page_connexion()
        return

    db_ready, db_message = ensure_db_or_fail_gracefully(st.session_state, max_retries=2)
    if not db_ready:
        logger.error("DB indisponible en session authentifiée: %s", db_message)
        _invalidate_user_and_redirect_to_login(
            "Connexion base perdue. Merci de vous reconnecter dans quelques secondes."
        )
        return

    st.markdown(get_sidebar_styles_css(SIDEBAR_BG_PLAIN), unsafe_allow_html=True)
    _render_sidebar()

    page_bg_html = get_page_background_html(
        st.session_state.get("page", "dashboard"),
        PAGE_BACKGROUND_IMAGES,
    )
    if page_bg_html:
        st.markdown(page_bg_html, unsafe_allow_html=True)
    try:
        _route_authenticated_page()
    except Exception:
        logger.exception("Erreur non capturée pendant le routing/authenticated view")
        db_ready, db_message = ensure_db_or_fail_gracefully(st.session_state, max_retries=1)
        if not db_ready:
            _invalidate_user_and_redirect_to_login(
                "La base est indisponible. Session réinitialisée pour éviter un écran bloqué."
            )
            return
        st.error("❌ Une erreur temporaire est survenue. Réessayez.")

    render_bottom_nav(
        {
            "app_name": APP_CONFIG.get("name", ""),
            "app_subtitle": APP_CONFIG.get("subtitle", ""),
        }
    )


if __name__ == "__main__":
    main()
