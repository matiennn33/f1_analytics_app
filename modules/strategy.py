import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.plotting import apply_plotly_style
from utils.session_store import get_cached_laps, get_cached_results

BG_CARD = "#121212"
BORDER = "#27272a"
TEXT_M = "#a1a1aa"
TEXT_W = "#ffffff"


def render(session):
    st.markdown("### <i class='fa-solid fa-stopwatch-20'></i> Strategy & Tyres", unsafe_allow_html=True)

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

            compound_colors = {
                "SOFT": "#FF3333",
                "MEDIUM": "#FFDD57",
                "HARD": "#F0F0F0",
                "INTERMEDIATE": "#39B54A",
                "WET": "#1E90FF",
                "UNKNOWN": "#808080",
            }

            fig = go.Figure()
            legend_added = set()

            for _, row in stint_data.iterrows():
                driver = row["Driver"]
                compound = str(row["Compound"]).upper()
                is_fresh = row["FreshTyre"]
                c_color = compound_colors.get(compound, "#808080")
                leg_name = f"{compound} (FRESH)" if is_fresh else f"{compound} (USED)"

                show_leg = leg_name not in legend_added
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
