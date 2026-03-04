"""
Multi-Session Comparison Module
Overlays FP1 / FP2 / FP3 / Qualifying speed traces and delta in a clean layout.
Fixes: _get_events_ms moved to module level, all_data deduplication,
       single speed overlay + delta (no triple-chart clutter).
"""

import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plotting import get_driver_color, apply_plotly_style, get_comparison_colors
from utils.components import plot_chart
import warnings

warnings.filterwarnings("ignore")

BG_CARD = "#060608"
BORDER  = "rgba(255,255,255,0.07)"
TEXT_M  = "#a1a1aa"
TEXT_W  = "#ffffff"
GREEN   = "#21C55E"
ORANGE  = "#f59e0b"

SESSION_PALETTE = ["#21C55E", "#3b82f6", "#f59e0b", "#c084fc"]
SESSION_DASH    = ["solid",    "dot",     "dash",    "dashdot"]


# ── Module-level cached helpers ────────────────────────────────────────────────

@st.cache_data
def _get_event_list(year: int):
    try:
        return fastf1.get_event_schedule(year)["EventName"].tolist()
    except Exception:
        return ["API Offline"]


@st.cache_data
def _get_sessions_for_event(year: int, event_name: str):
    try:
        row = fastf1.get_event_schedule(year)
        row = row[row["EventName"] == event_name].iloc[0]
        sessions = [
            str(row.get(f"Session{i}"))
            for i in range(1, 6)
            if pd.notna(row.get(f"Session{i}")) and str(row.get(f"Session{i}")).lower() != "none"
        ]
        return sessions or ["Race"]
    except Exception:
        return ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Race"]


def _load_session(year: int, event_name: str, session_type: str):
    """Load FastF1 session once, cache in Streamlit session_state."""
    key = f"ms_{year}|{event_name}|{session_type}"
    if key in st.session_state:
        return st.session_state[key]
    try:
        schedule  = fastf1.get_event_schedule(year)
        row       = schedule[schedule["EventName"] == event_name]
        if row.empty:
            return None
        round_num = int(row["RoundNumber"].values[0])
        session   = (fastf1.get_testing_session(year, 1, session_type)
                     if round_num == 0
                     else fastf1.get_session(year, round_num, session_type))
        session.load(telemetry=True, laps=True, weather=False)
        st.session_state[key] = session
        return session
    except Exception as e:
        st.error(f"Errore: {e}")
        return None


def _fastest_lap_data(session, drv: str):
    """Return (fast_lap, telemetry_with_distance) or None."""
    try:
        laps = session.laps.pick_drivers(drv).pick_quicklaps().pick_wo_box()
        fast = laps.pick_fastest()
        if fast is None:
            return None
        return fast, fast.get_telemetry().add_distance()
    except Exception:
        return None


def _detect_q_segments(session):
    """
    Return list of (label, start_sec, end_sec) for Q1/Q2/Q3 segments.
    Uses session.session_status if available, else returns None.
    """
    try:
        status = session.session_status
        if status is None or status.empty:
            return None
        started = status[status["Status"] == "Started"].sort_values("Time")
        if started.empty:
            return None
        starts = started["Time"].dt.total_seconds().values
        labels = ["Q1", "Q2", "Q3"][:len(starts)]
        ends   = list(starts[1:]) + [float("inf")]
        return [(lbl, float(s), float(e)) for lbl, s, e in zip(labels, starts, ends)]
    except Exception:
        return None


