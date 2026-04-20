import logging

from app.utils.config import settings


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Production code can extend this with structured logging, trace IDs, and
    tenant or team metadata.
    """
    logging.basicConfig(level=settings.log_level)
    return logging.getLogger(name)
