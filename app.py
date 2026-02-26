# app.py
"""
Application Streamlit principale - Gestion Couturier
Architecture MVC - Render SAFE
"""

import os
import streamlit as st

# =====================
# BOOTSTRAP VISUEL (ANTI ÉCRAN BLANC)
# =====================
st.set_page_config(page_title="Gestion Couturier", layout="wide")
st.write("⏳ Initialisation de l'application...")

# =====================
# ENV
# =====================
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    st.warning("⚠️ DATABASE_URL non détectée. Mode limité activé.")

# =====================
# SESSION STATE SAFE
# =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "db" not in st.session_state:
    from database import get_db
    st.session_state.db = get_db()

if "user" not in st.session_state:
    st.session_state.user = None

# =====================
# IMPORTS (APRÈS INIT)
# =====================
from views.auth_view import afficher_page_connexion
#from views.commande_view import afficher_page_commande
#from views.liste_view import afficher_liste_commandes
from components.bottom_nav import render_bottom_nav
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
from utils.role_utils import est_admin
from utils.bottom_nav import render_bottom_nav as render_nav_footer
from utils.permissions import est_super_admin
from config import APP_CONFIG, PAGE_BACKGROUND_IMAGES
# =====================
# ROUTER PRINCIPAL
# =====================
def main():

    if not st.session_state.authenticated:
        afficher_page_connexion()
        return

    # --- Pages internes
    page = st.session_state.page
    if page in ("commande", "nouvelle_commande"):
        afficher_page_commande()
    elif page in ("liste", "liste_commandes"):
        afficher_page_liste_commandes()
    elif page == "dashboard":
        afficher_page_dashboard()
    elif page == "comptabilite":
        afficher_page_comptabilite()
    elif page == "charges":
        afficher_page_mes_charges()
    elif page == "fermer_commandes":
        afficher_page_fermer_commandes()
    elif page == "calendrier":
        afficher_page_calendrier()
    elif page == "admin":
        afficher_page_administration()
    elif page == "super_admin":
        afficher_dashboard_super_admin()
    else:
        afficher_page_commande()

    # --- Navigation : boutons + footer (image / infos entreprise)
    render_bottom_nav({})
    render_nav_footer({
        "app_name": "Gestion Couturier",
        "app_subtitle": "Pilotage intelligent"
    })


# =====================
# RUN
# =====================
main()