def render_quali_progression(session, drivers: list):
    """Per-driver lap time progression across Q1/Q2/Q3 runs, showing improvement each stint."""
    SEG_COLORS = {"Q1": "#3b82f6", "Q2": "#f59e0b", "Q3": "#21C55E"}

    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:14px;'>"
        f"<i class='fa-solid fa-stopwatch' style='color:{GREEN}; font-size:1.2rem; margin-right:10px;'></i>"
        "<h4 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:0.95rem;"
        " text-transform:uppercase; letter-spacing:1px;'>Q1 / Q2 / Q3 PROGRESSION</h4></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:rgba(33,197,94,0.05); border:1px solid rgba(33,197,94,0.2); border-left:4px solid {GREEN}; border-radius:8px;"
        " padding:14px 16px; margin-bottom:18px;'>"
        f"<p style='color:#d4d4d8; font-size:0.85rem; font-family:Space Grotesk,sans-serif; margin:0; line-height:1.5;'>"
        "Andamento dei tempi sul giro per ciascun pilota nel corso della sessione di qualifica. "
        "Ogni punto = un giro cronometrato. Il colore del marker indica il segmento (Q1/Q2/Q3). "
        "La linea tratteggiata mostra il miglioramento progressivo del personal best.</p></div>",
        unsafe_allow_html=True,
    )

    try:
        all_laps = session.laps.copy()
    except Exception:
        st.info("Dati dei giri non disponibili per questa sessione.")
        return

    # Keep only timed laps with valid LapTime
    timed = all_laps.dropna(subset=["LapTime"])
    timed = timed[timed["LapTime"].dt.total_seconds() > 30]  # remove outliers
    if timed.empty:
        st.info("Nessun giro cronometrato trovato.")
        return

    segments = _detect_q_segments(session)

    def _assign_segment(row):
        if segments is None:
            return "Q?"
        t = row["SessionTime"].total_seconds() if pd.notna(row.get("SessionTime")) else 0
        for lbl, s, e in segments:
            if s <= t < e:
                return lbl
        return "Q?"

    timed = timed.copy()
    timed["Segment"] = timed.apply(_assign_segment, axis=1)
    timed["LapSec"]  = timed["LapTime"].dt.total_seconds()

    _cmp   = get_comparison_colors(drivers, session)
    fig    = go.Figure()

    # Background segment shading
    if segments:
        # Get session max time for shaping
        max_t = timed["SessionTime"].dt.total_seconds().max() if (not timed.empty and "SessionTime" in timed.columns) else 5400
        for lbl, s_start, s_end in segments:
            end_x = min(s_end, max_t + 30)
            fig.add_vrect(
                x0=s_start, x1=end_x,
                fillcolor=SEG_COLORS.get(lbl, "#444"),
                opacity=0.05, layer="below", line_width=0,
            )
            fig.add_annotation(
                x=(s_start + min(s_end, max_t)) / 2, y=1, yref="paper",
                text=f"<b>{lbl}</b>",
                showarrow=False,
                font=dict(color=SEG_COLORS.get(lbl, "#aaa"), size=12, family="Geist Mono"),
                xanchor="center", yanchor="top",
            )

    for drv in drivers:
        drv_laps = timed[timed["Driver"] == drv].sort_values("SessionTime" if "SessionTime" in timed.columns else "LapNumber")
        if drv_laps.empty:
            continue
        color = _cmp.get(drv, get_driver_color(drv, session))

        # Scatter: all timed laps, colored by segment
        for seg, seg_df in drv_laps.groupby("Segment"):
            seg_color_marker = SEG_COLORS.get(seg, color)
            fig.add_trace(go.Scatter(
                x=seg_df["SessionTime"].dt.total_seconds() if "SessionTime" in seg_df.columns else seg_df["LapNumber"],
                y=seg_df["LapSec"],
                mode="markers",
                name=f"{drv} {seg}",
                legendgroup=drv,
                showlegend=(seg == drv_laps["Segment"].iloc[0]),
                marker=dict(color=seg_color_marker, size=9, line=dict(color=color, width=1.5)),
                hovertemplate=(
                    f"<b>{drv}</b> [{seg}]<br>"
                    "Tempo: %{y:.3f}s<br>"
                    "Ora sessione: %{x:.0f}s<extra></extra>"
                ),
            ))

        # Personal best progression line
        cum_best = drv_laps["LapSec"].cummin()
        x_vals = (drv_laps["SessionTime"].dt.total_seconds()
                  if "SessionTime" in drv_laps.columns
                  else list(range(len(drv_laps))))
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=cum_best,
            mode="lines",
            name=f"{drv} best",
            legendgroup=drv,
            showlegend=False,
            line=dict(color=color, width=2, dash="dot"),
            hovertemplate=f"<b>{drv}</b> Personal best: %{{y:.3f}}s<extra></extra>",
        ))

        # Annotate final best
        pb = drv_laps["LapSec"].min()
        pb_row = drv_laps.loc[drv_laps["LapSec"].idxmin()]
        pb_x = (pb_row["SessionTime"].total_seconds()
                if "SessionTime" in drv_laps.columns and pd.notna(pb_row.get("SessionTime"))
                else int(drv_laps["LapSec"].idxmin()))
        fig.add_annotation(
            x=pb_x,
            y=pb,
            text=f"<b>{drv} {int(pb//60)}:{pb%60:06.3f}</b>",
            showarrow=True, ax=0, ay=-28, arrowhead=2, arrowcolor=color,
            font=dict(color=color, size=9, family="Geist Mono"),
        )

    apply_plotly_style(fig, "QUALIFYING LAP TIME PROGRESSION")
    fig.update_layout(
        height=500,
        hovermode="closest",
        margin=dict(l=50, r=20, t=70, b=30),
    )
    fig.update_xaxes(title_text="SESSION TIME (S)")
    fig.update_yaxes(title_text="LAP TIME (S)")
    plot_chart(fig, "ms_lap_times")

    # Segment best times table
    st.markdown(
        f"<div style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:10px;"
        " overflow:hidden; margin-top:12px;'>",
        unsafe_allow_html=True,
    )
    seg_labels = [s[0] for s in segments] if segments else ["Q?"]
    header = "".join(
        f"<th style='padding:10px 14px; color:{SEG_COLORS.get(s,'#aaa')}; text-align:center;"
        f" font-family:Geist Mono,monospace; font-size:0.78rem;'>{s}</th>"
        for s in seg_labels
    )
    rows_html = ""
    for i, drv in enumerate(drivers):
        color  = _cmp.get(drv, get_driver_color(drv, session))
        bg     = "#030305" if i % 2 == 0 else BG_CARD
        drv_l  = timed[timed["Driver"] == drv]
        cells  = ""
        for seg in seg_labels:
            seg_laps = drv_l[drv_l["Segment"] == seg]["LapSec"]
            if seg_laps.empty:
                cells += "<td style='padding:10px 14px; text-align:center; color:#555;'>—</td>"
            else:
                best_s = seg_laps.min()
                cells += (
                    f"<td style='padding:10px 14px; text-align:center; color:{TEXT_W};"
                    f" font-family:Geist Mono,monospace; font-size:0.8rem;'>"
                    f"<b>{int(best_s//60)}:{best_s%60:06.3f}</b></td>"
                )
        rows_html += (
            f"<tr style='background:{bg}; border-bottom:1px solid {BORDER};'>"
            f"<td style='padding:10px 14px; color:{color}; font-weight:700;"
            f" font-family:Geist Mono,monospace; font-size:0.8rem;'>{drv}</td>{cells}</tr>"
        )
    st.markdown(
        f"<table style='width:100%; border-collapse:collapse;'>"
        f"<thead><tr style='background:rgba(255,255,255,0.04); border-bottom:1px solid {BORDER};'>"
        f"<th style='padding:10px 14px; text-align:left; color:{TEXT_M};"
        f" font-family:Geist Mono,monospace; font-size:0.78rem;'>DRIVER</th>{header}</tr></thead>"
        f"<tbody>{rows_html}</tbody></table></div>",
        unsafe_allow_html=True,
    )


