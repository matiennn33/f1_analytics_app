import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import plotly.graph_objects as go
import fastf1.plotting
from utils.plotting import apply_plotly_style, get_driver_color, get_comparison_colors
from utils.session_store import get_cached_laps, get_cached_results
from utils.components import plot_chart

BG_CARD = "#060608"
BORDER  = "rgba(255,255,255,0.07)"
TEXT_M  = "#a1a1aa"
TEXT_W  = "#ffffff"
GREEN   = "#21C55E"
ORANGE  = "#f59e0b"
RED     = "#ef4444"
BLUE    = "#3b82f6"

LOGOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logos")


def _get_team_logo_b64(drv: str, session) -> str:
    try:
        team = fastf1.plotting.get_team_name_by_driver(drv, session)
        for fname in os.listdir(LOGOS_DIR):
            if fname.replace(".png", "").lower() == team.lower():
                with open(os.path.join(LOGOS_DIR, fname), "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return ""

COMPOUND_COLORS = {
    "SOFT":         "#FF3333",
    "MEDIUM":       "#FFDD57",
    "HARD":         "#F0F0F0",
    "INTERMEDIATE": "#39B54A",
    "WET":          "#1E90FF",
    "UNKNOWN":      "#808080",
}


def render_stint_chart(laps, session, stint_data, driver_order):
    fig = go.Figure()
    legend_added: set = set()

    for _, row in stint_data.iterrows():
        driver   = row["Driver"]
        compound = str(row["Compound"]).upper()
        is_fresh = row["FreshTyre"]
        c_color  = COMPOUND_COLORS.get(compound, "#808080")
        leg_name = f"{compound} (FRESH)" if is_fresh else f"{compound} (USED)"
        show_leg = leg_name not in legend_added
        if show_leg:
            legend_added.add(leg_name)

        fig.add_trace(go.Bar(
            y=[driver],
            x=[row["EndLap"] - row["StartLap"] + 1],
            base=[row["StartLap"]],
            orientation="h",
            marker=dict(
                color=c_color,
                line=dict(color=BG_CARD, width=2.5),
                pattern_shape="" if is_fresh else "/",
            ),
            name=leg_name,
            legendgroup=leg_name,
            hovertemplate=(
                f"<b>{driver}</b><br>Stint {row['Stint']}<br>"
                f"{leg_name}<br>Laps {row['StartLap']} \u2013 {row['EndLap']}"
                f" ({row['EndLap'] - row['StartLap'] + 1} laps)<extra></extra>"
            ),
            showlegend=show_leg,
        ))

    fig.update_layout(
        barmode="stack",
        yaxis={"categoryorder": "array", "categoryarray": driver_order[::-1]},
        height=650,
        margin=dict(l=50, r=20, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font=dict(family="Geist Mono", size=12, color=TEXT_W)),
    )
    fig.update_xaxes(title="LAP NUMBER", title_font=dict(family="Geist Mono", size=11, color=TEXT_M))
    apply_plotly_style(fig, "TYRE STRATEGY & STINTS")

    st.markdown(
        f"<div class='f1-card' style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; padding:20px; margin-bottom:20px;'>",
        unsafe_allow_html=True,
    )
    plot_chart(fig, "strategy_stints")
    st.markdown("</div>", unsafe_allow_html=True)


def render_pit_stop_analysis(laps, session):
    """Pit stop time per driver: PitOutTime(out-lap) - PitInTime(in-lap)."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:14px;'>"
        f"<i class='fa-solid fa-wrench' style='color:{ORANGE}; font-size:1.2rem; margin-right:10px;'></i>"
        "<h4 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:0.95rem;"
        " text-transform:uppercase; letter-spacing:1px;'>PIT STOP ANALYSIS</h4></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:rgba(249,115,22,0.05); border:1px solid rgba(249,115,22,0.2); border-left:4px solid {ORANGE}; border-radius:8px;"
        " padding:14px 16px; margin-bottom:18px;'>"
        f"<p style='color:#d4d4d8; font-size:0.85rem; font-family:Space Grotesk,sans-serif; margin:0; line-height:1.5;'>"
        "Durata totale del pit stop misurata da <b>PitInTime</b> (ingresso pit lane) a <b>PitOutTime</b> "
        "(uscita pit lane). Include il tempo fermo al box e il transito in pit lane. "
        "Verde &lt;23s, Arancio 23–26s, Rosso &gt;26s.</p></div>",
        unsafe_allow_html=True,
    )

    needed = {"Driver", "LapNumber", "PitInTime", "PitOutTime", "Stint"}
    if not needed.issubset(laps.columns):
        st.info("Dati PitInTime/PitOutTime non disponibili per questa sessione.")
        return

    # --- Compute stop durations ---
    stop_rows = []
    for drv, grp in laps.groupby("Driver"):
        grp = grp.sort_values("LapNumber").reset_index(drop=True)
        for i, row in grp.iterrows():
            if pd.isna(row["PitInTime"]):
                continue
            # out-lap is the next row
            if i + 1 >= len(grp):
                continue
            out_row = grp.iloc[i + 1]
            if pd.isna(out_row["PitOutTime"]):
                continue
            duration = (out_row["PitOutTime"] - row["PitInTime"]).total_seconds()
            if duration <= 0 or duration > 120:
                continue
            stop_rows.append(dict(
                Driver=drv,
                Lap=int(row["LapNumber"]),
                Stint=int(row["Stint"]) if pd.notna(row["Stint"]) else 0,
                Duration=round(duration, 3),
                Label=f"{drv} S{int(row['Stint']) if pd.notna(row['Stint']) else '?'}",
            ))

    if not stop_rows:
        st.info("Nessun pit stop rilevato. Dati PitInTime/PitOutTime non presenti per questa sessione.")
        return

    stops_df = pd.DataFrame(stop_rows).sort_values(["Driver", "Lap"])
    drivers  = sorted(stops_df["Driver"].unique())
    _cmp     = get_comparison_colors(drivers, session)

    # --- Bar chart: each stop as one bar ---
    fig = go.Figure()
    for drv in drivers:
        drv_stops = stops_df[stops_df["Driver"] == drv]
        color = _cmp.get(drv, get_driver_color(drv, session))
        for _, s in drv_stops.iterrows():
            bar_color = GREEN if s["Duration"] < 23 else (ORANGE if s["Duration"] < 26 else RED)
            fig.add_trace(go.Bar(
                x=[s["Label"]],
                y=[s["Duration"]],
                marker_color=bar_color,
                marker_line_color=color, marker_line_width=2,
                name=drv,
                legendgroup=drv,
                showlegend=False,
                hovertemplate=(
                    f"<b>{drv}</b> Stint {int(s['Stint'])} (Lap {int(s['Lap'])})<br>"
                    f"Pit stop: <b>{s['Duration']:.2f}s</b><extra></extra>"
                ),
            ))

    fig.add_hline(y=23, line_color=GREEN, line_width=1, line_dash="dot",
                  annotation_text="FAST (<23s)", annotation_font_color=GREEN, annotation_font_size=9)
    fig.add_hline(y=26, line_color=RED, line_width=1, line_dash="dot",
                  annotation_text="SLOW (>26s)", annotation_font_color=RED, annotation_font_size=9)

    apply_plotly_style(fig, "PIT STOP DURATION (S)")
    fig.update_layout(height=380, barmode="group", margin=dict(l=50, r=20, t=60, b=60))
    fig.update_yaxes(title_text="DURATION (S)", range=[0, stops_df["Duration"].max() + 4])
    fig.update_xaxes(tickangle=-20, tickfont=dict(family="Geist Mono", size=10))
    plot_chart(fig, "pit_stop_duration")

    # --- Summary tiles ---
    st.markdown("<div style='display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;'>", unsafe_allow_html=True)
    for drv in drivers:
        drv_stops = stops_df[stops_df["Driver"] == drv]
        color      = _cmp.get(drv, get_driver_color(drv, session))
        best_stop  = drv_stops["Duration"].min()
        avg_stop   = drv_stops["Duration"].mean()
        n_stops    = len(drv_stops)
        logo_b64   = _get_team_logo_b64(drv, session)
        logo_html  = (
            f'<img src="data:image/png;base64,{logo_b64}" style="height:36px; max-width:90px; object-fit:contain; opacity:0.9;">'
            if logo_b64 else ""
        )
        stops_html = "".join(
            f"<span style='display:inline-block; margin:2px 4px 2px 0; padding:2px 8px; border-radius:4px; font-size:0.68rem; font-family:Geist Mono,monospace; font-weight:600; border:1px solid rgba(255,255,255,0.1); color:"
            f"{'#21C55E' if r.Duration<23 else ('#f59e0b' if r.Duration<26 else '#ef4444')};'>"
            f"S{int(r.Stint)}&nbsp;{r.Duration:.2f}s</span>"
            for r in drv_stops.itertuples()
        )
        st.markdown(
            f"<div style='background:#000000; border:1px solid {BORDER}; border-left:3px solid {color}; border-radius:10px;"
            f" padding:16px 18px; flex:1; min-width:200px; margin:4px;'>"
            f"<div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>"
            f"{logo_html}"
            f"<div><div style='font-family:Space Grotesk,sans-serif; font-size:1.05rem; color:{color}; font-weight:700; letter-spacing:0.5px; line-height:1.2;'>{drv}</div>"
            f"<div style='font-family:Geist Mono,monospace; font-size:0.65rem; color:{TEXT_M}; letter-spacing:1px; text-transform:uppercase;'>{n_stops} PIT STOP</div>"
            f"</div></div>"
            f"<div style='margin-bottom:10px;'>{stops_html}</div>"
            f"<div style='display:flex; gap:16px; border-top:1px solid rgba(255,255,255,0.07); padding-top:10px;'>"
            f"<div><div style='font-family:Geist Mono,monospace; font-size:0.55rem; color:{TEXT_M}; letter-spacing:1px; margin-bottom:2px;'>BEST</div>"
            f"<div style='font-family:Geist Mono,monospace; font-size:0.9rem; font-weight:700; color:{TEXT_W};'>{best_stop:.2f}s</div></div>"
            f"<div><div style='font-family:Geist Mono,monospace; font-size:0.55rem; color:{TEXT_M}; letter-spacing:1px; margin-bottom:2px;'>AVG</div>"
            f"<div style='font-family:Geist Mono,monospace; font-size:0.9rem; font-weight:700; color:{TEXT_W};'>{avg_stop:.2f}s</div></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render(session):
    tab_strategy, tab_pit = st.tabs(["TYRE STRATEGY", "PIT STOP ANALYSIS"])

    with tab_strategy:
        st.markdown(
            "<div class='reveal-card rd-1'><div class='section-sep'>"
            "<div class='section-sep-icon'><i class='fa-solid fa-circle' style='color:#FF3333; font-size:0.6rem;'></i></div>"
            "<span class='section-sep-label'>Tyre Strategy & Stints</span>"
            "<div class='section-sep-line'></div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        with st.spinner("Elaborazione dati strategia..."):
            try:
                laps = get_cached_laps(session)
                stints = laps[["Driver", "Stint", "Compound", "LapNumber", "FreshTyre"]].dropna(
                    subset=["Stint", "Compound", "LapNumber"]
                )
                if stints.empty:
                    st.info("Nessun dato di stint disponibile per questa sessione.")
                    return

                stint_data = (
                    stints.groupby(["Driver", "Stint", "Compound", "FreshTyre"])
                    .agg(StartLap=("LapNumber", "min"), EndLap=("LapNumber", "max"))
                    .reset_index()
                )

                try:
                    results_df = get_cached_results(session)
                    results = results_df[results_df["GridPosition"] > 0] if results_df is not None else pd.DataFrame()
                    driver_order = results.sort_values("GridPosition")["Abbreviation"].tolist()
                    missing = [d for d in stint_data["Driver"].unique() if d not in driver_order]
                    driver_order.extend(missing)
                except Exception:
                    driver_order = laps.groupby("Driver")["LapNumber"].max().sort_values(ascending=False).index.tolist()

            except Exception as e:
                st.error(f"Errore nel caricamento della strategia: {e}")
                return

        render_stint_chart(laps, session, stint_data, driver_order)

    with tab_pit:
        st.markdown(
            "<div class='reveal-card rd-1'><div class='section-sep'>"
            "<div class='section-sep-icon'><i class='fa-solid fa-wrench'></i></div>"
            "<span class='section-sep-label'>Pit Stop Analysis</span>"
            "<div class='section-sep-line'></div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        with st.spinner("Elaborazione dati pit stop..."):
            try:
                laps = get_cached_laps(session)
                stints = laps[["Driver", "Stint", "Compound", "LapNumber", "FreshTyre"]].dropna(
                    subset=["Stint", "Compound", "LapNumber"]
                )
                if stints.empty:
                    st.info("Nessun dato di stint disponibile per questa sessione.")
                    return
            except Exception as e:
                st.error(f"Errore nel caricamento dei dati: {e}")
                return
        render_pit_stop_analysis(laps, session)
