import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.plotting import get_driver_color, apply_plotly_style
from utils.formatting import fmt_time
from utils.session_store import get_cached_laps


def render(session, drivers):
    st.markdown("### Advanced Lap Analysis")

    if not drivers:
        st.info("Select drivers to analyze.")
        return None

    laps = get_cached_laps(session)

    # --- 1. Average Gap ---
    fastest_lap_overall = laps.pick_fastest()
    if fastest_lap_overall is None:
        return
    ref_time = fastest_lap_overall["LapTime"].total_seconds()

    avg_data = []
    for driver in drivers:
        d_laps = laps.pick_drivers(driver).pick_wo_box().pick_quicklaps()
        if d_laps.empty:
            continue

        avg_sec = d_laps["LapTime"].dt.total_seconds().mean()
        gap = avg_sec - ref_time
        avg_data.append(
            {
                "Driver": driver,
                "Gap": gap,
                "Color": get_driver_color(driver, session),
                "AvgTimeStr": fmt_time(avg_sec),
            }
        )

    if avg_data:
        df_gap = pd.DataFrame(avg_data).sort_values("Gap")

        fig_gap = go.Figure()
        fig_gap.add_trace(
            go.Bar(
                y=df_gap["Driver"],
                x=df_gap["Gap"],
                orientation="h",
                marker_color=df_gap["Color"],
                text=[f"+{x:.3f}s" for x in df_gap["Gap"]],
                textposition="auto",
                hovertemplate="<b>%{y}</b><br>Avg Pace Gap: +%{x:.3f}s<br>Avg Lap: %{customdata}<extra></extra>",
                customdata=df_gap["AvgTimeStr"],
            )
        )

        apply_plotly_style(fig_gap, "Average Race Pace Gap (vs Best Lap)")
        fig_gap.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_gap, width="stretch")

    # --- 2. Ideal Lap ---
    ideal_data = []
    for driver in drivers:
        d_laps = laps.pick_drivers(driver)
        if d_laps.empty:
            continue

        s1 = d_laps["Sector1Time"].min()
        s2 = d_laps["Sector2Time"].min()
        s3 = d_laps["Sector3Time"].min()
        actual = d_laps.pick_fastest()["LapTime"]

        if pd.notna(s1) and pd.notna(s2) and pd.notna(s3):
            ideal_sec = (s1 + s2 + s3).total_seconds()
            actual_sec = actual.total_seconds()

            ideal_data.append(
                {
                    "Driver": driver,
                    "Type": "Ideal",
                    "Time": ideal_sec,
                    "TimeStr": fmt_time(ideal_sec),
                    "Color": get_driver_color(driver, session),
                }
            )
            ideal_data.append(
                {
                    "Driver": driver,
                    "Type": "Actual Best",
                    "Time": actual_sec,
                    "TimeStr": fmt_time(actual_sec),
                    "Color": get_driver_color(driver, session),
                }
            )

    if ideal_data:
        df_ideal = pd.DataFrame(ideal_data)

        fig_ideal = px.bar(
            df_ideal,
            x="Driver",
            y="Time",
            color="Type",
            barmode="group",
            color_discrete_map={"Ideal": "#00ff00", "Actual Best": "#ffffff"},
            hover_data=["TimeStr"],
        )

        fig_ideal.update_traces(
            hovertemplate="<b>%{x}</b><br>%{data.name}: %{customdata[0]}<extra></extra>"
        )

        apply_plotly_style(fig_ideal, "Theoretical Best vs Actual Fastest Lap")
        min_y = df_ideal["Time"].min() * 0.99
        fig_ideal.update_yaxes(range=[min_y, df_ideal["Time"].max() * 1.005])
        st.plotly_chart(fig_ideal, width="stretch")

    return True
