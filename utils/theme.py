"""
Dark theme system for F1 Telemetry Analytics.
Single dark theme optimized for professional use and visual fatigue reduction.
"""
from __future__ import annotations

import streamlit as st
from utils.logger import log_info


DARK_THEME_CONFIG = {
    "bg_primary": "#0a0a0a",
    "bg_secondary": "#121212",
    "border": "#27272a",
    "text_primary": "#ffffff",
    "text_secondary": "#a1a1aa",
    "accent": "#21C55E",
}


def init_theme() -> str:
    """
    Initialize dark theme (no light mode option).

    Returns:
        Always returns "dark"
    """
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
        log_info("Dark theme initialized", "init_theme")

    return "dark"


def get_theme_config() -> dict:
    """Get current theme color configuration (always dark)."""
    return DARK_THEME_CONFIG


def get_theme_css() -> str:
    """
    Generate CSS for dark theme.

    Returns:
        CSS string with dark theme colors
    """
    config = DARK_THEME_CONFIG

    return f"""
    <style>
        :root {{
            --primary-bg: {config['bg_primary']};
            --secondary-bg: {config['bg_secondary']};
            --border: {config['border']};
            --text-primary: {config['text_primary']};
            --text-secondary: {config['text_secondary']};
            --accent: {config['accent']};
        }}

        /* Apply dark theme to Streamlit components */
        .stApp {{
            background-color: {config['bg_primary']};
            color: {config['text_primary']};
        }}

        [data-testid="stAppViewContainer"] {{
            background-color: {config['bg_primary']};
        }}

        [data-testid="stSidebar"] {{
            background-color: {config['bg_secondary']};
            border-right: 1px solid {config['border']};
        }}

        .stButton > button {{
            border-color: {config['border']};
            color: {config['text_primary']};
            background-color: {config['bg_secondary']};
        }}

        .stButton > button:hover {{
            background-color: {config['accent']};
            color: {config['bg_primary']};
        }}

        .stSelectbox {{
            background-color: {config['bg_secondary']};
            color: {config['text_primary']};
        }}

        .stMultiSelect {{
            background-color: {config['bg_secondary']};
            color: {config['text_primary']};
        }}

        .stMetricLabel {{
            color: {config['text_secondary']};
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {config['text_primary']};
        }}

        p, span, label {{
            color: {config['text_primary']};
        }}

        /* Card styling */
        .f1-card {{
            background-color: {config['bg_secondary']};
            border-color: {config['border']};
            color: {config['text_primary']};
        }}

        /* Info/Alert boxes */
        [role="alert"] {{
            background-color: {config['bg_secondary']};
            border-color: {config['border']};
            color: {config['text_primary']};
        }}

        /* Smooth transitions */
        * {{
            transition: background-color 0.2s ease, color 0.2s ease;
        }}
    </style>
    """

