import streamlit as st
import fastf1
import pandas as pd
from modules import telemetry, strategy, race
from utils.session_store import ensure_state, get_f1_data, store_loaded_session


def render():
    ensure_state()

    with st.sidebar:
        logo_col1, logo_col2, logo_col3 = st.columns([1, 5, 1])
        with logo_col2:
            st.image("logo.png")

        st.markdown("---")

        year = st.selectbox("Year", range(2026, 2018, -1), key="main_sb_year")

        @st.cache_data
        def get_events(y):
            try:
                schedule = fastf1.get_event_schedule(y)
                return schedule["EventName"].tolist()
            except Exception:
                return ["API Offline"]

        event_name = st.selectbox("Grand Prix", get_events(year), key="main_sb_event")

        @st.cache_data
        def get_event_sessions(y, ev_name):
            try:
                if ev_name == "API Offline":
                    return ["N/A"]
                schedule = fastf1.get_event_schedule(y)
                event = schedule[schedule["EventName"] == ev_name].iloc[0]
                sessions = []
                for i in range(1, 6):
                    s_name = event.get(f"Session{i}", None)
                    if pd.notna(s_name) and s_name and str(s_name).lower() != "none":
                        sessions.append(str(s_name))
                return sessions if sessions else ["Race"]
            except Exception:
                if "test" in str(ev_name).lower():
                    return ["Session 1", "Session 2", "Session 3"]
                return ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Sprint", "Race"]

        sessions_list = get_event_sessions(year, event_name)
        session_type = st.selectbox("Session", sessions_list, key="main_sb_session")

        if st.button("LOAD SESSION", key="main_btn_load"):
            with st.spinner("LOADING DATA..."):
                try:
                    schedule = fastf1.get_event_schedule(year)
                    round_num = schedule.loc[schedule["EventName"] == event_name, "RoundNumber"].values[0]

                    if round_num == 0:
                        testing_events = schedule[schedule["RoundNumber"] == 0]
                        test_idx = testing_events.index.get_loc(schedule[schedule["EventName"] == event_name].index[0])
                        test_number = int(test_idx) + 1
                        session = fastf1.get_testing_session(year, test_number, session_type)
                    else:
                        session = fastf1.get_session(year, int(round_num), session_type)

                    session.load()
                    store_loaded_session(session, year, event_name, session_type)

                    st.toast(f"Uplink Active: {event_name}")
                    st.success(f"Dati telemetrici caricati con successo per: {event_name}")
                except Exception as e:
                    st.error(f"Sincronizzazione fallita. Verifica la connessione. Dettagli: {e}")

        st.markdown("---")

        if st.session_state.get("data_loaded"):
            f1_data = get_f1_data()
            drivers_list = f1_data.get("drivers_list", [])
            selected_drivers = st.multiselect(
                "Select Drivers",
                drivers_list,
                default=drivers_list[:2] if len(drivers_list) > 1 else drivers_list,
                key="main_sb_drivers",
            )
            st.session_state["selected_drivers"] = selected_drivers

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

        tab_tel, tab_race, tab_strat = st.tabs([
            "TELEMETRY ANALYSIS",
            "RACE HISTORY",
            "STRATEGY & TYRES",
        ])

        with tab_tel:
            telemetry.render(session, drivers)

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
