"""
Light/Dark theme toggler for F1 Telemetry Analytics.
Stores theme preference in session state and localStorage proxy.
"""
from __future__ import annotations

import streamlit as st
from utils.persistence import save_to_local_storage, restore_from_local_storage
from utils.logger import log_info


DARK_THEME_CONFIG = {
    "bg_primary": "#0a0a0a",
    "bg_secondary": "#121212",
    "border": "#27272a",
    "text_primary": "#ffffff",
    "text_secondary": "#a1a1aa",
    "accent": "#21C55E",
}

LIGHT_THEME_CONFIG = {
    "bg_primary": "#ffffff",
    "bg_secondary": "#f5f5f5",
    "border": "#e0e0e0",
    "text_primary": "#1a1a1a",
    "text_secondary": "#666666",
    "accent": "#1a7c3d",
}


def init_theme() -> str:
    """
    Initialize theme from localStorage or default to dark.

    Returns:
        Current theme: "light" or "dark"
    """
    if "theme" not in st.session_state:
        # Try to restore from localStorage
        saved_theme = restore_from_local_storage("app_theme", "dark")
        st.session_state["theme"] = saved_theme
        log_info(f"Initialized theme: {saved_theme}", "init_theme")

    return st.session_state.get("theme", "dark")


def get_theme_config() -> dict:
    """Get current theme color configuration."""
    theme = st.session_state.get("theme", "dark")
    return DARK_THEME_CONFIG if theme == "dark" else LIGHT_THEME_CONFIG


def toggle_theme() -> None:
    """Toggle between light and dark theme."""
    current = st.session_state.get("theme", "dark")
    new_theme = "light" if current == "dark" else "dark"
    st.session_state["theme"] = new_theme
    save_to_local_storage("app_theme", new_theme)
    log_info(f"Theme changed to: {new_theme}", "toggle_theme")
    st.rerun()


def render_theme_toggle() -> None:
    """Render theme toggle button in sidebar."""
    theme = st.session_state.get("theme", "dark")
    icon = "☀️" if theme == "dark" else "🌙"
    label = "Light Mode" if theme == "dark" else "Dark Mode"

    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 15px 0;
        ">
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"{icon} {label}", use_container_width=True):
        toggle_theme()

    st.markdown("</div>", unsafe_allow_html=True)


def get_theme_css() -> str:
    """
    Generate CSS for current theme.

    Returns:
        CSS string with theme colors
    """
    theme = st.session_state.get("theme", "dark")
    config = get_theme_config()

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

        /* Apply theme to Streamlit components */
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

        /* Reduce jarring flash on theme change */
        * {{
            transition: background-color 0.2s ease, color 0.2s ease;
        }}
    </style>
    """
