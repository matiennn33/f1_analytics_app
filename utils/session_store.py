import streamlit as st


def build_session_key(year, event_name, session_type):
    return f"{year}|{event_name}|{session_type}"


def ensure_state():
    if "f1_data" not in st.session_state:
        st.session_state["f1_data"] = {}
    if "telemetry_base_cache" not in st.session_state:
        st.session_state["telemetry_base_cache"] = {}
    if "telemetry_derived_cache" not in st.session_state:
        st.session_state["telemetry_derived_cache"] = {}


def store_loaded_session(session, year, event_name, session_type):
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


def get_f1_data():
    ensure_state()
    return st.session_state.get("f1_data", {})


def get_cached_laps(session):
    f1_data = get_f1_data()
    cached_laps = f1_data.get("laps")
    if cached_laps is not None and not cached_laps.empty:
        return cached_laps
    return session.laps


def get_cached_results(session):
    f1_data = get_f1_data()
    cached_results = f1_data.get("results")
    if cached_results is not None:
        return cached_results
    return session.results if hasattr(session, "results") else None
