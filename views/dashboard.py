import streamlit as st
import fastf1
import pandas as pd
from modules import telemetry, strategy, race
from modules import multi_session
from utils.session_store import (
    ensure_state, get_f1_data, store_loaded_session,
    get_favorite_drivers, toggle_favorite_driver, is_favorite_driver,
)


def render():
    ensure_state()

    with st.sidebar:
        # ── Logo ───────────────────────────────────────────────
        logo_col1, logo_col2, logo_col3 = st.columns([1, 5, 1])
        with logo_col2:
            st.image("logo.png")

        # ── Session Configuration ─────────────────────────────────
        st.markdown(
            "<div class='sb-section-label'>"
            "<i class='fa-solid fa-satellite-dish'></i>SESSION CONFIGURATION</div>",
            unsafe_allow_html=True,
        )

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

        if st.button("LOAD SESSION", key="main_btn_load", use_container_width=True):
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
                    st.success(f"Loaded: {event_name}")
                except Exception as e:
                    st.error(f"Load failed: {e}")

        # ── No-session hint (Recognition vs Recall) ─────────────────
        if not st.session_state.get("data_loaded"):
            st.markdown(
                "<div style='margin-top:8px;padding:10px 14px;border-radius:8px;"
                "background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);"
                "font-family:var(--font-mono);font-size:0.62rem;color:var(--text-d);"
                "letter-spacing:0.8px;line-height:1.6;'>"
                "<i class='fa-solid fa-circle-info' style='color:var(--accent);margin-right:7px;opacity:0.7;'></i>"
                "Select a year, race &amp; session, then load."
                "</div>",
                unsafe_allow_html=True,
            )

        # ── Driver Selection ─────────────────────────────────────────
        if st.session_state.get("data_loaded"):
            f1_data = get_f1_data()
            drivers_list = f1_data.get("drivers_list", [])

            st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='sb-section-label'>"
                "<i class='fa-solid fa-user-astronaut'></i>DRIVERS</div>",
                unsafe_allow_html=True,
            )

            favs = get_favorite_drivers()
            fav_available = [d for d in favs if d in drivers_list] if favs else []
            if fav_available:
                st.markdown(
                    "<div class='sb-meta-label'>"
                    "<i class='fa-solid fa-star'></i>QUICK SELECT</div>",
                    unsafe_allow_html=True,
                )
                fav_cols = st.columns(min(len(fav_available), 4))
                for fi, fdrv in enumerate(fav_available):
                    with fav_cols[fi % 4]:
                        if st.button(fdrv, key=f"fav_quick_{fdrv}",
                                     use_container_width=True, help=fdrv):
                            cur = st.session_state.get("main_sb_drivers", [])
                            if fdrv not in cur:
                                st.session_state["main_sb_drivers"] = cur + [fdrv]
                                st.rerun()

            selected_drivers = st.multiselect(
                "Select Drivers",
                drivers_list,
                default=drivers_list[:2] if len(drivers_list) > 1 else drivers_list,
                key="main_sb_drivers",
            )
            st.session_state["selected_drivers"] = selected_drivers

            if drivers_list:
                with st.expander("MANAGE FAVOURITE DRIVERS", expanded=False):
                    st.markdown(
                        "<div class='sb-meta-label' style='margin-bottom:10px;'>CLICK TO ADD / REMOVE</div>",
                        unsafe_allow_html=True,
                    )
                    fav_grid_cols = st.columns(3)
                    for gi, drv_code in enumerate(sorted(drivers_list)):
                        is_fav = is_favorite_driver(drv_code)
                        star = "★" if is_fav else "☆"
                        with fav_grid_cols[gi % 3]:
                            if st.button(
                                f"{star} {drv_code}",
                                key=f"fav_toggle_{drv_code}",
                                use_container_width=True,
                                help="Remove" if is_fav else "Add to favourites",
                            ):
                                toggle_favorite_driver(drv_code)
                                st.rerun()

        # ── Export ───────────────────────────────────────────────
        if st.session_state.get("data_loaded"):
            f1_data_exp = get_f1_data()
            ev_name_exp = f1_data_exp.get("event_name", "session")
            sess_type_exp = f1_data_exp.get("session_type", "")
            laps_exp = f1_data_exp.get("laps")

            st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='sb-section-label'>"
                "<i class='fa-solid fa-download'></i>EXPORT</div>",
                unsafe_allow_html=True,
            )
            with st.expander("DOWNLOAD OPTIONS", expanded=False):
                from utils.export import build_laps_csv, build_charts_zip, build_charts_pdf

                # ── CSV (always immediate) ────────────────────────
                if laps_exp is not None:
                    csv_bytes = build_laps_csv(laps_exp)
                    st.download_button(
                        "⬇ Laps CSV",
                        csv_bytes,
                        file_name=f"laps_{ev_name_exp}_{sess_type_exp}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="dl_csv",
                    )

                st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

                # ── Bulk chart export ────────────────────────────
                charts = st.session_state.get("_f1_charts", {})
                n_charts = len(charts)

                if not charts:
                    st.markdown(
                        "<div style='font-family:var(--font-mono);font-size:0.6rem;"
                        "color:var(--text-d);padding:4px 0 8px;line-height:1.5;'>"
                        "<i class='fa-solid fa-circle-info' style='color:var(--accent);margin-right:5px;'></i>"
                        "Navigate the tabs first to capture charts."
                        "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div style='font-family:var(--font-mono);font-size:0.6rem;"
                        f"color:var(--text-d);margin-bottom:8px;'>"
                        f"<i class='fa-solid fa-check' style='color:var(--accent);margin-right:5px;'></i>"
                        f"{n_charts} chart{'s' if n_charts != 1 else ''} captured"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    fmt = st.radio(
                        "Image format",
                        ["PNG", "JPG", "SVG"],
                        horizontal=True,
                        key="export_fmt",
                    )
                    fmt_lower = fmt.lower()

                    # Invalidate cached bytes when format or chart set changes
                    chart_sig = (fmt_lower, tuple(sorted(charts.keys())))
                    if st.session_state.get("_export_sig") != chart_sig:
                        st.session_state.pop("_export_zip", None)
                        st.session_state.pop("_export_pdf", None)
                        st.session_state["_export_sig"] = chart_sig

                    # ── ZIP ──────────────────────────────────────
                    if "_export_zip" in st.session_state:
                        st.download_button(
                            f"⬇ Save Charts ZIP ({fmt})",
                            st.session_state["_export_zip"],
                            file_name=f"charts_{ev_name_exp}.zip",
                            mime="application/zip",
                            use_container_width=True,
                            key="dl_zip",
                        )
                    else:
                        if st.button(
                            "⚙ Prepare Charts ZIP",
                            use_container_width=True,
                            key="btn_prep_zip",
                        ):
                            with st.spinner(f"Rendering {n_charts} chart(s)…"):
                                try:
                                    st.session_state["_export_zip"] = build_charts_zip(
                                        list(charts.values()),
                                        list(charts.keys()),
                                        fmt=fmt_lower,
                                    )
                                except Exception as e:
                                    st.error(f"ZIP error: {e}")
                            st.rerun()

                    # ── PDF ──────────────────────────────────────
                    if fmt_lower != "svg":
                        if "_export_pdf" in st.session_state:
                            st.download_button(
                                "⬇ Save Report PDF",
                                st.session_state["_export_pdf"],
                                file_name=f"report_{ev_name_exp}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="dl_pdf",
                            )
                        else:
                            if st.button(
                                "⚙ Prepare PDF Report",
                                use_container_width=True,
                                key="btn_prep_pdf",
                            ):
                                with st.spinner(f"Rendering PDF ({n_charts} pages)…"):
                                    try:
                                        st.session_state["_export_pdf"] = build_charts_pdf(
                                            list(charts.values()),
                                            list(charts.keys()),
                                        )
                                    except Exception as e:
                                        st.error(f"PDF error: {e}")
                                st.rerun()

        # ── Footer ───────────────────────────────────────────────
        st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)
        if st.button("← BACK TO HOME", key="btn_back_home", use_container_width=True):
            st.session_state["current_route"] = "landing"
            st.rerun()
        st.markdown(
            "<div class='sb-footer'>Powered by "
            "<a href='https://www.linkedin.com/in/mattia-russo-3b807a305/'"
            " target='_blank'>Mattia Russo</a></div>",
            unsafe_allow_html=True,
        )

    # --- MAIN CONTENT ---
    if st.session_state.get("data_loaded"):
        session     = st.session_state["f1_session"]
        drivers     = st.session_state.get("selected_drivers", [])
        f1_data     = st.session_state.get("f1_data", {})
        ev_name     = f1_data.get("event_name", "")
        sess_type   = f1_data.get("session_type", "")
        sess_year   = f1_data.get("year", "")
        drv_count   = len(drivers)

        # ── Session Context Bar ──────────────────────────────────────────
        driver_pills = "".join(
            f"<span class='data-pill accent'><i class='fa-solid fa-helmet-safety'></i>{d}</span>"
            for d in (drivers[:6] if drivers else [])
        ) + (f"<span class='data-pill'>+{drv_count-6} more</span>" if drv_count > 6 else "")
        if not driver_pills:
            driver_pills = "<span class='data-pill'>No drivers selected</span>"

        st.markdown(
            f"""
            <div class="reveal-card rd-1" style="
                display:flex; align-items:center; gap:16px; flex-wrap:wrap;
                background:linear-gradient(135deg,rgba(33,197,94,0.04) 0%,rgba(6,6,8,0) 60%);
                border:1px solid rgba(33,197,94,0.13); border-radius:14px;
                padding:12px 20px; margin-bottom:20px; position:relative; overflow:hidden;">
                <div style='position:absolute;top:0;left:0;right:0;height:1px;
                    background:linear-gradient(90deg,transparent,rgba(33,197,94,0.4),transparent);'></div>
                <div style='display:flex;align-items:center;gap:10px;flex-shrink:0;'>
                    <span class='live-dot'></span>
                    <span style='font-family:var(--font-mono);font-size:0.62rem;font-weight:800;
                        color:#21C55E;text-transform:uppercase;letter-spacing:1.5px;'>UPLINK ACTIVE</span>
                </div>
                <div style='width:1px;height:24px;background:rgba(255,255,255,0.08);flex-shrink:0;'></div>
                <div style='display:flex;align-items:center;gap:7px;flex-shrink:0;'>
                    <i class='fa-solid fa-flag-checkered' style='color:var(--text-d);font-size:0.72rem;'></i>
                    <span style='font-family:var(--font-mono);font-size:0.68rem;font-weight:700;color:var(--text-s);'>{ev_name}</span>
                </div>
                <div style='display:flex;align-items:center;gap:7px;flex-shrink:0;'>
                    <i class='fa-solid fa-stopwatch' style='color:var(--text-d);font-size:0.72rem;'></i>
                    <span style='font-family:var(--font-mono);font-size:0.68rem;color:var(--text-m);'>{sess_type} · {sess_year}</span>
                </div>
                <div style='flex:1;'></div>
                <div style='display:flex;align-items:center;gap:6px;flex-wrap:wrap;'>{driver_pills}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_tel, tab_race, tab_strat, tab_ms = st.tabs([
            "TELEMETRY ANALYSIS",
            "RACE HISTORY",
            "STRATEGY & TYRES",
            "MULTI-SESSION",
        ])

        with tab_tel:
            st.markdown(
                """
                <div class="tab-banner">
                    <div class="tab-banner-icon">
                        <i class="fa-solid fa-chart-line" style="color:#21C55E;"></i>
                    </div>
                    <div class="tab-banner-body">
                        <div class="tab-banner-title">Telemetry Analysis</div>
                        <div class="tab-banner-desc">Speed traces, G-force diagrams, ERS energy curves, sector splits and advanced driver dynamics</div>
                    </div>
                    <div class="tab-banner-badge">
                        <span class="live-dot"></span>&nbsp;LIVE DATA
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            telemetry.render(session, drivers)

        with tab_race:
            st.markdown(
                """
                <div class="tab-banner">
                    <div class="tab-banner-icon">
                        <i class="fa-solid fa-flag-checkered" style="color:#21C55E;"></i>
                    </div>
                    <div class="tab-banner-body">
                        <div class="tab-banner-title">Race History</div>
                        <div class="tab-banner-desc">Lap-by-lap pace, position tracker, consistency score, fuel-corrected degradation and head-to-head breakdown</div>
                    </div>
                    <div class="tab-banner-badge">
                        <i class="fa-solid fa-trophy" style="font-size:0.65rem; margin-right:4px;"></i>&nbsp;ANALYSIS
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            race.render(session)

        with tab_strat:
            st.markdown(
                """
                <div class="tab-banner">
                    <div class="tab-banner-icon">
                        <i class="fa-solid fa-wrench" style="color:#f59e0b;"></i>
                    </div>
                    <div class="tab-banner-body">
                        <div class="tab-banner-title">Strategy & Tyres</div>
                        <div class="tab-banner-desc">Tyre compound stints, pit stop duration, undercut/overcut windows and stint degradation models</div>
                    </div>
                    <div class="tab-banner-badge" style="border-color:rgba(245,158,11,0.3); background:rgba(245,158,11,0.07);">
                        <i class="fa-solid fa-circle" style="font-size:0.45rem; color:#f59e0b; margin-right:4px;"></i>
                        <span style="color:#f59e0b;">STRATEGY</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            strategy.render(session)

        with tab_ms:
            st.markdown(
                """
                <div class="tab-banner">
                    <div class="tab-banner-icon">
                        <i class="fa-solid fa-layer-group" style="color:#a855f7;"></i>
                    </div>
                    <div class="tab-banner-body">
                        <div class="tab-banner-title">Multi-Session</div>
                        <div class="tab-banner-desc">Cross-session speed overlays, delta comparisons and qualifying progression across FP1 / FP2 / FP3 / Q</div>
                    </div>
                    <div class="tab-banner-badge" style="border-color:rgba(168,85,247,0.3); background:rgba(168,85,247,0.07);">
                        <i class="fa-solid fa-code-compare" style="font-size:0.65rem; color:#a855f7; margin-right:4px;"></i>
                        <span style="color:#a855f7;">COMPARE</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            multi_session.render(session, drivers)

    else:
        st.html(
            """
        <div style="text-align:center; padding:90px 20px 80px; max-width:720px; margin:0 auto;
                    animation:hero-enter 0.85s cubic-bezier(0.19,1,0.22,1) both;">
            <div style="position:relative; display:inline-block; width:120px; height:120px; margin-bottom:44px;">
                <div style="position:absolute; inset:0; border-radius:50%; border:1px solid rgba(33,197,94,0.10);"></div>
                <div style="position:absolute; inset:14px; border-radius:50%; border:1px solid rgba(33,197,94,0.16);"></div>
                <div style="position:absolute; inset:28px; border-radius:50%; border:1px solid rgba(33,197,94,0.24);"></div>
                <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
                    width:38px; height:38px; border-radius:50%;
                    background:rgba(33,197,94,0.07); border:1px solid rgba(33,197,94,0.32);
                    display:flex; align-items:center; justify-content:center;
                    animation:glyph-glow 2.8s ease-in-out infinite;">
                    <i class="fa-solid fa-tower-broadcast" style="color:#21C55E; font-size:1rem;"></i>
                </div>
                <div style="position:absolute; top:50%; left:50%; width:7px; height:7px; margin:-3.5px;
                    border-radius:50%; background:#21C55E; box-shadow:0 0 10px #21C55E;
                    animation:orbit 3s linear infinite;"></div>
                <div style="position:absolute; top:50%; left:50%; width:5px; height:5px; margin:-2.5px;
                    border-radius:50%; background:rgba(33,197,94,0.55);
                    animation:orbit2 5s linear infinite;"></div>
            </div>
            <h1 style="font-family:'Geist Mono',monospace; font-weight:900; text-transform:uppercase;
                letter-spacing:4px; font-size:2.9rem; margin-bottom:0; color:#f4f4f5;
                text-shadow:0 0 60px rgba(33,197,94,0.12);">Systems Online</h1>
            <div style="width:52px; height:2px;
                background:linear-gradient(90deg,transparent,#21C55E,transparent);
                margin:20px auto 24px;"></div>
            <p style="color:#52525b; font-family:'Space Grotesk',sans-serif; font-size:1rem;
                line-height:1.7; margin-bottom:44px; max-width:520px; margin-left:auto; margin-right:auto;">
                Uplink established. Configure year, Grand Prix and session type on the sidebar,
                then press <strong style="color:#71717a; font-weight:600;">LOAD SESSION</strong>
                to initiate data synchronisation.
            </p>
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px;
                max-width:560px; margin:0 auto 48px; text-align:left;">
                <div style="background:#040406; border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px; padding:16px;
                    animation:hero-enter 0.7s 0.1s cubic-bezier(0.19,1,0.22,1) both;">
                    <div style="font-family:'Geist Mono',monospace; font-size:0.52rem; font-weight:800;
                        color:rgba(33,197,94,0.6); letter-spacing:2px; margin-bottom:10px;">STEP 01</div>
                    <i class="fa-solid fa-calendar-days" style="color:#21C55E; font-size:1.1rem; margin-bottom:8px; display:block;"></i>
                    <div style="font-family:'Space Grotesk',sans-serif; font-size:0.78rem; color:#71717a; line-height:1.5;">
                        Select Year, Grand Prix and Session from the sidebar</div>
                </div>
                <div style="background:#040406; border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px; padding:16px;
                    animation:hero-enter 0.7s 0.18s cubic-bezier(0.19,1,0.22,1) both;">
                    <div style="font-family:'Geist Mono',monospace; font-size:0.52rem; font-weight:800;
                        color:rgba(33,197,94,0.6); letter-spacing:2px; margin-bottom:10px;">STEP 02</div>
                    <i class="fa-solid fa-cloud-arrow-down" style="color:#21C55E; font-size:1.1rem; margin-bottom:8px; display:block;"></i>
                    <div style="font-family:'Space Grotesk',sans-serif; font-size:0.78rem; color:#71717a; line-height:1.5;">
                        Press <strong style="color:#a1a1aa;">LOAD SESSION</strong> to fetch telemetry data</div>
                </div>
                <div style="background:#040406; border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px; padding:16px;
                    animation:hero-enter 0.7s 0.26s cubic-bezier(0.19,1,0.22,1) both;">
                    <div style="font-family:'Geist Mono',monospace; font-size:0.52rem; font-weight:800;
                        color:rgba(33,197,94,0.6); letter-spacing:2px; margin-bottom:10px;">STEP 03</div>
                    <i class="fa-solid fa-users" style="color:#21C55E; font-size:1.1rem; margin-bottom:8px; display:block;"></i>
                    <div style="font-family:'Space Grotesk',sans-serif; font-size:0.78rem; color:#71717a; line-height:1.5;">
                        Choose drivers to compare and explore the analytics tabs</div>
                </div>
            </div>
            <div style="display:flex; justify-content:center; gap:7px;">
                <div style="width:6px; height:6px; border-radius:50%; background:#21C55E; animation:fade-step 1.8s 0.0s infinite;"></div>
                <div style="width:6px; height:6px; border-radius:50%; background:#21C55E; animation:fade-step 1.8s 0.3s infinite;"></div>
                <div style="width:6px; height:6px; border-radius:50%; background:#21C55E; animation:fade-step 1.8s 0.6s infinite;"></div>
            </div>
        </div>
        """
        )
