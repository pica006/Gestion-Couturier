"""
Couche de compatibilité legacy pour les imports `from database import get_db`.
"""

from typing import Optional

import streamlit as st

from models.database import DatabaseConnection
from services.database_service import ensure_database_connection


def get_db() -> Optional[DatabaseConnection]:
    """
    Retourne une connexion DB active en réutilisant la session Streamlit.
    """
    existing = st.session_state.get("db_connection")
    if existing and existing.is_connected():
        return existing

    ok, _ = ensure_database_connection(st.session_state)
    if not ok:
        return None

    return st.session_state.get("db_connection")
