"""
Utilitaires de logs centralisés pour production.
"""

import logging
import os


def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger avec niveau configurable via LOG_LEVEL.
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        )
    logger.setLevel(level)
    return logger
