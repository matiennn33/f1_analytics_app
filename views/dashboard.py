from __future__ import annotations

import streamlit as st
import fastf1
import pandas as pd
from typing import Optional
from modules import telemetry, strategy, race, lap_comparison
from utils.session_store import ensure_state, get_f1_data, store_loaded_session
from utils.logger import log_error, log_info, log_warning, validate_inputs
from utils.persistence import save_session_to_url, restore_session_from_url
from config import SESSION_CONFIG, ERROR_MESSAGES, F1_YEAR_RANGE


def get_events(year: int) -> list[str]:
    """Fetch F1 events for a given year with error handling."""
    try:
        schedule = fastf1.get_event_schedule(year)
        events = schedule["EventName"].tolist()
        log_info(f"Loaded {len(events)} events for {year}", "get_events")
        return events
    except Exception as e:
        log_error(e, "get_events", ERROR_MESSAGES["api_offline"])
        return ["API Offline"]


def get_event_sessions(year: int, event_name: str) -> list[str]:
    """Fetch available sessions for an event with error handling."""
    try:
        if event_name == "API Offline":
            return ["N/A"]

        schedule = fastf1.get_event_schedule(year)
        event = schedule[schedule["EventName"] == event_name].iloc[0]
        sessions = []

        for i in range(1, 6):
            session_name = event.get(f"Session{i}", None)
            if pd.notna(session_name) and session_name and str(session_name).lower() != "none":
                sessions.append(str(session_name))

        return sessions if sessions else ["Race"]
    except Exception as e:
        log_error(e, "get_event_sessions")
        # Fallback to common sessions
        if "test" in str(event_name).lower():
            return ["Session 1", "Session 2", "Session 3"]
        return ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Sprint", "Race"]


def load_f1_session(year: int, event_name: str, session_type: str) -> bool:
    """Load F1 session data with comprehensive error handling."""
    try:
        schedule = fastf1.get_event_schedule(year)
        round_num = schedule.loc[schedule["EventName"] == event_name, "RoundNumber"].values[0]

        if round_num == 0:
            # Testing session
            testing_events = schedule[schedule["RoundNumber"] == 0]
            test_idx = testing_events.index.get_loc(schedule[schedule["EventName"] == event_name].index[0])
            test_number = int(test_idx) + 1
            session = fastf1.get_testing_session(year, test_number, session_type)
        else:
            session = fastf1.get_session(year, int(round_num), session_type)

        session.load()
        store_loaded_session(session, year, event_name, session_type)

        st.toast(f"✅ Uplink Active: {event_name}")
        st.success(f"✅ Dati telemetrici caricati con successo per: {event_name}")
        log_info(f"Session loaded: {year} {event_name} {session_type}", "load_f1_session")
        return True

    except Exception as e:
        log_error(e, "load_f1_session", ERROR_MESSAGES["data_load_failed"])
        return False


