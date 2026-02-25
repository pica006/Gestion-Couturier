"""
Service d'authentification applicative.
"""

from typing import Any, Dict, Optional, Tuple

from controllers.auth_controller import AuthController


def authenticate_user(db_connection: Any, code_couturier: str, password: str) -> Tuple[bool, Optional[Dict], str, str]:
    """
    Retourne (succes, donnees, message, page_cible).
    """
    auth_controller = AuthController(db_connection)
    succes, donnees, message = auth_controller.authentifier(code_couturier, password)

    if not succes or not donnees:
        return succes, donnees, message, "connexion"

    role_normalise = str(donnees.get("role", "")).upper().strip()
    page_cible = "super_admin_dashboard" if role_normalise == "SUPER_ADMIN" else "nouvelle_commande"
    return True, donnees, message, page_cible
