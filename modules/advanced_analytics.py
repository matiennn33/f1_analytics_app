"""
Advanced Analytics Module
Features:
  - Consistency Score per Driver (0-100%)
  - Weather Impact Panel (Air/Track temp + performance)
  - Understeer/Oversteer Index (per corner)
  - Engine Braking Analysis (coast vs full brake decel)
"""

import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plotting import get_driver_color, apply_plotly_style, get_comparison_colors
from utils.session_store import get_cached_laps
from utils.components import plot_chart
import warnings
import base64
import os

warnings.filterwarnings("ignore")

BG_CARD = "#060608"
BORDER = "rgba(255,255,255,0.07)"
TEXT_M = "#a1a1aa"
TEXT_W = "#ffffff"
GREEN = "#21C55E"
BLUE = "#3b82f6"
ORANGE = "#f59e0b"
RED = "#ef4444"
PURPLE = "#c084fc"

LOGOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logos")


def _get_team_logo_b64(drv: str, session) -> str:
    """Return base64-encoded PNG for the driver's team logo, or empty string."""
    try:
        team = fastf1.plotting.get_team_name_by_driver(drv, session)
        for fname in os.listdir(LOGOS_DIR):
            if fname.replace(".png", "").lower() == team.lower():
                with open(os.path.join(LOGOS_DIR, fname), "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# 1. CONSISTENCY SCORE
# ─────────────────────────────────────────────────────────────────────────────

def _compute_consistency_score(lap_times_sec: pd.Series) -> float:
    """Convert lap time variability to a 0-100 consistency score."""
    lap_times_sec = lap_times_sec.dropna()
    if len(lap_times_sec) < 2:
        return 100.0
    median_t = lap_times_sec.median()
    if median_t <= 0:
        return 0.0
    cv = lap_times_sec.std() / median_t  # Coefficient of Variation
    # cv=0 -> 100, cv=0.05 -> ~0 (5% variation = 0 score)
    score = max(0.0, 100.0 - (cv * 2000.0))
    return round(min(score, 100.0), 1)


def render_consistency_score(session, drivers, race_mode: bool = False, filtered_laps_dict: dict = None):
    """Render the Consistency Score panel for each driver.

    Parameters
    ----------
    race_mode : bool
        When True the data comes from a Race session, so ``pick_quicklaps()``
        is skipped (race laps naturally vary due to SC/VSC) and laps are only
        filtered via ``pick_wo_box()``.
    filtered_laps_dict : dict, optional
        Pre-filtered {driver: DataFrame} from the Race History configuration
        panel. When provided, laps are taken directly from here instead of
        being re-fetched and re-filtered from the session.
    """
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:16px;'>"
        f"<i class='fa-solid fa-chart-bar' style='color:{GREEN}; font-size:1.3rem; margin-right:10px;'></i>"
        "<h3 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:1.1rem; text-transform:uppercase; letter-spacing:1px;'>CONSISTENCY SCORE</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    if filtered_laps_dict is None:
        laps_all = get_cached_laps(session)
    driver_data = []
    _cmp_colors = get_comparison_colors(drivers, session)

    for drv in drivers:
        try:
            if filtered_laps_dict is not None:
                drv_laps = filtered_laps_dict.get(drv)
                if drv_laps is None or drv_laps.empty:
                    continue
                drv_laps = drv_laps.dropna(subset=["LapTime"])
            else:
                _drv_base = laps_all.pick_drivers(drv).pick_wo_box().dropna(subset=["LapTime"])
                if race_mode:
                    drv_laps = _drv_base
                else:
                    drv_laps = _drv_base.pick_quicklaps()
            if drv_laps.empty:
                continue

            lap_sec = drv_laps["LapTime"].dt.total_seconds()
            score = _compute_consistency_score(lap_sec)
            best = lap_sec.min()
            median = lap_sec.median()
            std = lap_sec.std()
            lap_count = len(drv_laps)
            color = _cmp_colors.get(drv, get_driver_color(drv, session))

            driver_data.append(
                {
                    "Driver": drv,
                    "Score": score,
                    "Best": best,
                    "Median": median,
                    "Std": std,
                    "LapCount": lap_count,
                    "Color": color,
                    "LapTimes": lap_sec.values,
                    "LogoB64": _get_team_logo_b64(drv, session),
                }
            )
        except Exception:
            continue

    if not driver_data:
        st.info("Nessun dato di consistenza disponibile per i piloti selezionati.")
        return

    # Score cards
    cols = st.columns(len(driver_data))
    for i, d in enumerate(driver_data):
        score = d["Score"]
        if score >= 85:
            grade, grade_color = "S", GREEN
        elif score >= 70:
            grade, grade_color = "A", "#22d3ee"
        elif score >= 55:
            grade, grade_color = "B", ORANGE
        elif score >= 40:
            grade, grade_color = "C", "#fb923c"
        else:
            grade, grade_color = "D", RED

        score_arc = int(score / 100 * 220)  # degrees of arc (0-220)
        logo_b64 = d.get("LogoB64", "")
        logo_html = (
            f'<div style="margin-bottom:8px;"><img src="data:image/png;base64,{logo_b64}"'
            ' style="height:22px; max-width:80px; object-fit:contain; opacity:0.85;"></div>'
            if logo_b64 else ""
        )
        with cols[i]:
            st.markdown(
                f"""
<div style="background:#000000; border:1px solid {BORDER}; border-radius:12px; padding:20px; text-align:center;">
  {logo_html}
  <div style="display:flex; align-items:center; justify-content:center; margin-bottom:12px;">
    <span style="font-family:'Geist Mono',monospace; font-size:1rem; color:{d['Color']}; font-weight:700;">{d['Driver']}</span>
  </div>
  <div style="position:relative; display:inline-block; margin-bottom:12px;">
    <svg width="120" height="80" viewBox="0 0 120 80">
      <defs>
        <linearGradient id="arc-grad-{d['Driver']}" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:{d['Color']};stop-opacity:1" />
          <stop offset="100%" style="stop-color:{_lighten_hex(d['Color'])};stop-opacity:1" />
        </linearGradient>
      </defs>
      <path d="M 10 70 A 50 50 0 0 1 110 70" stroke="rgba(255,255,255,0.07)" stroke-width="10" fill="none" />
      <path d="M 10 70 A 50 50 0 0 1 110 70" stroke="url(#arc-grad-{d['Driver']})" stroke-width="10" fill="none"
            stroke-dasharray="{score_arc / 220 * 157:.0f} 157" stroke-linecap="round" />
    </svg>
    <div style="position:absolute; bottom:0; left:50%; transform:translateX(-50%); font-family:'Geist Mono',monospace; font-size:1.6rem; font-weight:700; color:{d['Color']};">{grade}</div>
  </div>
  <div style="margin-bottom:4px;">
    <span style="font-family:'Geist Mono',monospace; font-size:2rem; font-weight:700; color:{d['Color']};">{score:.0f}</span><span style="font-size:0.8rem; color:{TEXT_M}; font-family:'Geist Mono',monospace;">/100</span>
  </div>
  <div style="font-size:0.65rem; color:{TEXT_M}; font-family:'Geist Mono',monospace; letter-spacing:1px; margin-bottom:16px;">CONSISTENCY SCORE</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
    <div style="background:#000000; padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.1);">
      <div style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono',monospace;">BEST LAP</div>
      <div style="color:{TEXT_W}; font-size:0.8rem; font-weight:700; font-family:'Geist Mono',monospace;">{int(d['Best']//60)}:{d['Best']%60:06.3f}</div>
    </div>
    <div style="background:#000000; padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.1);">
      <div style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono',monospace;">STD DEV</div>
      <div style="color:{TEXT_W}; font-size:0.8rem; font-weight:700; font-family:'Geist Mono',monospace;">&plusmn;{d['Std']:.3f}s</div>
    </div>
    <div style="background:#000000; padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.1);">
      <div style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono',monospace;">LAPS</div>
      <div style="color:{TEXT_W}; font-size:0.8rem; font-weight:700; font-family:'Geist Mono',monospace;">{d['LapCount']}</div>
    </div>
    <div style="background:#000000; padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.1);">
      <div style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono',monospace;">MEDIAN</div>
      <div style="color:{TEXT_W}; font-size:0.8rem; font-weight:700; font-family:'Geist Mono',monospace;">{int(d['Median']//60)}:{d['Median']%60:06.3f}</div>
    </div>
  </div>
</div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Lap time distribution chart
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:16px;'>"
        f"<i class='fa-solid fa-chart-column' style='color:{GREEN}; font-size:1.3rem; margin-right:10px;'></i>"
        "<h3 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:1.1rem;"
        " text-transform:uppercase; letter-spacing:1px;'>LAP TIME DISTRIBUTION</h3></div>",
        unsafe_allow_html=True,
    )
    fig = go.Figure()
    for d in driver_data:
        sorted_laps = np.sort(d["LapTimes"])
        fig.add_trace(
            go.Box(
                y=d["LapTimes"],
                name=d["Driver"],
                marker_color=d["Color"],
                line=dict(color=d["Color"], width=2),
                fillcolor=f"rgba({_hex_to_rgb(d['Color'])},0.15)",
                boxmean="sd",
                hovertemplate="<b>%{x}</b><br>%{y:.3f}s<extra></extra>",
            )
        )

    apply_plotly_style(fig, "")
    fig.update_layout(height=380, margin=dict(l=50, r=20, t=40, b=20))
    fig.update_yaxes(title_text="LAP TIME (S)")
    plot_chart(fig, "consistency_scatter")


def _hex_to_rgb(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"{r},{g},{b}"


def _lighten_hex(hex_color: str, amount: float = 0.55) -> str:
    """Blend a hex color towards white by `amount` (0=original, 1=white)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. WEATHER IMPACT PANEL
# ─────────────────────────────────────────────────────────────────────────────

def render_weather_impact(session, drivers):
    """Render the Weather Impact panel with air/track temps and lap-time correlation."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:16px;'>"
        f"<i class='fa-solid fa-cloud-sun' style='color:{ORANGE}; font-size:1.3rem; margin-right:10px;'></i>"
        "<h3 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:1.1rem; text-transform:uppercase; letter-spacing:1px;'>WEATHER IMPACT ANALYSIS</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    laps_all = get_cached_laps(session)

    # Try to get weather data per lap
    weather_records = []
    try:
        for drv in drivers:
            drv_laps = (
                laps_all.pick_drivers(drv)
                .pick_quicklaps()
                .pick_wo_box()
                .dropna(subset=["LapTime"])
            )
            for _, lap in drv_laps.iterrows():
                try:
                    w = lap.get_weather_data()
                    weather_records.append(
                        {
                            "Driver": drv,
                            "LapNumber": lap["LapNumber"],
                            "LapTime": lap["LapTime"].total_seconds(),
                            "AirTemp": float(w["AirTemp"]) if pd.notna(w["AirTemp"]) else np.nan,
                            "TrackTemp": float(w["TrackTemp"]) if pd.notna(w["TrackTemp"]) else np.nan,
                            "Humidity": float(w["Humidity"]) if pd.notna(w.get("Humidity", np.nan)) else np.nan,
                            "WindSpeed": float(w["WindSpeed"]) if pd.notna(w.get("WindSpeed", np.nan)) else np.nan,
                            "Rainfall": bool(w.get("Rainfall", False)),
                        }
                    )
                except Exception:
                    pass
    except Exception:
        pass

    if not weather_records:
        st.info("Dati meteo non disponibili per questa sessione.")
        return

    weather_df = pd.DataFrame(weather_records).dropna(subset=["AirTemp", "TrackTemp"])

    if weather_df.empty:
        st.info("Dati meteo insufficienti per l'analisi.")
        return

    # Summary metrics
    avg_air = weather_df["AirTemp"].mean()
    avg_track = weather_df["TrackTemp"].mean()
    avg_humidity = weather_df["Humidity"].mean() if weather_df["Humidity"].notna().any() else np.nan
    avg_wind = weather_df["WindSpeed"].mean() if weather_df["WindSpeed"].notna().any() else np.nan
    has_rain = weather_df["Rainfall"].any()

    # Condition assessment
    if avg_track > 50:
        track_condition = ("VERY HOT", RED, "fa-temperature-high", "Gomme surriscaldate, alta pressione pneumatici, rischio blistering. Performance negativamente impattata.")
    elif avg_track > 40:
        track_condition = ("HOT", ORANGE, "fa-sun", "Track evolution rapida. Mescole medie e soft in difficoltà. Warm-up rapido.")
    elif avg_track > 28:
        track_condition = ("OPTIMAL", GREEN, "fa-check-circle", "Finestra ideale per le gomme. Performance massima, degrado controllato.")
    elif avg_track > 18:
        track_condition = ("COLD", BLUE, "fa-snowflake", "Gomme fredde, graining probabile. Warm-up lento, stint corti necessari.")
    else:
        track_condition = ("FREEZING", PURPLE, "fa-icicles", "Pista pericolosamente fredda. Aderenza ridotta, mescole extra-soft necessarie.")

    cond_label, cond_color, cond_icon, cond_desc = track_condition

    # Weather summary cards
    wc1, wc2, wc3, wc4 = st.columns(4)
    _weather_metric_card(wc1, "AIR TEMP", f"{avg_air:.1f}°C", "fa-thermometer-half", ORANGE)
    _weather_metric_card(wc2, "TRACK TEMP", f"{avg_track:.1f}°C", "fa-road", cond_color)
    _weather_metric_card(wc3, "HUMIDITY", f"{avg_humidity:.0f}%" if pd.notna(avg_humidity) else "N/A", "fa-droplet", BLUE)
    _weather_metric_card(wc4, "WIND SPEED", f"{avg_wind:.1f} km/h" if pd.notna(avg_wind) else "N/A", "fa-wind", TEXT_M)

    st.markdown("<br>", unsafe_allow_html=True)

    # Condition banner
    rain_html = (
        "<div style=\"margin-top:8px; font-family:'Geist Mono',monospace; font-size:0.75rem; color:#ef4444;\">"
        "<i class='fa-solid fa-cloud-rain' style='margin-right:6px;'></i>RAINFALL DETECTED — WET CONDITIONS</div>"
        if has_rain else ""
    )
    st.markdown(
        f"""
<div style="background:rgba({_hex_to_rgb(cond_color)},0.08); border:1px solid {cond_color}40; border-left:4px solid {cond_color}; border-radius:8px; padding:16px; margin-bottom:20px; display:flex; align-items:flex-start; gap:14px;">
  <i class="fa-solid {cond_icon}" style="color:{cond_color}; font-size:1.4rem; margin-top:2px;"></i>
  <div>
    <div style="font-family:'Geist Mono',monospace; font-size:0.8rem; font-weight:700; color:{cond_color}; margin-bottom:4px; letter-spacing:1px;">TRACK CONDITION: {cond_label}</div>
    <div style="font-family:'Space Grotesk',sans-serif; font-size:0.9rem; color:#d4d4d8; line-height:1.5;">{cond_desc}</div>
    {rain_html}
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    # Scatter: TrackTemp vs LapTime per driver
    _cmp_colors_weather = get_comparison_colors(drivers, session)
    if len(weather_df) > 5:
        fig = go.Figure()
        for drv in drivers:
            drv_w = weather_df[weather_df["Driver"] == drv]
            if drv_w.empty:
                continue
            color = _cmp_colors_weather.get(drv, get_driver_color(drv, session))
            fig.add_trace(
                go.Scatter(
                    x=drv_w["TrackTemp"],
                    y=drv_w["LapTime"],
                    mode="markers",
                    name=drv,
                    marker=dict(color=color, size=8, opacity=0.75, line=dict(color="#000", width=1)),
                    hovertemplate=f"<b>{drv}</b><br>Track: %{{x:.1f}}°C<br>Lap: %{{y:.3f}}s<extra></extra>",
                )
            )
            # Trend line (linear fit)
            if len(drv_w) >= 4:
                try:
                    x_fit = drv_w["TrackTemp"].values
                    y_fit = drv_w["LapTime"].values
                    m, b = np.polyfit(x_fit, y_fit, 1)
                    x_range = np.linspace(x_fit.min(), x_fit.max(), 50)
                    fig.add_trace(
                        go.Scatter(
                            x=x_range,
                            y=m * x_range + b,
                            mode="lines",
                            name=f"{drv} trend",
                            line=dict(color=color, width=1.5, dash="dot"),
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                except Exception:
                    pass

        apply_plotly_style(fig, "TRACK TEMPERATURE vs LAP TIME")
        fig.update_layout(height=380, margin=dict(l=50, r=20, t=60, b=20))
        fig.update_xaxes(title_text="TRACK TEMP (°C)")
        fig.update_yaxes(title_text="LAP TIME (S)")
        plot_chart(fig, "weather_impact_scatter")

    # Track temp evolution over laps
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    for drv in drivers:
        drv_w = weather_df[weather_df["Driver"] == drv].sort_values("LapNumber")
        if drv_w.empty:
            continue
        color = _cmp_colors_weather.get(drv, get_driver_color(drv, session))
        fig2.add_trace(
            go.Scatter(
                x=drv_w["LapNumber"],
                y=drv_w["LapTime"],
                mode="lines+markers",
                name=f"{drv} PACE",
                line=dict(color=color, width=2.5),
                marker=dict(size=4),
                hovertemplate=f"<b>{drv}</b> Lap %{{x}}: %{{y:.3f}}s<extra></extra>",
            ),
            secondary_y=False,
        )

    # Track temp on secondary axis
    avg_track_by_lap = weather_df.groupby("LapNumber")["TrackTemp"].mean().reset_index()
    fig2.add_trace(
        go.Scatter(
            x=avg_track_by_lap["LapNumber"],
            y=avg_track_by_lap["TrackTemp"],
            mode="lines",
            name="TRACK TEMP",
            line=dict(color=ORANGE, width=1.5, dash="dot"),
            hovertemplate="Track Temp Lap %{x}: %{y:.1f}°C<extra></extra>",
        ),
        secondary_y=True,
    )

    apply_plotly_style(fig2, "PACE EVOLUTION & TRACK TEMPERATURE")
    fig2.update_layout(height=380, margin=dict(l=50, r=60, t=60, b=20))
    fig2.update_xaxes(title_text="LAP NUMBER")
    fig2.update_yaxes(title_text="LAP TIME (S)", secondary_y=False)
    fig2.update_yaxes(title_text="TRACK TEMP (°C)", secondary_y=True, showgrid=False, tickfont=dict(color=ORANGE))
    plot_chart(fig2, "stint_degradation")


def _weather_metric_card(col, label, value, icon, color):
    with col:
        st.markdown(
            f"""
<div style="background:#000000; border:1px solid {BORDER}; border-radius:10px; padding:16px; text-align:center;">
  <i class="fa-solid {icon}" style="color:{color}; font-size:1.4rem; margin-bottom:8px; display:block;"></i>
  <div style="font-family:'Geist Mono',monospace; font-size:1.3rem; font-weight:700; color:{color}; margin-bottom:4px;">{value}</div>
  <div style="font-family:'Geist Mono',monospace; font-size:0.55rem; color:{TEXT_M}; letter-spacing:1px;">{label}</div>
</div>""",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. UNDERSTEER / OVERSTEER INDEX
# ─────────────────────────────────────────────────────────────────────────────

def render_understeer_oversteer(session, drivers):
    """Render the Understeer/Oversteer Index analysis per corner."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:16px;'>"
        f"<i class='fa-solid fa-steering-wheel' style='color:{PURPLE}; font-size:1.3rem; margin-right:10px;'></i>"
        "<h3 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:1.1rem; text-transform:uppercase; letter-spacing:1px;'>UNDERSTEER / OVERSTEER INDEX</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Info box
    st.markdown(
        f"""
<div style="background:rgba(168,85,247,0.05); border:1px solid rgba(168,85,247,0.2); border-left:4px solid {PURPLE}; border-radius:8px; padding:16px; margin-bottom:20px;">
  <h4 style="color:#fff; font-family:'Geist Mono',monospace; font-size:0.85rem; margin:0 0 10px 0;">
    <i class="fa-solid fa-graduation-cap" style="color:{PURPLE}; margin-right:8px;"></i> COME LEGGERE L'INDICE
  </h4>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
    <p style="color:#d4d4d8; font-family:'Space Grotesk',sans-serif; font-size:0.85rem; line-height:1.5; margin:0;">
      <b style="color:{RED};">Understeer (US Index &lt; 0):</b> Il pilota deve ridurre la velocità più del previsto per mantenere la traiettoria. 
      Il treno anteriore supera il limite di aderenza, l'auto "spinge" verso l'esterno della curva.
    </p>
    <p style="color:#d4d4d8; font-family:'Space Grotesk',sans-serif; font-size:0.85rem; line-height:1.5; margin:0;">
      <b style="color:{GREEN};">Oversteer (US Index &gt; 0):</b> Il treno posteriore tende a perdere aderenza. 
      L'auto "ruota" più del necessario. Richiede correzioni di sterzo. Potenzialmente più veloce ma instabile.
    </p>
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    circuit_info = None
    try:
        circuit_info = session.get_circuit_info()
    except Exception:
        pass

    _cmp_colors_usos = get_comparison_colors(drivers, session)
    laps_cache = {}
    for drv in drivers:
        try:
            laps = get_cached_laps(session).pick_drivers(drv).pick_quicklaps().pick_wo_box()
            fast = laps.pick_fastest()
            if fast is None:
                continue
            tel = fast.get_telemetry().add_distance()
            laps_cache[drv] = {"tel": tel, "color": _cmp_colors_usos.get(drv, get_driver_color(drv, session))}
        except Exception:
            continue

    if not laps_cache:
        st.info("Dati telemetrici non disponibili per l'analisi US/OS.")
        return

    # Compute handling index per driver per corner
    # Using G_Lat and Speed relationship: lateral_coeff = G_Lat / (v^2)
    # Higher ratio = more oversteer tendency (car rotates more)
    # Lower ratio = understeer tendency

    # First compute baseline lateral coefficient for each driver
    driver_corner_data = {}

    for drv, cache in laps_cache.items():
        tel = cache["tel"].copy()
        if "Speed" not in tel.columns:
            continue

        # Compute G_Lat from XY path curvature if column is missing or near-zero
        has_glat = "G_Lat" in tel.columns and tel["G_Lat"].abs().max() > 0.01
        if not has_glat:
            if "X" in tel.columns and "Y" in tel.columns:
                try:
                    xp = tel["X"].values.astype(float)
                    yp = tel["Y"].values.astype(float)
                    dx = np.gradient(xp)
                    dy = np.gradient(yp)
                    ddx = np.gradient(dx)
                    ddy = np.gradient(dy)
                    denom = (dx ** 2 + dy ** 2) ** 1.5
                    kappa = np.where(denom > 1e-10, (dx * ddy - dy * ddx) / denom, 0.0)
                    v_ms_arr = tel["Speed"].values / 3.6
                    tel = tel.copy()
                    tel["G_Lat"] = np.abs(v_ms_arr ** 2 * kappa / 9.81)
                except Exception:
                    continue
            else:
                continue

        corner_indices = {}

        if circuit_info is not None:
            for _, corner in circuit_info.corners.iterrows():
                dist = corner["Distance"]
                c_num = corner["Number"]
                search = 60  # metres window around corner
                mask = (tel["Distance"] > dist - search) & (tel["Distance"] < dist + search)
                segment = tel[mask]
                if segment.empty or len(segment) < 5:
                    continue

                v = segment["Speed"].values
                g_lat = segment["G_Lat"].abs().values

                # Find apex (min speed in segment)
                min_speed_idx = np.argmin(v)
                apex_speed = v[min_speed_idx]
                apex_g_lat = g_lat[min_speed_idx] if g_lat[min_speed_idx] > 0 else np.nanmean(g_lat)

                if apex_speed < 30:  # skip chicanes/pit entry
                    continue

                # Lateral handling coeff: G_Lat / (v^2) * 10000 (normalised)
                v2 = apex_speed ** 2
                if v2 > 0:
                    handling_coeff = (apex_g_lat / v2) * 10000.0
                else:
                    handling_coeff = 0.0

                corner_indices[c_num] = {
                    "handling_coeff": handling_coeff,
                    "apex_speed": apex_speed,
                    "apex_g_lat": apex_g_lat,
                    "distance": dist,
                }
        else:
            # Without circuit_info, use 20-bin segmentation
            max_dist = tel["Distance"].max()
            bin_edges = np.linspace(0, max_dist, 21)
            for bin_n in range(20):
                mask = (tel["Distance"] >= bin_edges[bin_n]) & (tel["Distance"] < bin_edges[bin_n + 1])
                segment = tel[mask]
                if segment.empty:
                    continue
                v = segment["Speed"].values
                g_lat = segment["G_Lat"].abs().values
                idx = np.argmin(v)
                apex_v = v[idx]
                apex_gl = g_lat[idx] if len(g_lat) > 0 else 0
                if apex_v < 30:
                    continue
                v2 = apex_v ** 2
                coeff = (apex_gl / v2) * 10000.0 if v2 > 0 else 0.0
                corner_indices[f"S{bin_n+1}"] = {
                    "handling_coeff": coeff,
                    "apex_speed": apex_v,
                    "apex_g_lat": apex_gl,
                    "distance": bin_edges[bin_n],
                }

        driver_corner_data[drv] = corner_indices

    if not driver_corner_data:
        st.info("Dati G laterale insufficienti per calcolare l'indice US/OS.")
        return

    # Compute relative index: compare each driver to average
    all_corners = set()
    for d in driver_corner_data.values():
        all_corners.update(d.keys())
    all_corners = sorted(all_corners, key=lambda x: driver_corner_data[drivers[0]].get(x, {}).get("distance", 0) if drivers[0] in driver_corner_data else 0)

    # Build comparison dataframe
    rows = []
    for c in all_corners:
        row = {"Corner": c}
        for drv in driver_corner_data:
            if c in driver_corner_data[drv]:
                row[drv] = driver_corner_data[drv][c]["handling_coeff"]
            else:
                row[drv] = np.nan
        rows.append(row)
    df_corners = pd.DataFrame(rows).set_index("Corner")

    # Normalize: for each corner, compute index relative to mean
    # Positive = more oversteer tendency, Negative = more understeer
    if len(df_corners.columns) >= 2:
        mean_row = df_corners.mean(axis=1)
        df_normalized = df_corners.sub(mean_row, axis=0).div(mean_row.replace(0, np.nan), axis=0) * 100
    else:
        df_normalized = df_corners  # single driver, show raw coefficients

    # Plot
    fig = go.Figure()
    corner_labels = [str(c) for c in df_normalized.index]
    x_vals = list(range(len(corner_labels)))

    for drv in laps_cache.keys():
        if drv not in df_normalized.columns:
            continue
        color = laps_cache[drv]["color"]
        y_vals = df_normalized[drv].values.tolist()
        fig.add_trace(
            go.Bar(
                x=corner_labels,
                y=y_vals,
                name=drv,
                marker_color=[
                    f"rgba({_hex_to_rgb(color)},0.85)" if (not np.isnan(v) and v >= 0) else f"rgba(239,68,68,0.85)"
                    for v in y_vals
                ],
                hovertemplate=f"<b>{drv}</b><br>Corner %{{x}}<br>Index: %{{y:.1f}}<extra></extra>",
            )
        )

    fig.add_hline(y=0, line_color="rgba(255,255,255,0.3)", line_width=1.5, line_dash="dash")
    fig.add_hrect(y0=-5, y1=5, fillcolor="rgba(255,255,255,0.02)", line_width=0, annotation_text="NEUTRAL ZONE", annotation_position="top right", annotation_font_color=TEXT_M, annotation_font_size=10)

    apply_plotly_style(fig, "UNDERSTEER / OVERSTEER INDEX PER CORNER")
    fig.update_layout(
        height=420,
        barmode="group",
        margin=dict(l=50, r=20, t=60, b=40),
        xaxis_title="CORNER NUMBER",
        yaxis_title="US/OS INDEX (+ = OS, − = US)",
    )

    fig.add_annotation(
        text="▼ UNDERSTEER DOMINANT",
        x=0.01, y=0.02, xref="paper", yref="paper",
        showarrow=False, font=dict(color=RED, size=10, family="Geist Mono"), align="left",
    )
    fig.add_annotation(
        text="▲ OVERSTEER DOMINANT",
        x=0.01, y=0.98, xref="paper", yref="paper",
        showarrow=False, font=dict(color=GREEN, size=10, family="Geist Mono"), align="left",
    )

    plot_chart(fig, "downforce_analysis")

    # Per-driver summary
    if len(laps_cache) >= 1:
        st.markdown("<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:12px; margin-top:8px;'>", unsafe_allow_html=True)
        for drv in laps_cache.keys():
            if drv not in df_normalized.columns:
                continue
            vals = df_normalized[drv].dropna()
            if vals.empty:
                continue
            mean_idx = vals.mean()
            us_corners = int((vals < -5).sum())
            os_corners = int((vals > 5).sum())
            balance_text = "OVERSTEER PRONE" if mean_idx > 3 else ("UNDERSTEER PRONE" if mean_idx < -3 else "BALANCED")
            balance_color = GREEN if mean_idx > 3 else (RED if mean_idx < -3 else ORANGE)
            color = laps_cache[drv]["color"]
            logo_b64 = _get_team_logo_b64(drv, session)
            logo_html = (
                f'<img src="data:image/png;base64,{logo_b64}"'
                ' style="height:20px; max-width:72px; object-fit:contain; opacity:0.8;">'
                if logo_b64 else ""
            )
            st.markdown(
                f"""
<div style="background:#000000; border:1px solid {BORDER}; border-radius:10px; padding:16px;">
  <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid {BORDER};">
    <div style="display:flex; align-items:center; gap:8px;">
      <div style="width:4px; height:18px; background:{color}; border-radius:2px;"></div>
      <span style="font-family:'Geist Mono',monospace; font-size:0.9rem; color:{color}; font-weight:700;">{drv}</span>
    </div>
    {logo_html}
  </div>
  <div style="font-family:'Geist Mono',monospace; font-size:1.05rem; font-weight:700; color:{balance_color}; margin-bottom:10px; letter-spacing:0.5px;">{balance_text}</div>
  <div style="text-align:center; margin-bottom:10px; padding:8px; background:rgba(255,255,255,0.03); border-radius:6px; border:1px solid rgba(255,255,255,0.06);">
    <div style="font-family:'Geist Mono',monospace; font-size:0.5rem; color:{TEXT_M}; letter-spacing:1px; margin-bottom:2px;">AVG INDEX</div>
    <div style="font-family:'Geist Mono',monospace; font-size:1.6rem; font-weight:700; color:{balance_color};">{mean_idx:+.1f}</div>
  </div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-family:'Geist Mono',monospace;">
    <div style="text-align:center; padding:6px; background:rgba(239,68,68,0.06); border-radius:5px; border:1px solid rgba(239,68,68,0.15);">
      <div style="color:{RED}; font-size:0.5rem; letter-spacing:0.5px;">US CORNERS</div>
      <div style="color:{TEXT_W}; font-size:0.85rem; font-weight:700;">{us_corners}</div>
    </div>
    <div style="text-align:center; padding:6px; background:rgba(33,197,94,0.06); border-radius:5px; border:1px solid rgba(33,197,94,0.15);">
      <div style="color:{GREEN}; font-size:0.5rem; letter-spacing:0.5px;">OS CORNERS</div>
      <div style="color:{TEXT_W}; font-size:0.85rem; font-weight:700;">{os_corners}</div>
    </div>
  </div>
</div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. ENGINE BRAKING ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def render_engine_braking(session, drivers):
    """Render the Engine Braking analysis: coast vs full brake deceleration."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:16px;'>"
        f"<i class='fa-solid fa-gauge-simple-high' style='color:{BLUE}; font-size:1.3rem; margin-right:10px;'></i>"
        "<h3 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:1.1rem; text-transform:uppercase; letter-spacing:1px;'>ENGINE BRAKING ANALYSIS</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div style="background:rgba(59,130,246,0.05); border:1px solid rgba(59,130,246,0.2); border-left:4px solid {BLUE}; border-radius:8px; padding:16px; margin-bottom:20px;">
  <p style="color:#d4d4d8; font-family:'Space Grotesk',sans-serif; font-size:0.9rem; line-height:1.5; margin:0;">
    <b style="color:#fff;">Engine Braking</b> è la decelerazione generata dal motore quando il pilota toglie il gas senza premere il freno (fase di <i>coast</i>).
    Comparato con la frenata completa, rivela la mappatura del <b>engine brake map</b> e la tecnica di <b>lift-and-coast</b>.
    Un engine braking elevato aiuta a caricare l'anteriore prima dell'ingresso curva.
  </p>
</div>""",
        unsafe_allow_html=True,
    )

    _cmp_colors_eb = get_comparison_colors(drivers, session)
    laps_cache = {}
    for drv in drivers:
        try:
            laps = get_cached_laps(session).pick_drivers(drv).pick_quicklaps().pick_wo_box()
            fast = laps.pick_fastest()
            if fast is None:
                continue
            tel = fast.get_telemetry().add_distance()
            laps_cache[drv] = {"tel": tel, "color": _cmp_colors_eb.get(drv, get_driver_color(drv, session))}
        except Exception:
            continue

    if not laps_cache:
        st.info("Dati telemetrici non disponibili per l'analisi di engine braking.")
        return

    # Compute deceleration profiles
    driver_stats = []
    fig_profiles = go.Figure()

    for drv, cache in laps_cache.items():
        tel = cache["tel"].copy()
        color = cache["color"]

        v_ms = tel["Speed"] / 3.6
        dt = tel["Time"].dt.total_seconds().diff().fillna(0.02).clip(lower=0.001)
        decel = -(v_ms.diff() / dt)  # positive = decelerating

        brake_bool = tel["Brake"] > 0 if tel["Brake"].dtype != bool else tel["Brake"]
        throttle = tel["Throttle"]

        # Coast phase: throttle=0, no brake, speed>80kph
        coast_mask = (throttle < 3) & (~brake_bool) & (tel["Speed"] > 80)
        # Full brake phase: brake active, throttle=0
        brake_mask = brake_bool & (throttle < 5) & (tel["Speed"] > 80)
        # Lift phase: throttle 0-30, no brake
        lift_mask = (throttle >= 3) & (throttle < 30) & (~brake_bool) & (tel["Speed"] > 80)

        coast_decel = decel[coast_mask].clip(lower=0)
        brake_decel = decel[brake_mask].clip(lower=0)
        lift_decel = decel[lift_mask].clip(lower=0)

        coast_avg = float(coast_decel.mean()) if not coast_decel.empty else 0
        brake_avg = float(brake_decel.mean()) if not brake_decel.empty else 0
        lift_avg = float(lift_decel.mean()) if not lift_decel.empty else 0
        coast_max = float(coast_decel.max()) if not coast_decel.empty else 0
        brake_max = float(brake_decel.max()) if not brake_decel.empty else 0

        # Engine braking index: coast_avg / brake_avg (higher = more engine braking)
        eb_index = (coast_avg / brake_avg * 100) if brake_avg > 0 else 0

        driver_stats.append(
            {
                "Driver": drv,
                "CoastAvg": coast_avg,
                "BrakeAvg": brake_avg,
                "LiftAvg": lift_avg,
                "CoastMax": coast_max,
                "BrakeMax": brake_max,
                "EBIndex": eb_index,
                "Color": color,
                "LogoB64": _get_team_logo_b64(drv, session),
            }
        )

        # Decel profile by speed bin
        bins = np.arange(80, 360, 20)
        bin_labels = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]

        coast_profile = []
        brake_profile = []
        for i in range(len(bins) - 1):
            spd_mask = (tel["Speed"] >= bins[i]) & (tel["Speed"] < bins[i + 1])
            c_vals = decel[coast_mask & spd_mask].clip(lower=0)
            b_vals = decel[brake_mask & spd_mask].clip(lower=0)
            coast_profile.append(float(c_vals.mean()) if not c_vals.empty else np.nan)
            brake_profile.append(float(b_vals.mean()) if not b_vals.empty else np.nan)

        fig_profiles.add_trace(
            go.Scatter(
                x=bin_labels,
                y=coast_profile,
                mode="lines+markers",
                name=f"{drv} — COAST",
                line=dict(color=color, width=2.5, dash="dot"),
                marker=dict(size=5, symbol="circle"),
                hovertemplate=f"<b>{drv} COAST</b><br>Speed: %{{x:.0f}} km/h<br>Decel: %{{y:.2f}} m/s²<extra></extra>",
            )
        )
        fig_profiles.add_trace(
            go.Scatter(
                x=bin_labels,
                y=brake_profile,
                mode="lines+markers",
                name=f"{drv} — BRAKE",
                line=dict(color=color, width=2.5),
                marker=dict(size=5, symbol="diamond"),
                hovertemplate=f"<b>{drv} BRAKE</b><br>Speed: %{{x:.0f}} km/h<br>Decel: %{{y:.2f}} m/s²<extra></extra>",
            )
        )

    # Stats cards
    cols = st.columns(len(driver_stats))
    for i, d in enumerate(driver_stats):
        eb_color = GREEN if d["EBIndex"] > 15 else (ORANGE if d["EBIndex"] > 8 else RED)
        logo_b64 = d.get("LogoB64", "")
        logo_html = (
            f'<img src="data:image/png;base64,{logo_b64}"'
            ' style="height:22px; max-width:80px; object-fit:contain; opacity:0.85;">'
            if logo_b64 else ""
        )
        with cols[i]:
            st.markdown(
                f"""
<div style="background:#000000; border:1px solid {BORDER}; border-radius:12px; padding:18px;">
  <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; padding-bottom:10px; border-bottom:1px solid {BORDER};">
    <div style="display:flex; align-items:center; gap:8px;">
      <div style="width:4px; height:20px; background:{d['Color']}; border-radius:2px;"></div>
      <span style="font-family:'Geist Mono',monospace; font-size:1rem; color:{d['Color']}; font-weight:700;">{d['Driver']}</span>
    </div>
    {logo_html}
  </div>
  <div style="text-align:center; margin-bottom:14px; padding:12px 8px; background:rgba(255,255,255,0.03); border-radius:8px; border:1px solid rgba(255,255,255,0.06);">
    <div style="font-family:'Geist Mono',monospace; font-size:0.5rem; color:{TEXT_M}; letter-spacing:1px; margin-bottom:2px;">ENGINE BRAKING INDEX</div>
    <div style="font-family:'Geist Mono',monospace; font-size:2.2rem; font-weight:700; color:{eb_color}; line-height:1;">{d['EBIndex']:.1f}<span style="font-size:0.75rem; color:{TEXT_M}; margin-left:2px;">%</span></div>
    <div style="font-family:'Space Grotesk',sans-serif; font-size:0.65rem; color:{TEXT_M}; margin-top:4px;">(Coast decel / Brake decel)</div>
  </div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-family:'Geist Mono',monospace; margin-bottom:6px;">
    <div style="background:rgba(59,130,246,0.08); padding:9px; border-radius:6px; border:1px solid rgba(59,130,246,0.2); text-align:center;">
      <div style="color:{TEXT_M}; font-size:0.5rem; margin-bottom:2px;">COAST AVG</div>
      <div style="color:{BLUE}; font-size:0.9rem; font-weight:700;">{d['CoastAvg']:.2f}<span style="font-size:0.6rem;"> m/s²</span></div>
    </div>
    <div style="background:rgba(239,68,68,0.08); padding:9px; border-radius:6px; border:1px solid rgba(239,68,68,0.2); text-align:center;">
      <div style="color:{TEXT_M}; font-size:0.5rem; margin-bottom:2px;">BRAKE AVG</div>
      <div style="color:{RED}; font-size:0.9rem; font-weight:700;">{d['BrakeAvg']:.2f}<span style="font-size:0.6rem;"> m/s²</span></div>
    </div>
  </div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-family:'Geist Mono',monospace;">
    <div style="background:rgba(255,255,255,0.02); padding:7px; border-radius:5px; border:1px solid rgba(255,255,255,0.05); text-align:center;">
      <div style="color:{TEXT_M}; font-size:0.45rem; opacity:0.7;">COAST PEAK</div>
      <div style="color:rgba(59,130,246,0.75); font-size:0.75rem; font-weight:700;">{d['CoastMax']:.2f}<span style="font-size:0.55rem;"> m/s²</span></div>
    </div>
    <div style="background:rgba(255,255,255,0.02); padding:7px; border-radius:5px; border:1px solid rgba(255,255,255,0.05); text-align:center;">
      <div style="color:{TEXT_M}; font-size:0.45rem; opacity:0.7;">BRAKE PEAK</div>
      <div style="color:rgba(239,68,68,0.75); font-size:0.75rem; font-weight:700;">{d['BrakeMax']:.2f}<span style="font-size:0.55rem;"> m/s²</span></div>
    </div>
  </div>
</div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Stacked comparison bar
    fig_bar = go.Figure()
    labels = ["Coast Avg", "Lift Avg", "Full Brake Avg"]
    for d in driver_stats:
        color = d["Color"]
        fig_bar.add_trace(
            go.Bar(
                x=labels,
                y=[d["CoastAvg"], d["LiftAvg"], d["BrakeAvg"]],
                name=d["Driver"],
                marker_color=color,
                hovertemplate=f"<b>{d['Driver']}</b><br>%{{x}}: %{{y:.3f}} m/s²<extra></extra>",
            )
        )

    apply_plotly_style(fig_bar, "DECELERATION PHASES COMPARISON")
    fig_bar.update_layout(height=320, barmode="group", margin=dict(l=50, r=20, t=60, b=20))
    fig_bar.update_yaxes(title_text="AVG DECELERATION (m/s²)")
    plot_chart(fig_bar, "driver_style_bar")

    # Profile chart
    apply_plotly_style(fig_profiles, "DECELERATION PROFILE BY SPEED (COAST vs BRAKE)")
    fig_profiles.update_layout(height=400, margin=dict(l=50, r=20, t=60, b=20))
    fig_profiles.update_xaxes(title_text="SPEED (KM/H)")
    fig_profiles.update_yaxes(title_text="AVG DECELERATION (m/s²)")
    plot_chart(fig_profiles, "telemetry_profiles")


# ─────────────────────────────────────────────────────────────────────────────
# Main render entry point
# ─────────────────────────────────────────────────────────────────────────────

def render(session, drivers):
    """Render all Advanced Analytics tabs."""
    if not drivers:
        st.info("Seleziona almeno un pilota per visualizzare le analisi avanzate.")
        return

    tab_cons, tab_weather, tab_usos, tab_eb = st.tabs([
        "CONSISTENCY SCORE",
        "WEATHER IMPACT",
        "UNDERSTEER / OVERSTEER",
        "ENGINE BRAKING",
    ])

    with tab_cons:
        render_consistency_score(session, drivers)

    with tab_weather:
        render_weather_impact(session, drivers)

    with tab_usos:
        render_understeer_oversteer(session, drivers)

    with tab_eb:
        render_engine_braking(session, drivers)
