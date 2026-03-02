import fastf1
import streamlit as st
import os

# Configure cache
CACHE_DIR = os.path.join(os.getcwd(), "cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

fastf1.Cache.enable_cache(CACHE_DIR)

@st.cache_data(ttl=3600, show_spinner=False)
def load_session(year, gp, session_type):
    """
    Loads a FastF1 session with caching.
    """
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load(laps=True, telemetry=True, weather=False, messages=False)
        return session
    except Exception:
        return None

def get_available_drivers(session):
    """Returns a sorted list of driver abbreviations."""
    if session and session.laps is not None:
        return sorted(session.laps['Driver'].unique().tolist())
    return []
