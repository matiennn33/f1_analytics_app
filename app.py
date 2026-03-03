from __future__ import annotations

import streamlit as st
import socket
import os
import fastf1
from utils.styles import inject_global_css
from utils.mobile import get_mobile_responsive_css
from utils.theme import init_theme, get_theme_css
from views import landing, dashboard, architecture, help as help_page

socket.setdefaulttimeout(30)
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

st.set_page_config(
    page_title="LC - TELEMETRY",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "current_route" not in st.session_state:
    st.session_state["current_route"] = "landing"

# Initialize theme system
init_theme()

inject_global_css()

# Inject mobile-responsive CSS
st.markdown(get_mobile_responsive_css(), unsafe_allow_html=True)

# Inject theme-based CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Nascondi la sidebar se non siamo nella dashboard
if st.session_state["current_route"] != "dashboard":
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
        </style>
    """,
        unsafe_allow_html=True,
    )

# Router
if st.session_state["current_route"] == "landing":
    landing.render()
elif st.session_state["current_route"] == "dashboard":
    dashboard.render()
elif st.session_state["current_route"] == "help":
    help_page.render()
elif st.session_state["current_route"] == "architecture":
    architecture.render()
