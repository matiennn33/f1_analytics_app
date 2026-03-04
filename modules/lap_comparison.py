"""
Advanced multi-lap comparison system for F1 Telemetry Analytics.
Compare multiple drivers' best laps against purple lap (session fastest).
Visualize delta, speed, throttle, and other telemetry channels.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Tuple, Optional

from utils.plotting import get_driver_color, apply_plotly_style
from utils.session_store import get_cached_laps
from utils.logger import log_info, log_error
from config import COLORS, FONTS

# Use config colors
BG_CARD = COLORS["bg_card"]
BORDER = COLORS["border"]
TEXT_M = COLORS["text_muted"]
TEXT_W = COLORS["text_white"]


def find_best_lap(laps: pd.DataFrame, driver: str) -> Optional[pd.Series]:
    """
    Find best lap for a driver.

    Args:
        laps: FastF1 laps DataFrame
        driver: Driver abbreviation

    Returns:
        Best lap row or None if not found
    """
    try:
        driver_laps = laps.pick_drivers(driver).pick_quicklaps()
        if driver_laps.empty:
            return None

        best_lap = driver_laps.loc[driver_laps["LapTime"].idxmin()]
        log_info(f"Found best lap for {driver}: {best_lap['LapTime']}", "find_best_lap")
        return best_lap
    except Exception as e:
        log_error(e, f"find_best_lap for {driver}")
        return None


def find_purple_lap(laps: pd.DataFrame) -> Optional[Tuple[str, pd.Series]]:
    """
    Find fastest lap across all drivers (purple lap).

    Args:
        laps: FastF1 laps DataFrame

    Returns:
        Tuple of (driver_name, lap_row) or None if not found
    """
    try:
        quicklaps = laps.pick_quicklaps().dropna(subset=["LapTime"])
        if quicklaps.empty:
            return None

        fastest_idx = quicklaps["LapTime"].idxmin()
        fastest_lap = quicklaps.loc[fastest_idx]
        driver = fastest_lap["Driver"]

        log_info(f"Found purple lap: {driver} - {fastest_lap['LapTime']}", "find_purple_lap")
        return (driver, fastest_lap)
    except Exception as e:
        log_error(e, "find_purple_lap")
        return None


def get_telemetry_delta(
    lap1: pd.Series,
    lap2: pd.Series,
    channel: str = "Speed",
) -> pd.DataFrame:
    """
    Calculate delta between two laps for a given telemetry channel.

    Args:
        lap1: First lap (reference)
        lap2: Second lap (comparison)
        channel: Telemetry channel (Speed, Throttle, Brake, etc)

    Returns:
        DataFrame with distance, delta, and channel values
    """
    try:
        if channel not in lap1.telemetry.columns or channel not in lap2.telemetry.columns:
            return pd.DataFrame()

        tel1 = lap1.telemetry[[channel, "Distance"]].copy()
        tel2 = lap2.telemetry[[channel, "Distance"]].copy()

        # Interpolate to same distance grid
        max_dist = min(tel1["Distance"].max(), tel2["Distance"].max())
        common_dist = np.linspace(0, max_dist, 500)

        val1 = np.interp(common_dist, tel1["Distance"], tel1[channel])
        val2 = np.interp(common_dist, tel2["Distance"], tel2[channel])

        delta = val2 - val1

        return pd.DataFrame({
            "Distance": common_dist,
            channel: val1,
            f"{channel}_Compare": val2,
            "Delta": delta,
        })
    except Exception as e:
        log_error(e, f"get_telemetry_delta for {channel}")
        return pd.DataFrame()


def render_lap_comparison_ui(session) -> None:
    """
    Render multi-lap comparison interface and visualizations.

    Args:
        session: FastF1 session object
    """
    st.markdown("### <i class='fa-solid fa-layer-group'></i> Advanced Multi-Lap Comparison", unsafe_allow_html=True)

    try:
        laps = get_cached_laps(session)

        if laps.empty:
            st.warning("No lap data available for this session")
            return

        # --- PURPLE LAP DETECTION ---
        st.markdown("**🟣 Session Fastest Lap (Purple)**")
        purple_result = find_purple_lap(laps)

        if not purple_result:
            st.error("Could not find purple lap")
            return

        purple_driver, purple_lap = purple_result
        purple_time = purple_lap["LapTime"]

        col_purple1, col_purple2, col_purple3 = st.columns(3)
        with col_purple1:
            st.metric("Purple Driver", purple_driver, f"{purple_driver}")
        with col_purple2:
            st.metric("Purple Time", f"{purple_time}")
        with col_purple3:
            st.metric("Lap #", int(purple_lap["LapNumber"]))

        st.markdown("---")

        # --- DRIVER SELECTION FOR COMPARISON ---
        st.markdown("**🏁 Select Drivers to Compare**")
        all_drivers = sorted(laps["Driver"].dropna().unique().tolist())

        # Remove purple driver from comparison list (already shown above)
        comparison_drivers = st.multiselect(
            "Drivers to compare vs purple lap (no limit)",
            [d for d in all_drivers if d != purple_driver],
            default=all_drivers[:3] if len(all_drivers) > 3 else all_drivers[1:],
            help="Select drivers whose best laps will be compared to purple. Showing all drivers' best laps."
        )

        if not comparison_drivers:
            st.info("Select drivers to see comparison")
            return

        st.markdown("---")

        # --- COLLECT BEST LAPS ---
        st.markdown("**📊 Best Laps Comparison**")

        comparison_data = []
        best_laps_dict: Dict[str, pd.Series] = {"PURPLE": purple_lap}

        for driver in comparison_drivers:
            best_lap = find_best_lap(laps, driver)
            if best_lap is not None:
                time_delta = best_lap["LapTime"] - purple_time
                comparison_data.append({
                    "Driver": driver,
                    "Best Lap Time": best_lap["LapTime"],
                    "Delta to Purple": time_delta,
                    "Lap #": int(best_lap["LapNumber"]),
                })
                best_laps_dict[driver] = best_lap

        if not comparison_data:
            st.error("Could not find best laps for selected drivers")
            return

        # Display comparison table
        comp_df = pd.DataFrame(comparison_data)
        comp_df["Delta to Purple"] = comp_df["Delta to Purple"].dt.total_seconds().round(3)

        st.dataframe(
            comp_df.sort_values("Delta to Purple"),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # --- TELEMETRY CHANNEL SELECTION ---
        st.markdown("**⚙️ Select Telemetry Channels to Compare**")

        available_channels = ["Speed", "Throttle", "Brake", "RPM", "Gear", "Acceleration"]
        selected_channels = st.multiselect(
            "Channels",
            available_channels,
            default=["Speed"],
            help="Select which telemetry channels to visualize"
        )

        st.markdown("---")

        # --- DELTA VISUALIZATION ---
        for channel in selected_channels:
            try:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12)
                fig.update_layout(height=600, hovermode="x unified")

                # Plot purple lap as reference
                fig.add_trace(
                    go.Scatter(
                        x=purple_lap.telemetry["Distance"],
                        y=purple_lap.telemetry[channel],
                        name=f"PURPLE ({purple_driver})",
                        line=dict(color="#9D4EDD", width=3),
                        mode="lines",
                    ),
                    row=1,
                    col=1,
                )

                # Plot comparison drivers
                for driver in comparison_drivers:
                    if driver in best_laps_dict and driver != "PURPLE":
                        best_lap = best_laps_dict[driver]
                        color = get_driver_color(driver, session)

                        fig.add_trace(
                            go.Scatter(
                                x=best_lap.telemetry["Distance"],
                                y=best_lap.telemetry[channel],
                                name=driver,
                                line=dict(color=color, width=2),
                                opacity=0.7,
                                mode="lines",
                            ),
                            row=1,
                            col=1,
                        )

                        # Add delta trace
                        delta_data = get_telemetry_delta(purple_lap, best_lap, channel)

                        if not delta_data.empty:
                            fig.add_trace(
                                go.Scatter(
                                    x=delta_data["Distance"],
                                    y=delta_data["Delta"],
                                    name=f"{driver} Δ",
                                    line=dict(color=color, width=2, dash="dash"),
                                    opacity=0.6,
                                    mode="lines",
                                ),
                                row=2,
                                col=1,
                            )

                fig.update_yaxes(title_text=channel, row=1, col=1)
                fig.update_yaxes(title_text=f"{channel} Delta (s)", row=2, col=1)
                fig.update_xaxes(title_text="Distance (m)", row=2, col=1)

                fig = apply_plotly_style(fig, f"{channel.upper()} COMPARISON: vs PURPLE LAP")

                st.markdown(
                    f"<div style='background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 15px;'>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                log_error(e, f"render_{channel}_comparison")
                st.error(f"Could not render {channel} comparison")

    except Exception as e:
        log_error(e, "render_lap_comparison_ui")
        st.error("Error rendering lap comparison interface")


def render(session) -> None:
    """
    Main render function for lap comparison view.

    Args:
        session: FastF1 session object
    """
    with st.spinner("⏳ Processing lap data..."):
        render_lap_comparison_ui(session)
