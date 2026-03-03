"""
Centralized logging system for F1 Telemetry Analytics
"""

import streamlit as st
import logging
from datetime import datetime
from typing import Optional
from config import ERROR_MESSAGES, COLORS

# Configure Python logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('app_logs.txt'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log_error(error: Exception, context: str = "", user_message: Optional[str] = None) -> None:
    """
    Log an error with context and optionally show user-friendly message.

    Args:
        error: The exception to log
        context: Context describing where the error occurred
        user_message: User-friendly message to display. If None, uses generic message.
    """
    logger.error(f"[{context}] {type(error).__name__}: {str(error)}", exc_info=True)

    if user_message is None:
        user_message = ERROR_MESSAGES.get("data_load_failed", "❌ Errore durante l'operazione.")

    st.error(user_message)


def log_info(message: str, context: str = "") -> None:
    """Log informational message."""
    if context:
        logger.info(f"[{context}] {message}")
    else:
        logger.info(message)


def log_warning(message: str, context: str = "") -> None:
    """Log warning message and notify user."""
    if context:
        logger.warning(f"[{context}] {message}")
    else:
        logger.warning(message)
    st.warning(f"⚠️ {message}")


def show_error_card(title: str, message: str, error_details: Optional[str] = None) -> None:
    """
    Show a styled error card to user.

    Args:
        title: Error title
        message: User-friendly error message
        error_details: Optional technical details (only shown in logs)
    """
    st.error(f"**{title}**\n\n{message}")
    if error_details:
        logger.error(f"Technical details: {error_details}")


def show_loading_status(message: str, progress: float = 0.0) -> None:
    """
    Show loading status with optional progress indication.

    Args:
        message: Status message
        progress: Progress percentage (0-1)
    """
    if progress > 0:
        st.progress(progress, text=message)
    else:
        with st.spinner(message):
            pass


def validate_inputs(drivers: list, max_allowed: int = 4) -> bool:
    """
    Validate user input selections.

    Args:
        drivers: List of selected drivers
        max_allowed: Maximum allowed drivers

    Returns:
        True if valid, False otherwise
    """
    if not drivers or len(drivers) == 0:
        log_warning("Nessun pilota selezionato", "validation")
        st.warning(ERROR_MESSAGES["invalid_drivers"])
        return False

    if len(drivers) > max_allowed:
        log_warning(f"Troppi piloti selezionati: {len(drivers)} > {max_allowed}", "validation")
        st.warning(f"❌ Massimo {max_allowed} piloti. Hai selezionato {len(drivers)}.")
        return False

    return True