def render() -> None:
    """Render the dashboard view with URL-based session persistence."""
    ensure_state()

    # Restore session from URL if available
    url_session = restore_session_from_url()
    if url_session:
        restored_year = url_session.get("year", 2024)
        restored_event = url_session.get("event_name", "")
        restored_session = url_session.get("session_type", "")
        restored_drivers = url_session.get("drivers", [])
        log_info(f"Restored from URL: {restored_year} {restored_event} {restored_session}", "dashboard.render")
    else:
        restored_year = None
        restored_event = None
        restored_session = None
        restored_drivers = []

    with st.sidebar:
        logo_col1, logo_col2, logo_col3 = st.columns([1, 5, 1])
        with logo_col2:
            st.image("logo.png")

        st.markdown("---")

        # Use restored values if available, otherwise 2024
        default_year = restored_year if restored_year else 2024
        year = st.selectbox(
            "Year",
            F1_YEAR_RANGE,
            index=list(F1_YEAR_RANGE).index(default_year) if default_year in F1_YEAR_RANGE else 0,
            key="main_sb_year",
        )

        events = get_events(year)
        default_event_idx = 0
        if restored_event and restored_event in events:
            default_event_idx = events.index(restored_event)

        event_name = st.selectbox("Grand Prix", events, index=default_event_idx, key="main_sb_event")

        sessions_list = get_event_sessions(year, event_name)
        default_session_idx = 0
        if restored_session and restored_session in sessions_list:
            default_session_idx = sessions_list.index(restored_session)

        session_type = st.selectbox("Session", sessions_list, index=default_session_idx, key="main_sb_session")

        if st.button("LOAD SESSION", key="main_btn_load", use_container_width=True):
            with st.spinner("🔄 LOADING DATA..."):
                if load_f1_session(year, event_name, session_type):
                    # Save to URL after successful load
                    save_session_to_url(year, event_name, session_type)

        st.markdown("---")

        if st.session_state.get("data_loaded"):
            f1_data = get_f1_data()
            drivers_list = f1_data.get("drivers_list", [])

            # Determine default drivers
            if restored_drivers and all(d in drivers_list for d in restored_drivers):
                default_drivers = restored_drivers
            else:
                default_drivers = drivers_list[: SESSION_CONFIG["default_drivers_to_show"]] if len(drivers_list) > 1 else drivers_list

            selected_drivers = st.multiselect(
                "Select Drivers",
                drivers_list,
                default=default_drivers,
                max_selections=SESSION_CONFIG["max_drivers_comparison"],
                key="main_sb_drivers",
            )

            if validate_inputs(selected_drivers, SESSION_CONFIG["max_drivers_comparison"]):
                st.session_state["selected_drivers"] = selected_drivers
                # Save drivers to URL
                save_session_to_url(year, event_name, session_type, selected_drivers)
            else:
                st.session_state["selected_drivers"] = []


        st.markdown("---")

        # Share Session Link
        if st.session_state.get("data_loaded") and st.session_state.get("selected_drivers"):
            with st.expander("🔗 Share Session Link", expanded=False):
                current_url = st.query_params
                share_text = f"📊 F1 Telemetry Session: {year} {event_name} {session_type}"
                st.info(f"Copy this link to share: `{share_text}`")

                if st.button("📋 Copy Current Session URL", use_container_width=True):
                    st.toast("✅ URL copied to clipboard (share this link with colleagues!)")
                    log_info(f"Shared session link: {year} {event_name}", "dashboard.render")

        st.markdown("---")

        st.markdown(
            """
        <div style="text-align: center; font-family: 'Space Grotesk', sans-serif; font-size: 0.85rem; color: #71717a; margin-top: 30px; margin-bottom: 20px;">
            Powered by <a href="https://www.linkedin.com/in/mattia-russo-3b807a305/" target="_blank" style="color: #21C55E; text-decoration: none; font-weight: 600;">Mattia Russo</a>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("<- BACK TO HOME"):
            st.session_state["current_route"] = "landing"
            st.rerun()

    # --- MAIN CONTENT ---
    if st.session_state.get("data_loaded"):
        session = st.session_state["f1_session"]
        drivers = st.session_state.get("selected_drivers", [])

        tab_tel, tab_comparison, tab_race, tab_strat = st.tabs([
            "TELEMETRY ANALYSIS",
            "LAP COMPARISON",
            "RACE HISTORY",
            "STRATEGY & TYRES",
        ])

        with tab_tel:
            telemetry.render(session, drivers)

        with tab_comparison:
            lap_comparison.render(session)

        with tab_race:
            race.render(session)

        with tab_strat:
            strategy.render(session)

    else:
        st.markdown(
            """
        <div class="f1-card" style="text-align: center; padding: 120px 20px; margin-top: 50px;">
            <i class="fa-solid fa-tower-broadcast radar-icon-animated" style="font-size: 4rem; color: #21C55E; margin-bottom: 30px;"></i>
            <h1 style="font-family: 'Geist Mono', monospace; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; font-size: 3.5rem; margin-bottom: 0px;">Systems Online</h1>
            <p style="color: #71717a; font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; max-width: 600px; margin: 20px auto;">
                Professional Telemetry Uplink Established. Select an event and session to initiate data synchronization.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
