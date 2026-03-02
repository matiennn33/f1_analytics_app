import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plotting import get_driver_color, get_team_color, apply_plotly_style
from utils.session_store import get_cached_laps


def render(session, drivers):
    st.markdown("### Speed & Sectors Performance")

    laps = get_cached_laps(session)
    if not drivers:
        return

    # --- 1. Top Speed ---
    speed_data = []

    for driver in drivers:
        fastest = laps.pick_drivers(driver).pick_fastest()
        if fastest is None:
            continue

        try:
            tel = fastest.get_telemetry()
            max_v = tel["Speed"].max()
            team_color = get_team_color(fastest["Team"], session)

            speed_data.append({"Driver": driver, "Speed": max_v, "Color": team_color})
        except Exception:
            pass

    if speed_data:
        df_spd = pd.DataFrame(speed_data).sort_values("Speed", ascending=False)

        fig_spd = go.Figure(
            go.Bar(
                x=df_spd["Driver"],
                y=df_spd["Speed"],
                marker_color=df_spd["Color"],
                text=[f"{v:.0f}" for v in df_spd["Speed"]],
                textposition="auto",
                hovertemplate="<b>%{x}</b><br>Top Speed: %{y:.1f} km/h<extra></extra>",
            )
        )

        apply_plotly_style(fig_spd, "Top Speed Comparison (Fastest Lap)")
        min_y = df_spd["Speed"].min() - 10
        fig_spd.update_yaxes(range=[min_y, df_spd["Speed"].max() + 5], title="Speed (km/h)")

        st.plotly_chart(fig_spd, width="stretch")

    # --- 2. Sectors ---
    st.markdown("<br>", unsafe_allow_html=True)
    sec_mode = st.radio("SECTORS MODE", ["Best Sectors", "Average Sectors", "Median Sectors"], horizontal=True)

    sectors_data = []
    clean_laps = laps.pick_wo_box().pick_quicklaps().dropna(subset=["Sector1Time", "Sector2Time", "Sector3Time"])

    for driver in drivers:
        d_laps = clean_laps.pick_drivers(driver)
        if d_laps.empty:
            continue

        for i, col in enumerate(["Sector1Time", "Sector2Time", "Sector3Time"], 1):
            if sec_mode == "Best Sectors":
                val = d_laps[col].min()
            elif sec_mode == "Average Sectors":
                val = d_laps[col].mean()
            else:
                val = d_laps[col].median()

            sectors_data.append(
                {
                    "Driver": driver,
                    "Sector": f"Sector {i}",
                    "Time": val.total_seconds(),
                    "Color": get_driver_color(driver, session),
                }
            )

    if sectors_data:
        df_sec = pd.DataFrame(sectors_data)
        fig_sec = make_subplots(rows=1, cols=3, subplot_titles=("Sector 1", "Sector 2", "Sector 3"))

        for i, sector in enumerate(["Sector 1", "Sector 2", "Sector 3"]):
            df_s = df_sec[df_sec["Sector"] == sector].sort_values("Time")
            best_time = df_s["Time"].min()

            colors = ["#21C55E" if t == best_time else c for t, c in zip(df_s["Time"], df_s["Color"])]
            texts = [f"<b>{t:.3f}s</b>" if t == best_time else f"+{(t - best_time):.3f}s" for t in df_s["Time"]]

            fig_sec.add_trace(
                go.Bar(
                    y=df_s["Driver"],
                    x=df_s["Time"],
                    orientation="h",
                    marker_color=colors,
                    text=texts,
                    textposition="auto",
                    hovertemplate=f"<b>%{{y}}</b><br>{sector}: %{{x:.3f}}s<extra></extra>",
                ),
                row=1,
                col=i + 1,
            )

            min_t, max_t = df_s["Time"].min() * 0.98, df_s["Time"].max() * 1.02
            fig_sec.update_xaxes(range=[min_t, max_t], row=1, col=i + 1, showticklabels=False)
            fig_sec.update_yaxes(autorange="reversed", row=1, col=i + 1)

        apply_plotly_style(fig_sec, f"{sec_mode.upper()}")
        fig_sec.update_layout(showlegend=False)
        st.plotly_chart(fig_sec, width="stretch")

    return True
