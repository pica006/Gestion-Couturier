"""
Services de connexion et bootstrap base de donnees.
"""

from typing import MutableMapping, Any, Tuple

from config import DATABASE_CONFIG, IS_RENDER
from controllers.auth_controller import AuthController
from controllers.commande_controller import CommandeController
from models.database import DatabaseConnection, ChargesModel
from utils.logging_utils import get_logger


logger = get_logger(__name__)


def _probe_connection(db_connection: DatabaseConnection) -> bool:
    """
    Vérifie qu'une connexion active répond réellement côté serveur.
    """
    try:
        if not db_connection or not db_connection.is_connected():
            return False
        conn = db_connection.get_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return True
    except Exception:
        logger.warning("Probe DB échouée (connexion potentiellement expirée).")
        return False


def _resolve_db_target() -> str:
    return "render_production" if IS_RENDER else "postgresql_local"


def _resolve_db_config() -> dict:
    return DATABASE_CONFIG.get(_resolve_db_target(), {})


def _validate_config(config: dict) -> Tuple[bool, str]:
    required_keys = ["host", "database", "user"]
    missing = [k for k in required_keys if not config.get(k)]
    if missing:
        logger.error("Configuration DB incomplète, clés manquantes: %s", ", ".join(missing))
        return False, "Configuration base de données incomplète."
    return True, ""


def _bootstrap_schema(db_connection: DatabaseConnection) -> Tuple[bool, str]:
    """
    Initialise les tables applicatives sans logique UI.
    """
    try:
        auth_controller = AuthController(db_connection)
        if not auth_controller.initialiser_tables():
            return False, "Initialisation table couturiers impossible."

        commande_controller = CommandeController(db_connection)
        if not commande_controller.initialiser_tables():
            return False, "Initialisation tables clients/commandes impossible."

        charges_model = ChargesModel(db_connection)
        if not charges_model.creer_tables():
            return False, "Initialisation tables charges impossible."

        return True, ""
    except Exception:
        logger.exception("Erreur pendant le bootstrap du schéma DB")
        return False, "Erreur d'initialisation du schéma de base de données."


def ensure_database_connection(state: MutableMapping[str, Any]) -> Tuple[bool, str]:
    """
    Etablit la connexion DB si necessaire et initialise le schema une seule fois.
    """
    db_connection = state.get("db_connection")
    if db_connection and db_connection.is_connected():
        if state.get("db_initialized"):
            state["db_available"] = True
            return True, ""
        ok, message = _bootstrap_schema(db_connection)
        state["db_initialized"] = ok
        state["db_last_error"] = None if ok else message
        state["db_available"] = ok
        return ok, message

    config = _resolve_db_config()
    valid, message = _validate_config(config)
    if not valid:
        state["db_last_error"] = message
        state["db_available"] = False
        return False, message

    connection = DatabaseConnection("postgresql", config)
    if not connection.connect():
        logger.error("Connexion DB échouée pour la cible '%s'.", _resolve_db_target())
        error_msg = (
            "Connexion a la base impossible. Verifiez les variables d'environnement "
            "Render ou la configuration locale."
        )
        state["db_last_error"] = error_msg
        state["db_available"] = False
        return False, error_msg

    state["db_connection"] = connection
    state["db_type"] = _resolve_db_target()

    ok, bootstrap_error = _bootstrap_schema(connection)
    state["db_initialized"] = ok
    state["db_last_error"] = None if ok else bootstrap_error
    state["db_available"] = ok

    if not ok:
        try:
            connection.disconnect()
        except Exception:
            pass
        state["db_connection"] = None
        state["db_available"] = False
        return False, bootstrap_error

    return True, ""


def ensure_db_or_fail_gracefully(state: MutableMapping[str, Any], max_retries: int = 2) -> Tuple[bool, str]:
    """
    Guard central de résilience DB :
    - probe connexion courante,
    - reconnexion légère (max_retries),
    - renvoie un état contrôlé sans exception.
    """
    db_connection = state.get("db_connection")
    if db_connection and _probe_connection(db_connection):
        state["db_available"] = True
        state["db_last_error"] = None
        return True, ""

    last_error = "Base de données temporairement indisponible."
    state["db_available"] = False

    for attempt in range(1, max_retries + 1):
        try:
            current = state.get("db_connection")
            if current:
                current.disconnect()
        except Exception:
            logger.warning("Échec fermeture connexion DB pendant retry %s.", attempt)

        state["db_connection"] = None
        state["db_initialized"] = False

        ok, message = ensure_database_connection(state)
        if ok:
            refreshed = state.get("db_connection")
            if refreshed and _probe_connection(refreshed):
                state["db_available"] = True
                state["db_last_error"] = None
                logger.info("Reconnexion DB réussie (tentative %s).", attempt)
                return True, ""
            last_error = "Connexion base instable après reconnexion."
            state["db_available"] = False
            state["db_last_error"] = last_error
        else:
            last_error = message or last_error
            state["db_last_error"] = last_error
            logger.warning("Retry DB %s/%s échoué: %s", attempt, max_retries, last_error)

    return False, last_error
