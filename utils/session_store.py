"""
Session state management for F1 Telemetry Analytics app.
Handles caching of session data, telemetry, and static assets like logos.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import base64
import os
from typing import Optional, Dict
from config import TEAM_LOGOS, LOGO_PATH


def build_session_key(year: int, event_name: str, session_type: str) -> str:
    """Build unique cache key for a session."""
    return f"{year}|{event_name}|{session_type}"


def ensure_state() -> None:
    """Initialize all required session state variables."""
    if "f1_data" not in st.session_state:
        st.session_state["f1_data"] = {}
    if "telemetry_base_cache" not in st.session_state:
        st.session_state["telemetry_base_cache"] = {}
    if "telemetry_derived_cache" not in st.session_state:
        st.session_state["telemetry_derived_cache"] = {}
    if "team_logos_cache" not in st.session_state:
        st.session_state["team_logos_cache"] = {}


def get_team_logo_b64(team_name: str, default_icon: str = "fa-car") -> str:
    """
    Get team logo as base64-encoded HTML img tag with caching.

    Args:
        team_name: Team name (e.g., "MCLAREN", "RED BULL RACING")
        default_icon: Font Awesome icon class if logo not found

    Returns:
        HTML img tag or Font Awesome icon as HTML string
    """
    ensure_state()

    # Check cache first
    cache = st.session_state.get("team_logos_cache", {})
    if team_name in cache:
        return cache[team_name]

    # Load logo from file
    file_name = TEAM_LOGOS.get(str(team_name).upper())
    if file_name:
        path = os.path.join(LOGO_PATH, file_name)
        if os.path.exists(path):
            try:
                with open(path, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode()
                    html = f'<img src="data:image/png;base64,{b64_string}" style="height: 24px; margin-right: 10px; object-fit: contain;">'

                    # Cache it
                    st.session_state["team_logos_cache"][team_name] = html
                    return html
            except Exception:
                pass

    # Fallback to Font Awesome icon
    html = f'<i class="fa-solid {default_icon}" style="font-size: 1.1rem; margin-right: 10px; color: #a1a1aa;"></i>'
    st.session_state["team_logos_cache"][team_name] = html
    return html


def store_loaded_session(session, year: int, event_name: str, session_type: str) -> None:
    """
    Store loaded F1 session data in session state.

    Args:
        session: FastF1 session object
        year: Race year
        event_name: Grand Prix name
        session_type: Session type (Practice, Qualifying, Race, etc)
    """
    ensure_state()
    session_key = build_session_key(year, event_name, session_type)
    laps = session.laps.copy()
    results = session.results.copy() if hasattr(session, "results") else None

    st.session_state["f1_session"] = session
    st.session_state["data_loaded"] = True
    st.session_state["f1_session_key"] = session_key
    st.session_state["f1_data"] = {
        "session_key": session_key,
        "year": year,
        "event_name": event_name,
        "session_type": session_type,
        "laps": laps,
        "results": results,
        "drivers_list": sorted(laps["Driver"].dropna().unique().tolist()),
        "available_stints": sorted(laps["Stint"].dropna().unique().tolist()),
    }

    # New session invalidates view-level caches.
    st.session_state["telemetry_base_cache"] = {}
    st.session_state["telemetry_derived_cache"] = {}


def get_f1_data() -> Dict:
    """Get stored F1 session data."""
    ensure_state()
    return st.session_state.get("f1_data", {})


def get_cached_laps(session) -> pd.DataFrame:
    """Get laps DataFrame with caching fallback."""
    f1_data = get_f1_data()
    cached_laps = f1_data.get("laps")
    if cached_laps is not None and not cached_laps.empty:
        return cached_laps
    return session.laps


def get_cached_results(session):
    """Get session results with caching fallback."""
    f1_data = get_f1_data()
    cached_results = f1_data.get("results")
    if cached_results is not None:
        return cached_results
    return session.results if hasattr(session, "results") else None

