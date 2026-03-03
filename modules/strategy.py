from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict

from utils.plotting import apply_plotly_style
from utils.session_store import get_cached_laps, get_cached_results
from utils.logger import log_error, log_info
from config import COLORS, FONTS

# Use config colors
BG_CARD = COLORS["bg_card"]
BORDER = COLORS["border"]
TEXT_M = COLORS["text_muted"]
TEXT_W = COLORS["text_white"]

# Compound colors (tire compounds)
COMPOUND_COLORS: Dict[str, str] = {
    "SOFT": "#FF3333",
    "MEDIUM": "#FFDD57",
    "HARD": "#F0F0F0",
    "INTERMEDIATE": "#39B54A",
    "WET": "#1E90FF",
    "UNKNOWN": "#808080",
}


def render(session) -> None:
    """
    Render strategy and tyres analysis tab with stint breakdown.

    Args:
        session: FastF1 session object
    """
    st.markdown("### <i class='fa-solid fa-stopwatch-20'></i> Strategy & Tyres", unsafe_allow_html=True)

    with st.spinner("📊 Processing strategy data..."):
        try:
            laps = get_cached_laps(session)
            stints = laps[["Driver", "Stint", "Compound", "LapNumber", "FreshTyre"]].dropna(
                subset=["Stint", "Compound", "LapNumber"]
            )

            if stints.empty:
                st.info("⚠️ No stint data available for this session.")
                log_info("Empty stints DataFrame", "strategy.render")
                return

            stint_data = (
                stints.groupby(["Driver", "Stint", "Compound", "FreshTyre"])
                .agg(StartLap=("LapNumber", "min"), EndLap=("LapNumber", "max"))
                .reset_index()
            )

            # Get driver order from results if available, fallback to lap count
            try:
                results_df = get_cached_results(session)
                results = results_df[results_df["GridPosition"] > 0] if results_df is not None else pd.DataFrame()
                driver_order = results.sort_values("GridPosition")["Abbreviation"].tolist()
                missing = [d for d in stint_data["Driver"].unique() if d not in driver_order]
                driver_order.extend(missing)
                log_info(f"Using grid order: {len(driver_order)} drivers", "strategy.render")
            except Exception as e:
                log_error(e, "strategy.render - grid order fallback")
                driver_order = laps.groupby("Driver")["LapNumber"].max().sort_values(ascending=False).index.tolist()

            # Build stint visualization
            fig = go.Figure()
            legend_added: set[str] = set()

            for _, row in stint_data.iterrows():
                driver: str = row["Driver"]
                compound: str = str(row["Compound"]).upper()
                is_fresh: bool = row["FreshTyre"]
                c_color: str = COMPOUND_COLORS.get(compound, "#808080")
                leg_name: str = f"{compound} (FRESH)" if is_fresh else f"{compound} (USED)"

                show_leg: bool = leg_name not in legend_added
                if show_leg:
                    legend_added.add(leg_name)

                fig.add_trace(
                    go.Bar(
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
                        hovertemplate=f"<b>{driver}</b><br>Stint: {row['Stint']}<br>Type: {leg_name}<br>Laps: {row['StartLap']} - {row['EndLap']}<extra></extra>",
                        showlegend=show_leg,
                    )
                )

            fig.update_layout(
                barmode="stack",
                yaxis={"categoryorder": "array", "categoryarray": driver_order[::-1]},
                height=650,
                margin=dict(l=50, r=20, t=50, b=50),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(family="Geist Mono", size=12, color=TEXT_W),
                ),
            )
            fig.update_xaxes(title="LAP NUMBER", title_font=dict(family="Geist Mono", size=11, color=TEXT_M))
            apply_plotly_style(fig, "TYRE STRATEGY & STINTS")

            st.markdown(
                f"<div class='f1-card' style='background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 20px;'>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(fig, width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Errore nel caricamento della strategia: {e}")
