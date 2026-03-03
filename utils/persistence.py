"""
Session persistence utilities - Save/restore state to URL and localStorage.
Allows users to share session links and maintains state across page refreshes.
"""
from __future__ import annotations

import streamlit as st
from urllib.parse import urlencode, parse_qs
from typing import Optional, Dict, Any
from utils.logger import log_info


def get_url_params() -> Dict[str, str]:
    """Extract query parameters from URL."""
    params = st.query_params
    return {key: value[0] if isinstance(value, list) and len(value) > 0 else value
            for key, value in params.items()}


def build_session_url(year: int, event_name: str, session_type: str, drivers: list[str] = None) -> str:
    """
    Build shareable URL with session parameters.

    Args:
        year: F1 season year
        event_name: Grand Prix name
        session_type: Session type (Practice, Qualifying, Race, etc)
        drivers: List of selected driver abbreviations

    Returns:
        Query string for URL
    """
    params: Dict[str, Any] = {
        "year": year,
        "event": event_name,
        "session": session_type,
    }

    if drivers:
        params["drivers"] = ",".join(drivers)

    log_info(f"Generated session URL params: {params}", "build_session_url")
    return urlencode(params)


def save_session_to_url(year: int, event_name: str, session_type: str, drivers: list[str] = None) -> None:
    """
    Save current session to URL query parameters.

    Args:
        year: F1 season year
        event_name: Grand Prix name
        session_type: Session type
        drivers: List of selected drivers
    """
    params: Dict[str, Any] = {
        "year": str(year),
        "event": event_name,
        "session": session_type,
    }

    if drivers and len(drivers) > 0:
        params["drivers"] = ",".join(drivers)

    st.query_params.update(params)
    log_info(f"Session saved to URL: {params}", "save_session_to_url")


def restore_session_from_url() -> Optional[Dict[str, Any]]:
    """
    Restore session parameters from URL query string.

    Returns:
        Dictionary with year, event_name, session_type, drivers if URL params exist, None otherwise
    """
    params = get_url_params()

    if not params or "year" not in params:
        return None

    try:
        session_data: Dict[str, Any] = {
            "year": int(params.get("year", 2024)),
            "event_name": params.get("event", ""),
            "session_type": params.get("session", ""),
            "drivers": params.get("drivers", "").split(",") if params.get("drivers") else [],
        }

        # Clean up empty driver strings
        session_data["drivers"] = [d.strip() for d in session_data["drivers"] if d.strip()]

        log_info(f"Restored session from URL: {session_data}", "restore_session_from_url")
        return session_data
    except Exception as e:
        log_info(f"Failed to restore session from URL: {e}", "restore_session_from_url")
        return None


def save_to_local_storage(key: str, value: Any) -> None:
    """
    Save data to browser localStorage via session_state.
    Uses Streamlit's session_state as a proxy to client-side storage.

    Args:
        key: Storage key
        value: Value to store
    """
    if "local_storage" not in st.session_state:
        st.session_state["local_storage"] = {}

    st.session_state["local_storage"][key] = value
    log_info(f"Saved to localStorage: {key}", "save_to_local_storage")


def restore_from_local_storage(key: str, default: Any = None) -> Any:
    """
    Restore data from localStorage proxy in session_state.

    Args:
        key: Storage key
        default: Default value if key not found

    Returns:
        Stored value or default
    """
    if "local_storage" not in st.session_state:
        st.session_state["local_storage"] = {}

    value = st.session_state["local_storage"].get(key, default)
    if value is not None and value != default:
        log_info(f"Restored from localStorage: {key}", "restore_from_local_storage")

    return value


def clear_session_params() -> None:
    """Clear all session-related URL parameters."""
    # Clear query params
    st.query_params.clear()
    log_info("Cleared all session URL parameters", "clear_session_params")


def create_shareable_link(base_url: str, year: int, event_name: str, session_type: str, drivers: list[str] = None) -> str:
    """
    Generate a fully shareable link with session parameters.

    Args:
        base_url: Application base URL (e.g., "https://f1-telemetry.streamlit.app")
        year: F1 season year
        event_name: Grand Prix name
        session_type: Session type
        drivers: List of selected drivers

    Returns:
        Full shareable URL
    """
    query_string = build_session_url(year, event_name, session_type, drivers)
    url = f"{base_url}?{query_string}"
    log_info(f"Generated shareable link: {url}", "create_shareable_link")
    return url
