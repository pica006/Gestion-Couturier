"""
========================================
VUE D'AUTHENTIFICATION (auth_view.py)
========================================
"""

import base64
import mimetypes
import os
import streamlit as st
from controllers.auth_controller import AuthController
from config import APP_CONFIG, BRANDING
from services.database_service import ensure_db_or_fail_gracefully
from utils.bottom_nav import load_site_content

def _ensure_auth_session_keys() -> None:
    # FIX: garde-fou idempotent sans effet de bord au chargement du module.
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False
    if "db_connection" not in st.session_state:
        st.session_state.db_connection = None


# ==========================================================
# LOGO
# ==========================================================
def _resolve_logo_path():
    logo_base = APP_CONFIG.get("logo_path")
    if not logo_base:
        return None

    if os.path.isabs(logo_base) and os.path.exists(logo_base):
        return logo_base

    project_root = os.path.dirname(os.path.dirname(__file__))
    candidate = os.path.join(project_root, logo_base)

    if os.path.splitext(candidate)[1]:
        return candidate if os.path.exists(candidate) else None

    for ext in (".png", ".jpg", ".jpeg"):
        possible = f"{candidate}{ext}"
        if os.path.exists(possible):
            return possible

    return None


def _get_logo_data_uri():
    logo_path = _resolve_logo_path()
    if not logo_path:
        return None

    mime_type, _ = mimetypes.guess_type(logo_path)
    mime_type = mime_type or "image/png"

    try:
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"
    except Exception:
        return None


# ==========================================================
# CSS / STYLES (INCHANGÉS)
# ==========================================================
lux_vars_style = f"""
<style>
:root {{
--lux-primary: {BRANDING.get('primary', '#C9A227')};
--lux-secondary: {BRANDING.get('secondary', '#0E0B08')};
--lux-accent: {BRANDING.get('accent', '#F5EFE6')};
--lux-text-dark: {BRANDING.get('text_dark', '#1A140F')};
--lux-text-light: {BRANDING.get('text_light', '#F2ECE3')};
}}
</style>
"""
st.markdown(lux_vars_style, unsafe_allow_html=True)

# (CSS long inchangé – volontairement non modifié)
# ⬇️ ⬇️ ⬇️
# >>> TOUT TON CSS ORIGINAL RESTE ICI TEL QUEL <<<

# ==========================================================
# PAGE DE CONNEXION
# ==========================================================
def afficher_page_connexion():
    _ensure_auth_session_keys()
    content = load_site_content()

    # ======================================================
    # FORMULAIRE DE CONNEXION
    # ======================================================
    st.markdown('<div class="login-scope">', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.3, 1])

    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Connexion sécurisée")

        with st.form("auth_form"):
            code = st.text_input("Code Couturier", key="code_input")
            password = st.text_input("Mot de passe", type="password", key="password_input")
            submit = st.form_submit_button("Se connecter", type="primary")

            if submit:
                if not code or not password:
                    st.error("⚠️ Champs requis")
                else:
                    with st.spinner("Vérification..."):
                        # FIX: connexion DB retardée au clic login (pas au chargement de la page).
                        db_ok, db_error = ensure_db_or_fail_gracefully(st.session_state, max_retries=1)
                        if not db_ok or st.session_state.get("db_connection") is None:
                            st.error(db_error or "❌ Base de données indisponible, réessaie.")
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                            return

                        auth = AuthController(st.session_state.db_connection)
                        success, data, message = auth.authentifier(code, password)

                        if success:
                            st.session_state.authentifie = True
                            st.session_state.couturier_data = data

                            role = str(data.get("role", "")).upper().strip()
                            st.session_state.page = (
                                "super_admin_dashboard"
                                if role == "SUPER_ADMIN"
                                else "nouvelle_commande"
                            )

                            st.success(message)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(message)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)