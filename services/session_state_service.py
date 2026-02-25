"""
Gestion centralisee du session_state Streamlit.
"""

from typing import MutableMapping, Any


SESSION_DEFAULTS = {
    "db_connection": None,
    "authentifie": False,
    "couturier_data": None,
    "page": "connexion",
    "db_type": None,
    "db_initialized": False,
    "db_last_error": None,
    "db_available": False,
}


def initialize_session_state(state: MutableMapping[str, Any]) -> None:
    """Initialise toutes les cles de session requises."""
    for key, default_value in SESSION_DEFAULTS.items():
        if key not in state:
            state[key] = default_value


def clear_user_session(state: MutableMapping[str, Any]) -> None:
    """
    Nettoie la session utilisateur sans casser la connexion DB.
    Le parcours UX reste identique apres deconnexion.
    """
    db_connection = state.get("db_connection")
    db_type = state.get("db_type")
    db_initialized = state.get("db_initialized", False)

    for key in list(state.keys()):
        del state[key]

    initialize_session_state(state)
    state["db_connection"] = db_connection
    state["db_type"] = db_type
    state["db_initialized"] = db_initialized