# ── Main render ────────────────────────────────────────────────────────────────

def render(primary_session, drivers: list):
    st.markdown(
        f'<div style="background:rgba(249,115,22,0.05); border:1px solid rgba(249,115,22,0.18); border-left:4px solid {ORANGE}; border-radius:10px;'
        f' padding:14px 18px; margin-bottom:20px;">'
        '<p style="color:#d4d4d8; font-family:Space Grotesk,sans-serif; font-size:0.88rem;'
        ' line-height:1.55; margin:0;">'
        '<i class="fa-solid fa-circle-info" style="margin-right:8px; color:#f59e0b;"></i>'
        'Confronta i giri più veloci attraverso più sessioni. '
        'Ogni pilota compare <b>una sola volta per sessione</b>: '
        'tratto continuo = primaria, tratteggio diverso = sessione extra.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    if not drivers:
        st.info("Seleziona almeno un pilota nella sidebar.")
        return

    f1_data              = st.session_state.get("f1_data", {})
    primary_year         = f1_data.get("year", 2024)
    primary_event        = f1_data.get("event_name", "")
    primary_session_type = f1_data.get("session_type", "Race")

    # Primary session badge
    st.markdown(
        f'<div style="background:rgba(33,197,94,0.05); border:1px solid rgba(33,197,94,0.2); border-radius:8px;'
        f' padding:12px; margin-bottom:16px; font-family:Geist Mono,monospace;'
        f' font-size:0.85rem; color:{GREEN};">'
        f'<i class="fa-solid fa-check-circle" style="margin-right:8px;"></i>'
        f'{primary_year} — {primary_event} — <b>{primary_session_type}</b>'
        f'<span style="color:{TEXT_M}; font-size:0.7rem; margin-left:12px;">(tratto continuo)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Extra session slots ────────────────────────────────────────────────
    extra_sessions_data = []
    for slot_idx in range(1, 4):
        k = f"ms_slot_{slot_idx}"
        with st.expander(f"Sessione extra #{slot_idx}", expanded=(slot_idx == 1)):
            c_en, c_yr, c_ev, c_ss = st.columns([0.5, 1, 2.5, 1.5])
            with c_en:
                enabled = st.checkbox("Attiva", value=(slot_idx == 1), key=f"{k}_enabled")
            if not enabled:
                continue
            with c_yr:
                ex_year = st.selectbox("Anno", range(2026, 2018, -1), index=0, key=f"{k}_year")
            with c_ev:
                ev_list = _get_event_list(ex_year)
                def_ev  = ev_list.index(primary_event) if primary_event in ev_list else 0
                ex_event = st.selectbox("GP", ev_list, index=def_ev, key=f"{k}_event")
            with c_ss:
                sess_list = _get_sessions_for_event(ex_year, ex_event)
                def_ss = (
                    (sess_list.index(primary_session_type) - 1) % len(sess_list)
                    if primary_session_type in sess_list else 0
                )
                ex_sess = st.selectbox("Sessione", sess_list, index=def_ss, key=f"{k}_session")

            load_col, _ = st.columns([1, 3])
            with load_col:
                if st.button(f"CARICA #{slot_idx}", key=f"{k}_btn"):
                    with st.spinner(f"Caricamento {ex_sess} {ex_year}..."):
                        if _load_session(ex_year, ex_event, ex_sess):
                            st.success(f"'{ex_sess}' caricata!")

            ms_key = f"ms_{ex_year}|{ex_event}|{ex_sess}"
            if ms_key in st.session_state:
                extra_sessions_data.append({
                    "session":     st.session_state[ms_key],
                    "label":       f"{ex_year} {ex_event} — {ex_sess}",
                    "short":       ex_sess,
                    "palette_idx": slot_idx,
                })

    if not extra_sessions_data:
        # Still show qualifying progression if primary session is qualifying
        primary_session_type = st.session_state.get("f1_data", {}).get("session_type", "")
        if "qualifying" in primary_session_type.lower() or "qualif" in primary_session_type.lower():
            st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-layer-group'></i></div><span class='section-sep-label'>Qualifying Progression</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
            render_quali_progression(primary_session, drivers)
        else:
            st.info("Carica almeno una sessione aggiuntiva.")
        return

    st.markdown("<div class='reveal-card rd-1' style='margin:28px 0 18px;'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-arrows-left-right'></i></div><span class='section-sep-label'>Cross-Session Comparison</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)

    # ── Build all_data: ONE entry per (label, driver) — no duplicates ──────
    sessions_to_plot = [{
        "session":     primary_session,
        "label":       f"{primary_year} {primary_event} — {primary_session_type}",
        "short":       primary_session_type,
        "palette_idx": 0,
    }] + extra_sessions_data

    all_data: dict = {}
    _cmp_colors = get_comparison_colors(drivers, primary_session)
    with st.spinner("Caricamento telemetria sessioni..."):
        for s_info in sessions_to_plot:
            for drv in drivers:
                key = (s_info["label"], drv)
                if key in all_data:
                    continue
                result = _fastest_lap_data(s_info["session"], drv)
                if result is None:
                    continue
                fast, tel = result
                all_data[key] = {
                    "tel":         tel,
                    "time":        fast["LapTime"].total_seconds(),
                    "color":       _cmp_colors.get(drv, get_driver_color(drv, s_info["session"])),
                    "short":       s_info["short"],
                    "palette_idx": s_info["palette_idx"],
                    "driver":      drv,
                }

    if not all_data:
        st.warning("Nessun dato telemetrico disponibile.")
        return

    # ── Lap time table ─────────────────────────────────────────────────────
    header_cells = "".join(
        f'<th style="padding:10px 14px; text-align:center;'
        f' color:{all_data.get((sessions_to_plot[0]["label"], drv), {}).get("color", TEXT_W)}; font-weight:700;">'
        f'{drv}</th>'
        for drv in drivers
    )
    rows_html = ""
    for i, s_info in enumerate(sessions_to_plot):
        lbl        = s_info["label"]
        sess_color = SESSION_PALETTE[s_info["palette_idx"] % len(SESSION_PALETTE)]
        dash_name  = SESSION_DASH[s_info["palette_idx"] % len(SESSION_DASH)]
        bg         = "#030305" if i % 2 == 0 else BG_CARD
        cells = "".join(
            f'<td style="padding:10px 14px; text-align:center; color:{TEXT_W};">'
            + (
                f"{int(all_data[(lbl, drv)]['time']//60)}:{all_data[(lbl, drv)]['time']%60:06.3f}"
                if (lbl, drv) in all_data else "—"
            )
            + "</td>"
            for drv in drivers
        )
        rows_html += (
            f'<tr style="background:{bg}; border-bottom:1px solid {BORDER};">'
            f'<td style="padding:10px 14px; color:{sess_color}; font-weight:600; white-space:nowrap;">'
            f'<span style="font-size:0.6rem; margin-right:6px; opacity:.7;">({dash_name})</span>'
            f'{s_info["short"]}</td>{cells}</tr>'
        )

    st.markdown(
        f'<div style="background:{BG_CARD}; border:1px solid {BORDER};'
        f' border-radius:10px; overflow:hidden; margin-bottom:24px;">'
        f'<table style="width:100%; border-collapse:collapse;'
        f' font-family:Geist Mono,monospace; font-size:0.8rem;">'
        f'<thead><tr style="background:rgba(255,255,255,0.04); border-bottom:1px solid {BORDER};">'
        f'<th style="padding:10px 14px; text-align:left; color:{TEXT_M}; font-weight:600;'
        f' letter-spacing:1px;">SESSION</th>'
        f'{header_cells}</tr></thead><tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )

    # ── Speed overlay ──────────────────────────────────────────────────────
    fig_speed = go.Figure()
    for (lbl, drv), d in all_data.items():
        fig_speed.add_trace(go.Scatter(
            x=d["tel"]["Distance"], y=d["tel"]["Speed"],
            mode="lines", name=f"{drv} · {d['short']}",
            line=dict(color=d["color"], width=2.5,
                      dash=SESSION_DASH[d["palette_idx"] % len(SESSION_DASH)]),
            hovertemplate=f"<b>{drv}</b> [{d['short']}]<br>%{{x:.0f}} m → %{{y:.0f}} km/h<extra></extra>",
        ))
    apply_plotly_style(fig_speed, "SPEED TRACE — MULTI-SESSION OVERLAY")
    fig_speed.update_layout(height=390, margin=dict(l=50, r=20, t=60, b=20))
    fig_speed.update_xaxes(title_text="DISTANCE (M)")
    fig_speed.update_yaxes(title_text="SPEED (KM/H)")
    plot_chart(fig_speed, "ms_speed_trace")

    # ── Delta ──────────────────────────────────────────────────────────────
    if len(sessions_to_plot) >= 2:
        primary_label = sessions_to_plot[0]["label"]
        fig_delta = go.Figure()
        fig_delta.add_hline(y=0, line_color="rgba(255,255,255,0.25)",
                            line_width=1.5, line_dash="dash")

        for s_info in sessions_to_plot[1:]:
            lbl   = s_info["label"]
            p_idx = s_info["palette_idx"]
            short = s_info["short"]
            dash  = SESSION_DASH[p_idx % len(SESSION_DASH)]

            for drv in drivers:
                ref = all_data.get((primary_label, drv))
                cmp = all_data.get((lbl, drv))
                if ref is None or cmp is None:
                    continue
                try:
                    rd = ref["tel"]["Distance"].values
                    rt = ref["tel"]["SessionTime"].dt.total_seconds().values
                    cd = cmp["tel"]["Distance"].values
                    ct = cmp["tel"]["SessionTime"].dt.total_seconds().values

                    _, ui1 = np.unique(rd, return_index=True)
                    _, ui2 = np.unique(cd, return_index=True)
                    rd, rt = rd[ui1], rt[ui1]
                    cd, ct = cd[ui2], ct[ui2]

                    ct_i  = np.interp(rd, cd, ct)
                    delta = (ct_i - rt) - (ct_i[0] - rt[0])

                    fig_delta.add_trace(go.Scatter(
                        x=rd, y=delta,
                        mode="lines",
                        name=f"{drv}  {short} vs {sessions_to_plot[0]['short']}",
                        line=dict(color=ref["color"], width=2.5, dash=dash),
                        fill="tozeroy" if len(drivers) == 1 else "none",
                        hovertemplate=(f"<b>{drv}</b> [{short}]<br>"
                                       f"%{{x:.0f}} m: %{{y:+.3f}}s<extra></extra>"),
                    ))
                except Exception:
                    pass

        apply_plotly_style(fig_delta, "DELTA (+ = più lento della sessione primaria)")
        fig_delta.update_layout(height=340, margin=dict(l=50, r=20, t=60, b=20))
        fig_delta.update_xaxes(title_text="DISTANCE (M)")
        fig_delta.update_yaxes(title_text="DELTA (S)")
        plot_chart(fig_delta, "ms_delta")

    # ── Throttle & Brake (expander) ────────────────────────────────────────
    with st.expander("THROTTLE & BRAKE OVERLAY (dettaglio)", expanded=False):
        fig_tb = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04)
        for (lbl, drv), d in all_data.items():
            tel   = d["tel"]
            dash  = SESSION_DASH[d["palette_idx"] % len(SESSION_DASH)]
            short = d["short"]
            g     = f"{drv}_{short}"

            fig_tb.add_trace(go.Scatter(
                x=tel["Distance"], y=tel["Throttle"],
                mode="lines", name=f"{drv} · {short}",
                line=dict(color=d["color"], width=2, dash=dash),
                legendgroup=g,
                hovertemplate=f"<b>{drv}</b> [{short}] Throttle: %{{y:.0f}}%<extra></extra>",
            ), row=1, col=1)

            brake_y = (tel["Brake"].astype(float)
                       if tel["Brake"].dtype != bool
                       else tel["Brake"].astype(int))
            fig_tb.add_trace(go.Scatter(
                x=tel["Distance"], y=brake_y,
                mode="lines", name=f"{drv} · {short}",
                line=dict(color=d["color"], width=2, dash=dash),
                legendgroup=g, showlegend=False,
                hovertemplate=f"<b>{drv}</b> [{short}] Brake: %{{y:.0f}}<extra></extra>",
            ), row=2, col=1)

        apply_plotly_style(fig_tb, "THROTTLE & BRAKE")
        fig_tb.update_yaxes(title_text="THROTTLE (%)", row=1, col=1)
        fig_tb.update_yaxes(title_text="BRAKE",        row=2, col=1)
        fig_tb.update_xaxes(title_text="DISTANCE (M)", row=2, col=1)
        fig_tb.update_layout(height=520, margin=dict(l=50, r=20, t=50, b=20))
        plot_chart(fig_tb, "ms_telemetry")

    # ── Legend ─────────────────────────────────────────────────────────────
    legend = "".join(
        f"<span style='color:{SESSION_PALETTE[s['palette_idx'] % len(SESSION_PALETTE)]};'>■</span>"
        f"<span style='color:{TEXT_M}; margin-left:4px; margin-right:18px;'>"
        f"{s['short']} ({SESSION_DASH[s['palette_idx'] % len(SESSION_DASH)]})</span>"
        for s in sessions_to_plot
    )
    st.markdown(
        f"<div style='margin-top:12px; font-family:Geist Mono,monospace; font-size:0.75rem;'>{legend}</div>",
        unsafe_allow_html=True,
    )

    # Q1/Q2/Q3 Progression — shown only for qualifying sessions
    _pst = st.session_state.get("f1_data", {}).get("session_type", "")
    if "qualifying" in _pst.lower() or "qualif" in _pst.lower():
        st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-stopwatch'></i></div><span class='section-sep-label'>Qualifying Progression</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
        render_quali_progression(primary_session, drivers)
