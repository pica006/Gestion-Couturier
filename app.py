# app3.py
"""
SpiritStitch by An's Learning - Gestion Couturier
Design maquette : sidebar bleue, formulaire connexion, footer
"""

import os
import streamlit as st

# =====================
# BOOTSTRAP VISUEL (ANTI ÉCRAN BLANC)
# =====================
st.set_page_config(page_title="SpiritStitch - Gestion Couturier", layout="wide")
init_placeholder = st.empty()
init_placeholder.write("⏳ Initialisation de l'application...")

# =====================
# ENV
# =====================
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_HOST = os.getenv("DATABASE_HOST", "").strip()

if not DATABASE_URL and not DATABASE_HOST:
    st.warning("⚠️ Aucune configuration DB cloud détectée (DATABASE_URL ou DATABASE_HOST).")

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

# =====================
# IMPORTS (APRÈS INIT)
# =====================
from views.auth_view import afficher_page_connexion
from components.bottom_nav import render_bottom_nav
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

# =====================
# STYLES CSS (statique - pas de JS, pas de ::before/::after)
# =====================
st.markdown("""
<style>
.stApp { background: #F8FAFC !important; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
[data-testid="stSidebar"] { border-right: 2px solid #E2E8F0; }
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #2C2C2C; }
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    border: 2px solid #E2E8F0 !important;
    border-radius: 10px !important;
}
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
}
.stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.stDataFrame th { background: #FAFAFA !important; color: #2C2C2C !important; font-weight: 600 !important; }
h1, h2, h3 { color: #2C2C2C; font-weight: 600; }
a { color: #2563EB !important; }
.stAlert { border-radius: 12px; }
/* Carte formulaire connexion - fond blanc */
[data-testid="stForm"] {
    background: #FFFFFF !important;
    padding: 2rem !important;
    border-radius: 16px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
}
/* Bouton Se connecter - rouge/coral comme maquette */
form button[data-baseweb="button"], form .stButton > button {
    background: #DC2626 !important;
    background-color: #DC2626 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    width: 100% !important;
}
form button[data-baseweb="button"]:hover, form .stButton > button:hover {
    background: #B91C1C !important;
    opacity: 0.95 !important;
}
/* Autres boutons - gradient violet/bleu */
.stButton > button {
    background: linear-gradient(135deg, #B19CD9 0%, #40E0D0 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 500 !important;
}
.stButton > button:hover { opacity: 0.9; }
.stTabs [data-baseweb="tab-list"] { background: #FAFAFA; padding: 0.5rem; border-radius: 12px; margin-bottom: 1rem; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #B19CD9 0%, #40E0D0 100%) !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# =====================
# ROUTER PRINCIPAL
# =====================
def main():
    init_placeholder.empty()

    if not st.session_state.authenticated:
        # --- Sidebar bleue "Mon Atelier" (page connexion uniquement)
        with st.sidebar:
            st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1E40AF 0%, #2563EB 50%, #3B82F6 100%) !important;
            }
            [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                color: #FFFFFF !important;
            }
            </style>
            <div style="color:white; padding:1.5rem 0; text-align:center;">
                <p style="font-size:2.5rem; margin:0;">🧵</p>
                <p style="font-size:2.5rem; margin:0;">📊</p>
                <h2 style="color:white !important; margin-top:2rem; font-size:1.8rem;">Mon Atelier</h2>
                <p style="color:rgba(255,255,255,0.95) !important; font-size:1rem; margin-top:0.5rem;">Espace Couture & Finance</p>
                <p style="margin-top:2rem; font-size:2rem;">🔑</p>
                <p style="margin-top:1rem; font-size:2rem;">📈</p>
            </div>
            """, unsafe_allow_html=True)

        # --- Header SpiritStitch
        st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <h1 style="color:#2563EB; font-size:2.2rem; margin-bottom:0.2rem; font-weight:700;">
                Spirit<span style="color:#60A5FA;">Stitch</span>
            </h1>
            <p style="color:#64748B; font-size:1rem;">by An's Learning</p>
        </div>
        """, unsafe_allow_html=True)

        # --- Formulaire connexion centré
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            afficher_page_connexion()

        # --- Footer (infos entreprise)
        render_nav_footer({
            "app_name": "An's Learning",
            "app_subtitle": "Système de gestion d'atelier"
        })
        return

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

    render_bottom_nav({})
    render_nav_footer({
        "app_name": "Gestion Couturier",
        "app_subtitle": "Pilotage intelligent"
    })


main()