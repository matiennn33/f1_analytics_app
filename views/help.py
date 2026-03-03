"""
Unified Help & Documentation page for F1 Telemetry Analytics
"""
from __future__ import annotations

import streamlit as st
from config import COLORS, FONTS


def render() -> None:
    """Render the unified help and documentation page."""
    st.markdown(
        f"""
        <div style="padding: 40px 0;">
            <h1 style="color: {COLORS['accent_green']}; font-family: {FONTS['mono']};">
                <i class="fa-solid fa-book"></i> Guide & Features
            </h1>
            <p style="color: {COLORS['text_muted']}; font-size: 1.2rem; font-family: {FONTS['sans']};">
                Complete guide to mastering the F1 Telemetry Analytics platform.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabs for organization
    tab_guide, tab_features, tab_tips = st.tabs(["📖 Quick Start", "⚡ Features", "💡 Advanced Tips"])

    with tab_guide:
        st.markdown(
            f"""
            <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                        border-radius: 12px; padding: 30px; gap: 20px; display: flex; flex-direction: column;">

                <div>
                    <h3 style="color: {COLORS['text_white']}; margin-bottom: 12px;">
                        <i class="fa-solid fa-rocket"></i> Step 1: Initialize Session
                    </h3>
                    <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                        From the home page, click <strong>"Initialize Uplink"</strong> to access the dashboard.
                        Use the sidebar to select your desired year, Grand Prix, and session type (FP1, FP2, FP3, Qualifying, Sprint, Race).
                    </p>
                </div>

                <div>
                    <h3 style="color: {COLORS['text_white']}; margin-bottom: 12px;">
                        <i class="fa-solid fa-cloud-arrow-down"></i> Step 2: Load Data
                    </h3>
                    <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                        Click <strong>"LOAD SESSION"</strong> button. The app will fetch telemetry data from FastF1.
                        First load may take 10-15 seconds; subsequent loads are cached for performance.
                        <br><strong>⏱️ Tip:</strong> Loading is faster during off-season or for recent races (cached servers).
                    </p>
                </div>

                <div>
                    <h3 style="color: {COLORS['text_white']}; margin-bottom: 12px;">
                        <i class="fa-solid fa-users"></i> Step 3: Select Drivers
                    </h3>
                    <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                        Use the multi-select dropdown to choose drivers for comparison.
                        <strong>Maximum 4 drivers</strong> for optimal chart readability.
                        Selected drivers' telemetry will overlay across all analysis tabs.
                    </p>
                </div>

                <div>
                    <h3 style="color: {COLORS['text_white']}; margin-bottom: 12px;">
                        <i class="fa-solid fa-chart-line"></i> Step 4: Analyze
                    </h3>
                    <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                        Navigate between three main analysis sections:
                        <br>• <strong>Telemetry Analysis:</strong> Peak lap performance, dynamics, and track dominance
                        <br>• <strong>Race History:</strong> Long-run pace, degradation analysis, sector times
                        <br>• <strong>Strategy & Tyres:</strong> Stint data, compound usage, pit strategies
                    </p>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_features:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"""
                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                            border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h4 style="color: {COLORS['accent_green']}; margin-top: 0;">
                        <i class="fa-solid fa-bolt"></i> Peak Performance Card
                    </h4>
                    <p style="color: {COLORS['text_muted']}; font-size: 0.95rem;">
                        Compare fastest lap times, sector-by-sector breakdowns, and theoretical gaps vs. ideal lap.
                        Real-time delta calculation shows how close to perfection each driver is.
                    </p>
                </div>

                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                            border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h4 style="color: {COLORS['accent_green']}; margin-top: 0;">
                        <i class="fa-solid fa-chart-pie"></i> GG Diagram
                    </h4>
                    <p style="color: {COLORS['text_muted']}; font-size: 0.95rem;">
                        Tire grip circle visualization showing lateral vs. longitudinal acceleration.
                        Reveals maximum cornering speed, braking capability, and acceleration zones.
                    </p>
                </div>

                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                            border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h4 style="color: {COLORS['accent_green']}; margin-top: 0;">
                        <i class="fa-solid fa-map"></i> 2D Track Dominance
                    </h4>
                    <p style="color: {COLORS['text_muted']}; font-size: 0.95rem;">
                        Spatial visualization of track sections where each driver excels.
                        Heat map overlay shows speed deltas across the entire circuit.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                            border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h4 style="color: {COLORS['accent_green']}; margin-top: 0;">
                        <i class="fa-solid fa-gauge-high"></i> Advanced Metrics
                    </h4>
                    <p style="color: {COLORS['text_muted']}; font-size: 0.95rem;">
                        Power delivery score, DRS percentage, cornering speeds, G-force peaks.
                        AI-powered damage and degradation assessment.
                    </p>
                </div>

                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                            border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h4 style="color: {COLORS['accent_green']}; margin-top: 0;">
                        <i class="fa-solid fa-chart-line"></i> Telemetry Channels
                    </h4>
                    <p style="color: {COLORS['text_muted']}; font-size: 0.95rem;">
                        Speed, throttle, brake, RPM, gear, DRS, ERS energy, and brake pressure channels.
                        Configurable smoothing and manual lap synchronization.
                    </p>
                </div>

                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                            border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h4 style="color: {COLORS['accent_green']}; margin-top: 0;">
                        <i class="fa-solid fa-truck"></i> Strategy Analysis
                    </h4>
                    <p style="color: {COLORS['text_muted']}; font-size: 0.95rem;">
                        Pit stop timing, tyre compound comparison, stint duration analysis.
                        Identifies optimal strategy windows and degradation patterns.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_tips:
        st.markdown(
            f"""
            <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
                        border-radius: 12px; padding: 30px;">

                <h3 style="color: {COLORS['accent_green']}; margin-top: 0;">
                    <i class="fa-solid fa-lightbulb"></i> Pro Tips for Better Analysis
                </h3>

                <p><strong>🎯 Optimal Driver Comparison:</strong> Select 2-3 drivers for clearest chart visibility.
                More drivers = harder to distinguish colors.</p>

                <p><strong>📊 Interpreting GG Diagrams:</strong> Drivers who push further into corners show better
                mechanical grip. Wider loops suggest more tire performance.</p>

                <p><strong>⚡ Power Delivery Score:</strong> Higher % = more consistent throttle application.
                Look for drivers who maintain high scores even on worn tires (tire degradation indicator).</p>

                <p><strong>🏁 Race Pace Analysis:</strong> The race debrief shows lap-by-lap trends.
                Sudden pace drops may indicate tire changes, fuel loading effects, or traffic.</p>

                <p><strong>🛣️ Track Dominance Reading:</strong> Green areas = driver advantage. Red = opponent advantage.
                Use this to identify sector-specific weaknesses in your driving.</p>

                <p><strong>💾 Cache Usage:</strong> The app caches data locally. Refreshing is instant for recent sessions.
                Clear cache if you notice data inconsistencies.</p>

                <p><strong>⌨️ Keyboard Shortcuts:</strong> Use Ctrl+← (Cmd+←) to jump back to home quick.</p>

                <p style="background: {COLORS['border']}; padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['accent_green']};">
                    <strong><i class="fa-solid fa-info-circle"></i> Data Source:</strong> All telemetry sourced from official
                    FastF1 API and official F1 Live Timing servers. Data updates every race weekend.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if st.button("← Back to Home", use_container_width=True):
        st.session_state["current_route"] = "landing"
        st.rerun()
