import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plotting import get_driver_color, apply_plotly_style, get_team_color, get_comparison_colors
from utils.formatting import fmt_time
from utils.components import plot_chart
import warnings
import base64
import os
from utils.session_store import get_cached_laps
from modules import advanced_analytics as _adv_analytics

warnings.filterwarnings("ignore")

BG_CARD = "#060608"
BORDER = "rgba(255,255,255,0.07)"
TEXT_M = "#a1a1aa" 
TEXT_W = "#ffffff" 

def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"

def get_team_logo_b64(team_name, default_icon):
    team_mapping = {
        "MCLAREN": "MCLAREN.png", "RED BULL RACING": "RED BULL RACING.png",
        "FERRARI": "FERRARI.png", "MERCEDES": "MERCEDES.png", "RACING BULLS": "RB.png",
        "AUDI": "AUDI.png", "ALPINE": "ALPINE.png", "ASTON MARTIN": "ASTON MARTIN.png",
        "HAAS F1 TEAM": "HAAS.png", "CADILLAC": "CADILLAC.png",
        "KICK SAUBER": "KICK SAUBER.png", "WILLIAMS": "WILLIAMS.png"
    }
    file_name = team_mapping.get(str(team_name).upper())
    if file_name:
        path = os.path.join("logos", file_name)
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode()
                return f'<img src="data:image/png;base64,{b64_string}" style="height: 24px; margin-right: 10px; object-fit: contain;">'
    return f'<i class="fa-solid {default_icon}" style="font-size: 1.1rem; margin-right: 10px; color: {TEXT_M};"></i>'

def _bar(label, val, bar_color):
    icon = "fa-gas-pump" if "Throttle" in label else "fa-shoe-prints" if "Braking" in label else "fa-road" if "Cornering" in label else "fa-arrows-split-up"
    return f"""
<div style="margin-bottom: 8px;">
    <div style="display:flex; justify-content:space-between; font-size:0.7rem; margin-bottom:4px; font-family:'Geist Mono', monospace;">
        <span style="color:{TEXT_M}; text-transform:uppercase; font-weight:500;"><i class="fa-solid {icon}" style="margin-right:6px;"></i> {label}</span>
        <span style="color:{TEXT_W}; font-weight:500;">{val:.1f}%</span>
    </div>
    <div style="height:3px; background:transparent; border-radius:3px; overflow:hidden;">
        <div style="height:100%; width:{val}%; background: linear-gradient(90deg, transparent 0%, {bar_color}55 18%, {bar_color} 100%); box-shadow: 0 0 6px {bar_color}55; border-radius: 3px;"></div>
    </div>
</div>"""

def estimate_brake_pressure(tel):
    try:
        dt = tel['Time'].dt.total_seconds().diff().fillna(0.001).replace(0, 0.001)
        v_ms = tel['Speed'] / 3.6
        accel = v_ms.diff() / dt
        drag_decel = 0.0008 * (tel['Speed']**2)
        pressure = (-accel - drag_decel).clip(lower=0)
        p_max = pressure.max()
        if p_max > 0:
            pressure = (pressure / p_max) * 100
        return pressure * (tel['Brake'] > 0)
    except Exception:
        return pd.Series(0, index=tel.index)

def calculate_advanced_metrics(tel, glat_smooth_window=10):
    if tel.empty: return {}
    
    try:
        cornering = tel[(tel['Throttle'] < 95) & (tel['Speed'] > 45)]
        ls = cornering[cornering['Speed'] < 125]['Speed'].mean() or 0
        ms = cornering[(cornering['Speed'] >= 125) & (cornering['Speed'] < 210)]['Speed'].mean() or 0
        hs = cornering[cornering['Speed'] >= 210]['Speed'].mean() or 0
        
        total_len = len(tel)
        full_throttle = (len(tel[tel['Throttle'] >= 99]) / total_len) * 100
        partial_throttle = (len(tel[(tel['Throttle'] > 0) & (tel['Throttle'] < 99)]) / total_len) * 100
        coasting = (len(tel[(tel['Throttle'] == 0) & (tel['Brake'] == 0)]) / total_len) * 100
        time_on_brakes = (len(tel[tel['Brake'] > 0]) / total_len) * 100 if 'Brake' in tel else 0
        
        max_speed = tel['Speed'].max() if 'Speed' in tel else 0
        vmax_time = (len(tel[tel['Speed'] >= (max_speed * 0.98)]) / total_len) * 100 if max_speed > 0 else 0
        gear_shifts = (tel['nGear'].diff().abs().sum() / 2) if 'nGear' in tel else 0
        avg_gear = tel['nGear'].mean() if 'nGear' in tel else 0
        max_rpm = tel['RPM'].max() if 'RPM' in tel else 0
        rev_limiter = (len(tel[tel['RPM'] >= (max_rpm * 0.98)]) / total_len) * 100 if max_rpm > 0 else 0
        drs_pct = (len(tel[tel['DRS'] >= 10]) / total_len) * 100 if 'DRS' in tel else 0
        
        corn_pct = (len(cornering) / total_len) * 100
        pd_score = (full_throttle * 0.7) + ((100 - coasting) * 0.3)
        
        dt = tel['Time'].dt.total_seconds().diff().fillna(0.001).replace(0, 0.001)
        v_ms = tel['Speed'] / 3.6
        
        acc_long = v_ms.diff() / dt
        acc_long = acc_long.rolling(3, min_periods=1, center=True).mean() 
        g_long = acc_long / 9.81
        
        tel['G_Long'] = g_long.mask(g_long.abs() > 5.5, np.nan).interpolate(method='linear').fillna(0)
        
        if 'X' in tel.columns and 'Y' in tel.columns:
            dx = tel['X'].diff()
            dy = tel['Y'].diff()
            v_mag = np.sqrt(dx**2 + dy**2).replace(0, 1e-6)
            tx = dx / v_mag
            ty = dy / v_mag
            
            vx = dx / dt
            vy = dy / dt
            vx = vx.rolling(5, min_periods=1, center=True).mean()
            vy = vy.rolling(5, min_periods=1, center=True).mean()
            
            ax = vx.diff() / dt
            ay = vy.diff() / dt
            
            acc_lat = ax * (-ty) + ay * tx
            g_lat_raw = acc_lat / 9.81
            
            g_lat_clean = g_lat_raw.mask(g_lat_raw.abs() > 5.5, np.nan).interpolate(method='linear').fillna(0)
            
            if glat_smooth_window > 1:
                tel['G_Lat'] = g_lat_clean.rolling(glat_smooth_window, min_periods=1, center=True).mean().fillna(0)
            else:
                tel['G_Lat'] = g_lat_clean
        else:
            tel['G_Lat'] = 0.0
            
        max_g_lat = tel['G_Lat'].abs().max()
        max_g_dec = tel['G_Long'].min()
        
        clipping_mask = (tel['Throttle'] >= 99) & (tel['Speed'] > 250) & (tel['G_Long'] <= 0.05)
        clipping_pct = (len(tel[clipping_mask]) / total_len) * 100
        
        brake_rate = tel['Brake'].diff() / dt
        brake_trans = brake_rate[(tel['Brake'] > 0) & (tel['Brake'] < 100)]
        trail_braking_score = brake_trans.abs().mean() if not brake_trans.empty else 0

    except Exception as e:
        return {}
        
    return {
        'LS': ls, 'MS': ms, 'HS': hs, 'ThrottleEff': full_throttle, 'PartialThrottle': partial_throttle,
        'Coasting': coasting, 'TimeOnBrakes': time_on_brakes, 'VmaxTime': vmax_time,
        'PDScore': pd_score, 'CorneringPct': corn_pct, 'GearShifts': gear_shifts,
        'AvgGear': avg_gear, 'MaxRPM': max_rpm, 'RevLimiter': rev_limiter, 'DRSPct': drs_pct,
        'MaxGLat': max_g_lat, 'MaxGDec': max_g_dec, 'ClippingPct': clipping_pct, 'TrailBraking': trail_braking_score
    }

def get_y_title(ch, br_mode):
    titles = {
        'Speed': 'SPEED (KM/H)',
        'Throttle': 'THROTTLE (%)',
        'Brake': 'BRAKE (%)' if br_mode == "Pressure" else 'BRAKE (ON/OFF)',
        'RPM': 'RPM',
        'Gear': 'GEAR',
        'Delta': 'DELTA (S)',
        'G_Long': 'LONGITUDINAL G',
        'G_Lat': 'LATERAL G',
        'ERS_Energy_2026': 'ENERGY (%)',
        'Accel_ms2': 'ACCELERATION (M/S²)',
    }
    return titles.get(ch, ch.upper())


def compute_ers_2026_power_curve(speed_kmh, mode="Standard", base_kw=350):
    v = speed_kmh.astype(float)
    p = np.zeros(len(v), dtype=float)
    if mode == "Override (MOM)":
        v_const, v_zero = 337.0, 355.0
    else:
        v_const, v_zero = 290.0, 355.0

    p[v <= v_const] = float(base_kw)
    fade_mask = (v > v_const) & (v < v_zero)
    p[fade_mask] = float(base_kw) * (1.0 - ((v[fade_mask] - v_const) / (v_zero - v_const)))
    p[v >= v_zero] = 0.0
    return np.clip(p, 0.0, float(base_kw))


def _drs_open_mask(drs_series):
    drs_num = pd.to_numeric(drs_series, errors='coerce')
    if drs_num.notna().any() and drs_num.max() > 1:
        return drs_num >= 10  # FastF1 style: 8 closed, >=10 active
    return drs_num.fillna(0) > 0


def add_ers_2026_channels(tel, base_kw=350, team_name=""):
    speed = pd.to_numeric(tel.get('Speed', pd.Series(0, index=tel.index)), errors='coerce').fillna(0)
    throttle = pd.to_numeric(tel.get('Throttle', pd.Series(0, index=tel.index)), errors='coerce').fillna(0).clip(0, 100)
    brake_raw = tel.get('Brake', pd.Series(0, index=tel.index))
    brake_num = pd.to_numeric(brake_raw, errors='coerce')
    brake_bool = brake_raw.astype(bool) if str(brake_raw.dtype) == 'bool' else (brake_num.fillna(0) > 0)
    drs_open = _drs_open_mask(tel.get('DRS', pd.Series(0, index=tel.index)))
    rpm = pd.to_numeric(tel.get('RPM', pd.Series(0, index=tel.index)), errors='coerce').fillna(0)
    gear = pd.to_numeric(tel.get('nGear', pd.Series(0, index=tel.index)), errors='coerce').fillna(0)

    dt = tel['Time'].dt.total_seconds().diff().fillna(0.02).clip(lower=0.001, upper=0.5)
    accel = (speed.diff().fillna(0) / 3.6) / dt  # m/s^2
    gear_delta = gear.diff().fillna(0)
    rpm_norm = np.clip((rpm - 8000.0) / 7000.0, 0.0, 1.0)

    std_curve_kw = compute_ers_2026_power_curve(speed, mode="Standard", base_kw=base_kw)
    mom_curve_kw = compute_ers_2026_power_curve(speed, mode="Override (MOM)", base_kw=base_kw)

    # Infer override-like phases from combined telemetry context.
    override_mask = (
        (throttle > 92) &
        (~brake_bool) &
        (speed > 220) &
        (drs_open | (accel > 0.4))
    )
    deploy_curve_kw = np.where(override_mask, mom_curve_kw, std_curve_kw)

    g_lat = pd.to_numeric(tel.get('G_Lat', pd.Series(0, index=tel.index)), errors='coerce').fillna(0).abs()
    deploy_mask = (throttle > 55) & (~brake_bool) & ((accel > 0.15) | ((speed > 215) & drs_open))
    corner_penalty = np.clip((g_lat - 2.2) / 2.0, 0.0, 0.45)
    deploy_base = deploy_curve_kw * np.clip((throttle - 40.0) / 60.0, 0.0, 1.0) * (1.0 - corner_penalty)
    deploy_raw = np.where(deploy_mask, deploy_base, 0.0)

    # Recovery from braking and from lift/decel phases.
    lift_recovery_mask = (~brake_bool) & (throttle < 12) & (speed > 100) & (accel < -0.6)
    speed_factor = np.clip(speed / 320.0, 0.2, 1.0)
    rec_brake = np.where(brake_bool, (base_kw * 0.52) * speed_factor, 0.0)
    rec_lift = np.where(lift_recovery_mask, (base_kw * 0.19) * speed_factor, 0.0)
    rec_team = np.zeros(len(tel), dtype=float)

    team_u = str(team_name).upper()
    # Team-engine calibrated heuristics (2026-style behavior).
    if "MERCEDES" in team_u:
        rpm_peak_recovery = (rpm_norm ** 1.8) * (base_kw * 0.18)
        rpm_peak_mask = (rpm > 12800) & (throttle < 35) & (~brake_bool) & (speed > 180)
        rec_team = np.where(rpm_peak_mask, rpm_peak_recovery, 0.0)

        # High-speed corner rpm "hiccups": short alternating pulses in ERS behavior.
        hs_corner_mask = (speed > 220) & (g_lat > 2.4) & (rpm > 12500) & (~brake_bool) & (throttle.between(25, 78))
        phase = np.cumsum(dt.values) * 11.0
        pulse = (np.sin(phase) > 0.45).astype(float)
        rec_team = rec_team + np.where(hs_corner_mask, pulse * (base_kw * 0.06), 0.0)
        deploy_raw = np.where(hs_corner_mask, deploy_raw * (1.0 - 0.12 * pulse), deploy_raw)
    elif "RED BULL" in team_u or "RBPT" in team_u or "FORD" in team_u:
        aggressive_downshift_mask = brake_bool & (gear_delta <= -1) & (speed > 120)
        downshift_intensity = np.clip((-gear_delta) / 2.0, 0.0, 1.5)
        rec_team = np.where(aggressive_downshift_mask, (base_kw * 0.22) * downshift_intensity * speed_factor, 0.0)
    elif "FERRARI" in team_u:
        low_gear_coast_mask = (~brake_bool) & (throttle < 14) & (gear <= 4) & (speed > 85)
        low_gear_factor = np.clip((5.0 - gear) / 4.0, 0.0, 1.0)
        rec_team = np.where(low_gear_coast_mask, (base_kw * 0.16) * low_gear_factor, 0.0)

    recovery_raw = rec_brake + rec_lift + rec_team

    # Single energy trace (battery-like state) for a unified chart.
    cap_kj = 4400.0
    deploy_eff = 0.97
    rec_eff = 0.75
    max_drop_rate = 2.9  # % per second
    max_rise_rate = 2.2  # % per second

    deploy_eff_kw = np.zeros(len(tel), dtype=float)
    rec_eff_kw = np.zeros(len(tel), dtype=float)
    energy = np.zeros(len(tel), dtype=float)
    energy[0] = 78.0

    for i in range(1, len(tel)):
        soc = energy[i-1]
        dep_soc_factor = np.clip((soc - 10.0) / 52.0, 0.16, 1.0)
        rec_soc_factor = np.clip((100.0 - soc) / 68.0, 0.30, 1.0)
        deploy_eff_kw[i] = deploy_raw[i] * dep_soc_factor
        rec_eff_kw[i] = recovery_raw[i] * rec_soc_factor

        delta_pct = (((rec_eff_kw[i] * rec_eff) - (deploy_eff_kw[i] / deploy_eff)) * dt.iloc[i] / cap_kj) * 100.0
        delta_pct = np.clip(delta_pct, -max_drop_rate * dt.iloc[i], max_rise_rate * dt.iloc[i])
        energy[i] = np.clip(soc + delta_pct, 8.0, 96.0)

    tel['ERS_Deploy_2026'] = pd.Series(deploy_eff_kw, index=tel.index).rolling(2, min_periods=1).mean()
    tel['ERS_Recovery_2026'] = pd.Series(rec_eff_kw, index=tel.index).rolling(2, min_periods=1).mean()
    tel['ERS_Energy_2026'] = pd.Series(energy, index=tel.index).rolling(4, min_periods=1).mean()
    return tel

def render_standard_card(d, best_s, best_lap, session):
    team_c = get_team_color(d['Team'], session)
    logo_html = get_team_logo_b64(d['Team'], "fa-user-astronaut")
    # Von Restorff: best sectors get isolation class (stands out from plain white)
    s_classes = ["best-cell" if d[f'S{i}'] == best_s[i-1] else "" for i in range(1, 4)]

    gap = d['ActualLap'] - best_lap
    is_fastest = gap <= 0.001
    gap_str = "FASTEST" if is_fastest else f"+{gap:.3f}s"
    gap_style = "color: #c084fc; text-shadow: 0 0 15px rgba(192, 132, 252, 0.7);" if is_fastest else "color: #ffffff;"
    # Von Restorff: fastest driver card gets green top-bar + subtle glow
    card_extra_class = "vr-highlight" if is_fastest else ""
    
    compound = str(d.get('Compound', 'UNKNOWN')).upper()
    tyre_life = d.get('TyreLife', 1)
    if pd.isna(tyre_life): tyre_life = 1
    
    life_str = "NEW" if tyre_life <= 3 else f"{int(tyre_life)} LAPS"
    c_map = {"SOFT": "#FF3333", "MEDIUM": "#FFDD57", "HARD": "#F0F0F0", "INTERMEDIATE": "#39B54A", "WET": "#1E90FF"}
    tyre_color = c_map.get(compound, "#808080")

    return f"""<div class="driver-card {card_extra_class}" style="--team-color: {_hex_to_rgb(team_c)}; font-family: 'Space Grotesk', sans-serif; border-color: rgba({_hex_to_rgb(team_c)}, 0.3);">
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 15px;">
        <div style="display: flex; align-items: center;">
            <div style="width: 4px; height: 24px; background-color: {team_c}; border-radius: 2px; margin-right: 12px;"></div>
            {logo_html}
            <div style="font-size: 1.15rem; font-weight: 600; color: {team_c};">{d['Driver']} <span style="font-size: 0.7rem; color: {TEXT_M}; font-family: 'Geist Mono', monospace;">{d['Team'].upper()}</span></div>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="display: flex; align-items: center; padding: 4px 8px;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background-color: {tyre_color}; margin-right: 6px; box-shadow: 0 0 6px {tyre_color}88;"></div>
                <span style="color: {TEXT_W}; font-size: 0.65rem; font-family: 'Geist Mono', monospace; font-weight: 700;">{compound[0] if compound != 'UNKNOWN' else 'U'} <span style="color: {TEXT_M};">{life_str}</span></span>
            </div>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; background: transparent; padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 15px;">
        <div style="text-align: center;"><div style="color: {TEXT_M}; font-family: 'Geist Mono', monospace; font-size: 0.6rem;">ACTUAL</div><div style="font-size: 1.1rem; font-weight: 700; color: {TEXT_W}; font-family: 'Geist Mono', monospace;">{fmt_time(d['ActualLap'])}</div></div>
        <div style="text-align: center; border-left: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.08);"><div style="color: {TEXT_M}; font-family: 'Geist Mono', monospace; font-size: 0.6rem;">GAP</div><div style="font-size: 1.1rem; font-weight: 700; {gap_style} font-family: 'Geist Mono', monospace;">{gap_str}</div></div>
        <div style="text-align: center;"><div style="color: {TEXT_M}; font-family: 'Geist Mono', monospace; font-size: 0.6rem;">IDEAL</div><div style="font-size: 1.1rem; font-weight: 700; color: #21C55E; font-family: 'Geist Mono', monospace;">{fmt_time(d['IdealLap'])}</div></div>
    </div>
    <div style="display: flex; justify-content: space-between; gap: 6px; margin-bottom: 15px;">
        <div style="flex:1; text-align:center; padding:6px 0;"><div style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace;">S1</div><div class="{s_classes[0]}" style="font-size:0.9rem; font-weight:700; font-family:'Geist Mono', monospace;">{d['S1']:.3f}</div></div>
        <div style="flex:1; text-align:center; padding:6px 0; border-left: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.08);"><div style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace;">S2</div><div class="{s_classes[1]}" style="font-size:0.9rem; font-weight:700; font-family:'Geist Mono', monospace;">{d['S2']:.3f}</div></div>
        <div style="flex:1; text-align:center; padding:6px 0;"><div style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace;">S3</div><div class="{s_classes[2]}" style="font-size:0.9rem; font-weight:700; font-family:'Geist Mono', monospace;">{d['S3']:.3f}</div></div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 0; padding: 12px 2px; border-bottom: 1px solid rgba(255,255,255,0.08);">
        <div><div style="color:{TEXT_M}; font-size:0.6rem; font-family:'Geist Mono', monospace;">TOP SPEED</div><div style="font-size:1.3rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d['TopSpeed']:.0f}<span style="font-size:0.7rem; color:{TEXT_M};"> KM/H</span></div></div>
        <div style="text-align:right;"><div style="color:{TEXT_M}; font-size:0.6rem; font-family:'Geist Mono', monospace;">AVG SPEED</div><div style="font-size:1.3rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d['AvgSpeed']:.0f}<span style="font-size:0.7rem; color:{TEXT_M};"> KM/H</span></div></div>
    </div>
    <div style="padding-top: 12px;">
    {_bar("Full Throttle", d.get('ThrottleEff',0), team_c)}
    {_bar("Braking", d.get('TimeOnBrakes',0), team_c)}
    {_bar("Cornering", d.get('CorneringPct',0), team_c)}
    </div>
</div>"""

def render_advanced_card(d, b_adv, session):
    team_c = get_team_color(d['Team'], session)
    logo_html = get_team_logo_b64(d['Team'], "fa-microchip")
    def g_style(k, v): return "color: #21C55E; text-shadow: 0 0 10px rgba(33,197,94,0.5);" if v >= b_adv.get(k, 0) and v > 0 else "color: #ffffff;"

    return f"""<div class="driver-card" style="--team-color: {_hex_to_rgb(team_c)}; font-family: 'Space Grotesk', sans-serif; border-color: rgba({_hex_to_rgb(team_c)}, 0.3);">
    <div style="display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 15px;">
        <div style="width: 4px; height: 24px; background-color: {team_c}; border-radius: 2px; margin-right: 12px;"></div>
        {logo_html}
        <div style="font-size: 1.1rem; font-weight: 600; color: {team_c}; font-family: 'Space Grotesk', sans-serif;">{d['Driver']} <span style="font-size: 0.7rem; color: {TEXT_M}; font-family: 'Geist Mono', monospace; font-weight: 500;">DYNAMICS</span></div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 14px; margin-bottom: 14px;">
        <div style="text-align: center; padding: 8px 0; border-right: 1px solid rgba(255,255,255,0.08);"><div style="color: {TEXT_M}; font-size: 0.55rem; font-family: 'Geist Mono', monospace; letter-spacing: 1px; margin-bottom: 4px;">POWER DELIVERY</div><div style="font-size: 1.5rem; font-weight: 700; color: {TEXT_W}; font-family: 'Geist Mono', monospace;">{d.get('PDScore', 0):.0f}<span style="font-size: 0.7rem; color: {TEXT_M};">/100</span></div></div>
        <div style="text-align: center; padding: 8px 0;"><div style="color: {TEXT_M}; font-size: 0.55rem; font-family: 'Geist Mono', monospace; letter-spacing: 1px; margin-bottom: 4px;">DRS USAGE</div><div style="font-size: 1.5rem; font-weight: 700; {g_style('DRSPct', d.get('DRSPct',0))} font-family: 'Geist Mono', monospace;">{d.get('DRSPct', 0):.1f}<span style="font-size: 0.7rem; color: {TEXT_M};">%</span></div></div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 14px; margin-bottom: 14px;">
        <div style="text-align: center; padding: 6px 0;"><div style="color:{TEXT_M}; font-size:0.5rem; font-family:'Geist Mono', monospace; letter-spacing:1px; margin-bottom:3px;">LOW AVG</div><div style="font-size:0.85rem; font-weight:700; {g_style('LS', d.get('LS',0))} font-family:'Geist Mono', monospace;">{d.get('LS',0):.0f}</div></div>
        <div style="text-align: center; padding: 6px 0; border-left: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.08);"><div style="color:{TEXT_M}; font-size:0.5rem; font-family:'Geist Mono', monospace; letter-spacing:1px; margin-bottom:3px;">MED AVG</div><div style="font-size:0.85rem; font-weight:700; {g_style('MS', d.get('MS',0))} font-family:'Geist Mono', monospace;">{d.get('MS',0):.0f}</div></div>
        <div style="text-align: center; padding: 6px 0;"><div style="color:{TEXT_M}; font-size:0.5rem; font-family:'Geist Mono', monospace; letter-spacing:1px; margin-bottom:3px;">HIGH AVG</div><div style="font-size:0.85rem; font-weight:700; {g_style('HS', d.get('HS',0))} font-family:'Geist Mono', monospace;">{d.get('HS',0):.0f}</div></div>
    </div>
    <div style="border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 14px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; padding: 5px 2px;"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">GEAR SHIFTS</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('GearShifts',0):.0f}</span></div>
        <div style="display: flex; justify-content: space-between; padding: 5px 2px; border-top: 1px solid rgba(255,255,255,0.05);"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">MAX LATERAL G</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('MaxGLat',0):.2f} G</span></div>
        <div style="display: flex; justify-content: space-between; padding: 5px 2px; border-top: 1px solid rgba(255,255,255,0.05);"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">MAX DECEL G</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('MaxGDec',0):.2f} G</span></div>
        <div style="display: flex; justify-content: space-between; padding: 5px 2px; border-top: 1px solid rgba(255,255,255,0.05);"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">TIME ON BRAKES</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('TimeOnBrakes',0):.1f}%</span></div>
    </div>
    <div>
        <div style="display: flex; justify-content: space-between; padding: 5px 2px;"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">ERS CLIPPING</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('ClippingPct',0):.1f}%</span></div>
        <div style="display: flex; justify-content: space-between; padding: 5px 2px; border-top: 1px solid rgba(255,255,255,0.05);"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">VMAX TIME</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('VmaxTime',0):.1f}%</span></div>
        <div style="display: flex; justify-content: space-between; padding: 5px 2px; border-top: 1px solid rgba(255,255,255,0.05);"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">REV LIMITER</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('RevLimiter',0):.1f}%</span></div>
        <div style="display: flex; justify-content: space-between; padding: 5px 2px; border-top: 1px solid rgba(255,255,255,0.05);"><span style="color:{TEXT_M}; font-size:0.55rem; font-family:'Geist Mono', monospace; letter-spacing:1px;">PEDAL RATE (TRAIL)</span><span style="font-size:0.82rem; font-weight:700; color:{TEXT_W}; font-family:'Geist Mono', monospace;">{d.get('TrailBraking',0):.0f} /s</span></div>
    </div>
</div>"""

def compute_downforce_contribution(df):
    required = {"Speed", "LatG", "LongG", "Throttle", "Brake", "Distance", "Driver", "DRS"}
    if df is None or df.empty or not required.issubset(df.columns):
        return pd.DataFrame(columns=["Driver", "MechanicalGrip", "AeroCoefficient", "DownforcePercent"])

    rows = []

    for drv, grp in df.groupby("Driver"):
        drs_col = pd.to_numeric(grp["DRS"], errors="coerce")
        # FastF1 can encode DRS as {8,10,12,14}; 8 means closed/off.
        if drs_col.notna().any() and drs_col.max() > 1:
            drs_closed_mask = drs_col <= 9
        else:
            drs_closed_mask = drs_col.fillna(0) == 0

        brake_num = pd.to_numeric(grp["Brake"], errors="coerce")
        if grp["Brake"].dtype == bool:
            brake_off_mask = ~grp["Brake"]
        else:
            brake_off_mask = brake_num.fillna(1) <= 0

        filt = grp[
            (grp["LatG"].abs() > 1.5) &
            brake_off_mask &
            (grp["Speed"] > 80) &
            drs_closed_mask
        ].dropna(subset=["Speed", "LatG"])

        if len(filt) < 20:
            rows.append({
                "Driver": drv,
                "MechanicalGrip": np.nan,
                "AeroCoefficient": np.nan,
                "DownforcePercent": np.nan
            })
            continue

        x = (filt["Speed"].astype(float) ** 2).values
        y = filt["LatG"].abs().astype(float).values

        # Robust fit on speed bins to reduce noise and avoid negative slopes from outliers.
        fit_df = pd.DataFrame({"x": x, "y": y}).dropna()
        if len(fit_df) >= 40:
            fit_df["bin"] = pd.qcut(fit_df["x"], q=8, duplicates="drop")
            fit_pts = fit_df.groupby("bin", observed=True).agg(x=("x", "median"), y=("y", "median")).dropna()
            x_fit = fit_pts["x"].values if len(fit_pts) >= 4 else fit_df["x"].values
            y_fit = fit_pts["y"].values if len(fit_pts) >= 4 else fit_df["y"].values
        else:
            x_fit = fit_df["x"].values
            y_fit = fit_df["y"].values

        try:
            b, a = np.polyfit(x_fit, y_fit, 1)
            b = float(b)
            # Fallback proxy if linear fit returns a non-physical negative slope.
            if b <= 0:
                q_lo = np.quantile(x_fit, 0.35)
                q_hi = np.quantile(x_fit, 0.85)
                low = fit_df[fit_df["x"] <= q_lo]["y"]
                high = fit_df[fit_df["x"] >= q_hi]["y"]
                dx = q_hi - q_lo
                if dx > 0 and len(low) >= 5 and len(high) >= 5:
                    b_proxy = (float(high.median()) - float(low.median())) / float(dx)
                    b = max(b_proxy, 0.0)
                else:
                    b = 0.0
            rows.append({
                "Driver": drv,
                "MechanicalGrip": float(a),
                "AeroCoefficient": float(b),
                "DownforcePercent": np.nan
            })
        except Exception:
            rows.append({
                "Driver": drv,
                "MechanicalGrip": np.nan,
                "AeroCoefficient": np.nan,
                "DownforcePercent": np.nan
            })

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    max_b = out["AeroCoefficient"].max(skipna=True)
    if pd.notna(max_b) and max_b > 0:
        out["DownforcePercent"] = (out["AeroCoefficient"] / max_b) * 100.0
    else:
        out["DownforcePercent"] = np.nan

    return out.sort_values("DownforcePercent", ascending=False, na_position="last").reset_index(drop=True)


def build_downforce_input_df(session, glat_smooth_window=15, max_laps_per_driver=4):
    points = []
    all_drivers = sorted(session.laps["Driver"].dropna().unique().tolist())
    cols = ["Speed", "G_Lat", "G_Long", "Throttle", "Brake", "Distance", "DRS"]

    for drv in all_drivers:
        try:
            laps = session.laps.pick_drivers(drv).pick_quicklaps().pick_wo_box()
            if laps.empty:
                continue
            sample_laps = laps.nsmallest(min(len(laps), max_laps_per_driver), "LapTime")
            for _, lap in sample_laps.iterrows():
                try:
                    tel = lap.get_telemetry().add_distance()
                    _ = calculate_advanced_metrics(tel, glat_smooth_window=glat_smooth_window)
                    if set(cols).issubset(tel.columns):
                        tmp = tel[cols].copy()
                        tmp["Driver"] = drv
                        tmp = tmp.rename(columns={"G_Lat": "LatG", "G_Long": "LongG"})
                        points.append(tmp)
                except Exception:
                    continue
        except Exception:
            continue

    if not points:
        return pd.DataFrame(columns=["Speed", "LatG", "LongG", "Throttle", "Brake", "Distance", "Driver", "DRS"])
    return pd.concat(points, ignore_index=True)

def render_structural_coach(metrics_data, use_expander=False):
    if len(metrics_data) < 2: return

    if use_expander:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        container = st.expander("AI TELEMETRY DEBRIEF", expanded=False)
    else:
        st.markdown("""
        <div style="display:flex; align-items:center; margin-top: 30px; margin-bottom: 15px;">
            <i class="fa-solid fa-satellite-dish" style="color: #21C55E; font-size: 1.4rem; margin-right: 12px;"></i>
            <h3 style="margin: 0; color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 1.2rem; text-transform: uppercase;">TELEMETRY DEBRIEF STRUTTURATO</h3>
        </div>
        """, unsafe_allow_html=True)
        container = st

    # Ordinamento principale per tempo sul giro
    m_sorted = sorted(metrics_data, key=lambda x: x['ActualLap'])
    leader = m_sorted[0]
    
    # 1. ANALISI DEL PASSO (OVERVIEW)
    overview_html = f"<b>{leader['Driver']}</b> detta il benchmark assoluto della sessione. I distacchi del gruppo: "
    gaps = [f"<b>{d['Driver']}</b> (+{(d['ActualLap'] - leader['ActualLap']):.3f}s)" for d in m_sorted[1:]]
    overview_html += ", ".join(gaps) + "."

    # 2. AERO DRAG E TOP SPEED
    spd_sorted = sorted(metrics_data, key=lambda x: x['TopSpeed'], reverse=True)
    vmax_drv = spd_sorted[0]
    vmin_drv = spd_sorted[-1]
    
    aero_text = f"<b>{vmax_drv['Driver']}</b> esprime l'assetto aerodinamico più efficiente (o la mappatura ICE più aggressiva in alto), dominando le speed trap con una punta massima di <b>{vmax_drv['TopSpeed']:.1f} km/h</b>. "
    
    if len(spd_sorted) > 2:
        mid_drivers = spd_sorted[1:-1]
        mid_str = ", ".join([f"<b>{d['Driver']}</b> ({d['TopSpeed']:.1f} km/h)" for d in mid_drivers])
        aero_text += f"Nel gruppo di mezzo si posizionano {mid_str}. "
        
    aero_text += f"All'estremo opposto troviamo <b>{vmin_drv['Driver']}</b>, che risulta il più limitato dal drag (<b>{vmin_drv['TopSpeed']:.1f} km/h</b>), un dato che certifica la chiara scelta verso un setup ad alto carico verticale, necessario per estrarre downforce extra nelle sezioni più guidate del tracciato."

    # 3. KINEMATICS E FRENATA (BRAKING & ENTRY)
    gdec_sorted = sorted(metrics_data, key=lambda x: abs(x['MaxGDec']), reverse=True)
    trail_sorted = sorted(metrics_data, key=lambda x: x['TrailBraking'], reverse=True)
    
    brake_text = f"Analizzando l'asse longitudinale, <b>{gdec_sorted[0]['Driver']}</b> aggredisce la fase di staccata in modo profondamente brutale, generando un vero e proprio muro di decelerazione pari a <b>{abs(gdec_sorted[0]['MaxGDec']):.2f}G</b> per spigolare l'ingresso. "
    
    if trail_sorted[0]['Driver'] != gdec_sorted[0]['Driver']:
        brake_text += f"Tuttavia, la telemetria premia <b>{trail_sorted[0]['Driver']}</b> per il miglior bilanciamento del veicolo: possiede il trail-braking più raffinato del lotto (rilascio modulato a <b>{trail_sorted[0]['TrailBraking']:.0f}/s</b>). Questa gestione chirurgica del trasferimento di carico sull'anteriore permette di saturare l'aderenza laterale (<b>{trail_sorted[0]['MaxGLat']:.2f}G</b>). "
    else:
        brake_text += f"Oltre a staccare più a fondo di tutti, <b>{trail_sorted[0]['Driver']}</b> unisce a questa violenza longitudinale anche la miglior tecnica di trail-braking del gruppo (rilascio a <b>{trail_sorted[0]['TrailBraking']:.0f}/s</b>), massimizzando il grip combinato degli pneumatici anteriori verso l'apice. "
        
    if len(m_sorted) > 2:
        alt_brake = [d for d in m_sorted if d['Driver'] not in [gdec_sorted[0]['Driver'], trail_sorted[0]['Driver']]]
        if alt_brake:
            alt_str = ", ".join([f"<b>{d['Driver']}</b>" for d in alt_brake])
            brake_text += f"Rispetto ai leader di questa metrica, piloti come {alt_str} mostrano transizioni più blande sul pedale del freno o picchi di G negativi inferiori, sacrificando potenziale di rotazione pur di non innescare il bloccaggio."

    # 4. TRACTION, POWER DELIVERY E IBRIDO
    wot_sorted = sorted(metrics_data, key=lambda x: x['ThrottleEff'], reverse=True)
    part_sorted = sorted(metrics_data, key=lambda x: x['PartialThrottle'], reverse=True)
    clip_sorted = sorted(metrics_data, key=lambda x: x['ClippingPct'])
    
    ers_text = f"In fase di uscita, <b>{wot_sorted[0]['Driver']}</b> vanta il Power Delivery più distruttivo: estrae il 100% dell'aderenza meccanica posteriore, raggiungendo il WOT (Wide Open Throttle) in largo anticipo e mantenendolo per il <b>{wot_sorted[0]['ThrottleEff']:.1f}%</b> dell'intero giro. "
    
    if part_sorted[0]['Driver'] != wot_sorted[0]['Driver']:
        ers_text += f"Profonda crisi di trazione, invece, per <b>{part_sorted[0]['Driver']}</b>, che per evitare l'innesco di micro-slip o snap di sovrasterzo è costretto a lottare col pedale, parzializzando l'erogazione (Partial Throttle) per un impressionante <b>{part_sorted[0]['PartialThrottle']:.1f}%</b> del tempo. "
        
    if len(wot_sorted) > 2:
        mid_wot = [d for d in wot_sorted if d['Driver'] not in [wot_sorted[0]['Driver'], part_sorted[0]['Driver']]]
        if mid_wot:
            mid_str = ", ".join([f"<b>{d['Driver']}</b> ({d['ThrottleEff']:.1f}% Full Throttle)" for d in mid_wot])
            ers_text += f"Valori di trazione intermedi registrati per {mid_str}. "

    ers_text += f"<br><br><span style='color:#a1a1aa;'><b>HYBRID DEPLOYMENT:</b></span> Sul fronte dell'efficienza Power Unit, <b>{clip_sorted[0]['Driver']}</b> gestisce al meglio la mappa SOC (clipping irrisorio del <b>{clip_sorted[0]['ClippingPct']:.1f}%</b>). "
    if clip_sorted[-1]['ClippingPct'] > clip_sorted[0]['ClippingPct'] + 2.0:
        ers_text += f"Al contrario, <b>{clip_sorted[-1]['Driver']}</b> soffre un deficit elettrico evidente, tagliando bruscamente la potenza a fine dritto (<b>{clip_sorted[-1]['ClippingPct']:.1f}%</b> di Clipping ERS), disperdendo preziosi centesimi sul dritto."

    # 5. ENERGY TRACE INSIGHTS
    e_valid = [d for d in metrics_data if pd.notna(d.get('EnergyDelta', np.nan))]
    energy_text = ""
    if e_valid:
        best_cons = sorted(e_valid, key=lambda x: x.get('EnergyDelta', 0), reverse=True)[0]
        best_rec = sorted(e_valid, key=lambda x: x.get('EnergyRecoveryPeak', 0), reverse=True)[0]
        best_dep = sorted(e_valid, key=lambda x: x.get('EnergyDeployPeak', 0), reverse=True)[0]
        energy_text = (
            f"La traccia <b>ENERGY %</b> mostra il SOC stimato giro dopo giro: scende in deployment e risale in recupero. "
            f"<b>{best_cons['Driver']}</b> chiude il giro con il miglior bilancio netto ({best_cons.get('EnergyDelta', 0):+.1f}%), "
            f"mentre <b>{best_rec['Driver']}</b> registra il picco di ricarica più alto ({best_rec.get('EnergyRecoveryPeak', 0):.0f} kW). "
            f"In uscita curva/dritto, <b>{best_dep['Driver']}</b> è quello col picco deployment più aggressivo ({best_dep.get('EnergyDeployPeak', 0):.0f} kW)."
        )
    else:
        energy_text = "Dati ENERGY % insufficienti per la debrief automatica in questa sessione."

    # RENDER HTML
    html_card = f"""
    <div style="background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
        <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 1.05rem; line-height: 1.5; margin: 0;">{overview_html}</p>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); padding: 20px; border-radius: 8px;">
                <h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 0.95rem; margin-top: 0; margin-bottom: 12px;"><i class="fa-solid fa-wind" style="color: #71717a; margin-right: 8px;"></i> AERO DRAG & TOP SPEED</h4>
                <p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin: 0;">{aero_text}</p>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); padding: 20px; border-radius: 8px;">
                <h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 0.95rem; margin-top: 0; margin-bottom: 12px;"><i class="fa-solid fa-arrows-down-to-line" style="color: #71717a; margin-right: 8px;"></i> KINEMATICS & TRAIL-BRAKING</h4>
                <p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin: 0;">{brake_text}</p>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); padding: 20px; border-radius: 8px;">
                <h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 0.95rem; margin-top: 0; margin-bottom: 12px;"><i class="fa-solid fa-bolt" style="color: #71717a; margin-right: 8px;"></i> TRACTION & PU DEPLOYMENT</h4>
                <p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin: 0;">{ers_text}</p>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); padding: 20px; border-radius: 8px;">
                <h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 0.95rem; margin-top: 0; margin-bottom: 12px;"><i class="fa-solid fa-battery-half" style="color: #71717a; margin-right: 8px;"></i> ENERGY TRACE (ERS 2026)</h4>
                <p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin: 0;">{energy_text}</p>
            </div>
        </div>
        <div style="margin-top: 15px; font-size: 0.6rem; color: #71717a; text-align: right; font-family: 'Geist Mono', monospace;">
            GENERATED BY: STRUCTURAL TELEMETRY ENGINE V4 (MULTI-DRIVER ANALYSIS)
        </div>
    </div>
    """
    container.markdown(html_card, unsafe_allow_html=True)


def render(session, drivers):
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:16px;'>"
        f"<i class='fa-solid fa-chart-line' style='color:#3b82f6; font-size:1.3rem; margin-right:10px;'></i>"
        "<h4 style='margin:0; color:#ffffff; font-family:Geist Mono,monospace; font-size:0.95rem;"
        " text-transform:uppercase; letter-spacing:1px;'>PERFORMANCE INSIGHTS</h4></div>",
        unsafe_allow_html=True,
    )
    with st.expander("CONFIGURAZIONE GRAFICI", expanded=False):
        st.markdown("<div style='font-family: Geist Mono; font-size:0.65rem; color:#71717a; margin-top:12px; margin-bottom:12px; letter-spacing: 1px;'>IMPOSTAZIONI TELEMETRIA</div>", unsafe_allow_html=True)
        c_cfg_1, c_cfg_2 = st.columns(2)
        with c_cfg_1:
            chs = st.multiselect(
                "CHANNELS TO DISPLAY",
                ['Delta', 'Speed', 'Throttle', 'Brake', 'RPM', 'Gear', 'Accel_ms2', 'ERS_Energy_2026'],
                default=['Delta', 'Speed', 'Throttle', 'Brake']
            )
            br_mode_toggle = st.toggle("ESTIMATE BRAKE PRESSURE", value=False)
            br_mode = "Pressure" if br_mode_toggle else "On/Off"
            show_apex = st.toggle("SHOW APEX VELOCITY", value=True)
            search_range = st.number_input("APEX SEARCH RANGE (M)", min_value=10, max_value=150, value=50, step=10) if show_apex else 50
            speed_dom = st.toggle("SPEED DOMINANCE COLOR", value=False)
            num_microsectors = st.number_input("MICRO-SECTORS", min_value=20, max_value=500, value=80, step=10) if speed_dom else 80
        with c_cfg_2:
            sep_plots = st.toggle("SINGLE PLOT CAPTURE", value=False)
            st.markdown("<div style='font-family: Geist Mono; font-size:0.65rem; color:#71717a; margin-top:6px; margin-bottom:8px; letter-spacing: 1px;'>SMOOTHING FILTERS</div>", unsafe_allow_html=True)
            glat_smooth = st.number_input("LATERAL G SMOOTHING WINDOW", min_value=1, max_value=100, value=15, step=1)
            st.markdown("<div style='font-family: Geist Mono; font-size:0.65rem; color:#71717a; margin-top:6px; margin-bottom:8px; letter-spacing: 1px;'>ERS 2026 MODEL</div>", unsafe_allow_html=True)
            ers_base_kw = st.selectbox("BASE DEPLOYMENT POWER (kW)", [350, 300, 250], index=0)
            ai_debrief_expander = st.toggle("AI DEBRIEF IN EXPANDER", value=True)

    if not drivers: return
    
    metrics_data, laps_cache = [], {}
    circuit_info = None
    try:
        circuit_info = session.get_circuit_info()
    except Exception:
        pass

    _cmp_colors = get_comparison_colors(drivers, session)

    session_key = st.session_state.get("f1_session_key", "unknown")
    base_cache_key = f"{session_key}|base"
    base_cache = st.session_state.setdefault("telemetry_base_cache", {})
    per_session_base_cache = base_cache.setdefault(base_cache_key, {})
    
    with st.spinner("Processing official telemetry..."):
        for drv in drivers:
            try:
                base_driver_data = per_session_base_cache.get(drv)
                if base_driver_data is None:
                    laps = get_cached_laps(session).pick_drivers(drv).pick_quicklaps().pick_wo_box()
                    fast = laps.pick_fastest()
                    if fast is None:
                        continue
                    base_tel = fast.get_telemetry().add_distance()
                    per_session_base_cache[drv] = {
                        "fast": fast,
                        "laps": laps,
                        "base_tel": base_tel,
                        "team": fast["Team"],
                    }
                    base_driver_data = per_session_base_cache[drv]

                fast = base_driver_data["fast"]
                laps = base_driver_data["laps"]
                tel = base_driver_data["base_tel"].copy()
                adv = calculate_advanced_metrics(tel, glat_smooth_window=glat_smooth)
                tel = add_ers_2026_channels(tel, base_kw=int(ers_base_kw), team_name=fast['Team'])
                tel['B_Pressure'] = estimate_brake_pressure(tel)
                # Longitudinal acceleration in m/s², smoothed
                _dt_acc = tel['Time'].dt.total_seconds().diff().fillna(0.02).clip(lower=0.001, upper=0.5)
                _accel_raw = (tel['Speed'].diff().fillna(0) / 3.6) / _dt_acc
                tel['Accel_ms2'] = _accel_raw.rolling(5, min_periods=1, center=True).mean().clip(-50, 50)
                energy_series = pd.to_numeric(tel.get('ERS_Energy_2026', pd.Series(np.nan, index=tel.index)), errors='coerce')
                deploy_series = pd.to_numeric(tel.get('ERS_Deploy_2026', pd.Series(0, index=tel.index)), errors='coerce').fillna(0)
                rec_series = pd.to_numeric(tel.get('ERS_Recovery_2026', pd.Series(0, index=tel.index)), errors='coerce').fillna(0)
                try:
                    w = fast.get_weather_data()
                    air = round(w['AirTemp'], 1) if pd.notna(w['AirTemp']) else 0
                    trk = round(w['TrackTemp'], 1) if pd.notna(w['TrackTemp']) else 0
                except Exception:
                    air, trk = 0, 0

                m_entry = {
                    'Driver': drv, 'Color': _cmp_colors.get(drv, get_driver_color(drv, session)), 'Team': fast['Team'],
                    'ActualLap': fast['LapTime'].total_seconds(),
                    'IdealLap': (laps['Sector1Time'].min() + laps['Sector2Time'].min() + laps['Sector3Time'].min()).total_seconds(),
                    'S1': fast['Sector1Time'].total_seconds(), 'S2': fast['Sector2Time'].total_seconds(), 'S3': fast['Sector3Time'].total_seconds(),
                    'TopSpeed': tel['Speed'].max(), 'AvgSpeed': tel['Speed'].mean(),
                    'Compound': fast['Compound'], 'TyreLife': fast['TyreLife'], 'AirT': air, 'TrackT': trk, 'tel': tel,
                    'EnergyMin': float(energy_series.min()) if energy_series.notna().any() else np.nan,
                    'EnergyMax': float(energy_series.max()) if energy_series.notna().any() else np.nan,
                    'EnergyDelta': float(energy_series.iloc[-1] - energy_series.iloc[0]) if energy_series.notna().any() else np.nan,
                    'EnergyDeployPeak': float(deploy_series.max()),
                    'EnergyRecoveryPeak': float(rec_series.max())
                }
                m_entry.update(adv)
                metrics_data.append(m_entry)
                laps_cache[drv] = {'lap': fast, 'tel': tel, 'color': _cmp_colors.get(drv, get_driver_color(drv, session))}
            except Exception:
                pass

    valid_drivers = [d for d in drivers if d in laps_cache]

    if metrics_data:
        t_stats, t_dyn, t_track = st.tabs(["LAP PERFORMANCE", "ADVANCED DYNAMICS", "TRACK DOMINANCE"])
        
        with t_stats:
            best_s = [min([d[f'S{i}'] for d in metrics_data]) for i in range(1,4)]
            best_lap = min([d['ActualLap'] for d in metrics_data])
            cols = st.columns(len(metrics_data))
            for i, col in enumerate(cols):
                reveal_cls = f"reveal-card rd-{min(i+1, 6)} pop"
                with col:
                    st.markdown(
                        f"<div class='{reveal_cls}'>"
                        + render_standard_card(metrics_data[i], best_s, best_lap, session)
                        + "</div>",
                        unsafe_allow_html=True,
                    )
        
        with t_dyn:
            best_adv = {'LS': max([d.get('LS',0) for d in metrics_data]), 'MS': max([d.get('MS',0) for d in metrics_data]), 'HS': max([d.get('HS',0) for d in metrics_data]), 'DRSPct': max([d.get('DRSPct',0) for d in metrics_data]), 'ThrottleEff': max([d.get('ThrottleEff',0) for d in metrics_data])}
            cols_adv = st.columns(len(metrics_data))
            for i, col in enumerate(cols_adv):
                reveal_cls = f"reveal-card rd-{min(i+1, 6)} pop"
                with col:
                    st.markdown(
                        f"<div class='{reveal_cls}'>"
                        + render_advanced_card(metrics_data[i], best_adv, session)
                        + "</div>",
                        unsafe_allow_html=True,
                    )

            st.markdown("""
            <div style="background-color: rgba(59,130,246,0.06); border: 1px solid rgba(59,130,246,0.2); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 20px; margin: 20px 0 25px 0;">
                <h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; margin-top: 0; margin-bottom: 15px;">
                    <i class="fa-solid fa-graduation-cap" style="color: #3b82f6; margin-right: 10px;"></i> COME LEGGERE IL CERCHIO DELLE ADERENZE (GG DIAGRAM)
                </h4>
                <p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin-bottom: 15px;">
                    Il <b>GG Diagram</b> visualizza graficamente come il pilota sfrutta il limite fisico degli pneumatici. Le gomme hanno una quantita finita di grip (100%). Se usi il 100% dell'aderenza per frenare a ruote dritte, non avrai margine per sterzare. Per essere veloci, i piloti devono combinare le due forze senza superare il limite.
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <ul style="color: #a1a1aa; font-family: 'Space Grotesk', sans-serif; font-size: 0.9rem; padding-left: 20px; margin: 0;">
                            <li style="margin-bottom: 8px;"><b style="color: #ffffff;">Punti Superiori (> 0):</b> Accelerazione pura. Limitata dalla potenza del motore (solitamente max +1.5G / +2G).</li>
                            <li style="margin-bottom: 8px;"><b style="color: #ffffff;">Punti Inferiori (< 0):</b> Decelerazione pura (Frenata). Il carico aerodinamico schiaccia l'auto permettendo staccate fino a -5G o -6G.</li>
                        </ul>
                    </div>
                    <div>
                        <ul style="color: #a1a1aa; font-family: 'Space Grotesk', sans-serif; font-size: 0.9rem; padding-left: 20px; margin: 0;">
                            <li style="margin-bottom: 8px;"><b style="color: #ffffff;">Estremi Laterali (Sinistra/Destra):</b> Pura percorrenza di curva (Forza Centrifuga). Maggiore e il carico aerodinamico, piu le auto spingono fino a 4G o 5G laterali.</li>
                            <li><b style="color: #21C55E;">La forma perfetta ("Trail Braking"):</b> Una forma esterna smussata, a "U" rovesciata, indica che il pilota rilascia il freno con fluidita man mano che aumenta i gradi di sterzo (G laterali), mantenendo la gomma sempre al 100% del suo potenziale in ingresso curva.</li>
                        </ul>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            gg_fig = go.Figure()
            for g in range(1, 7):
                gg_fig.add_shape(type="circle", x0=-g, y0=-g, x1=g, y1=g, line_color="rgba(255,255,255,0.05)", line_width=1, layer="below")
                gg_fig.add_annotation(x=0, y=g, text=f"{g}G", showarrow=False, yshift=10, font=dict(color="rgba(255,255,255,0.3)", size=10, family="Geist Mono"))

            gg_fig.add_hline(y=0, line_color="rgba(255,255,255,0.15)", line_width=1)
            gg_fig.add_vline(x=0, line_color="rgba(255,255,255,0.15)", line_width=1)

            for d in valid_drivers:
                tel = laps_cache[d]['tel']
                df_gg = tel[(tel['G_Lat'] != 0) | (tel['G_Long'] != 0)]
                gg_fig.add_trace(go.Scatter(
                    x=df_gg['G_Lat'],
                    y=df_gg['G_Long'],
                    mode='markers',
                    name=d,
                    marker=dict(color=laps_cache[d]['color'], size=4, opacity=0.4, line=dict(width=0)),
                    hovertemplate=f"<b>{d}</b><br>Lat G: %{{x:.2f}}<br>Long G: %{{y:.2f}}<extra></extra>"
                ))

            gg_fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title="LATERAL G (Cornering)", range=[-6, 6], zeroline=False, showgrid=False, title_font=dict(family="Geist Mono", size=11, color=TEXT_M)),
                yaxis=dict(title="LONGITUDINAL G (Accel/Brake)", range=[-6, 6], scaleanchor="x", scaleratio=1, zeroline=False, showgrid=False, title_font=dict(family="Geist Mono", size=11, color=TEXT_M)),
                margin=dict(l=20, r=20, t=20, b=20),
                height=650,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(family="Geist Mono", color="#ffffff", size=12))
            )
            gg_fig.add_annotation(x=-5.5, y=5.5, text="LEFT TURN + ACCEL", showarrow=False, font=dict(color=TEXT_M, size=10, family="Geist Mono"))
            gg_fig.add_annotation(x=5.5, y=5.5, text="RIGHT TURN + ACCEL", showarrow=False, font=dict(color=TEXT_M, size=10, family="Geist Mono"))
            gg_fig.add_annotation(x=-5.5, y=-5.5, text="LEFT TURN + BRAKING", showarrow=False, font=dict(color=TEXT_M, size=10, family="Geist Mono"))
            gg_fig.add_annotation(x=5.5, y=-5.5, text="RIGHT TURN + BRAKING", showarrow=False, font=dict(color=TEXT_M, size=10, family="Geist Mono"))
            st.markdown(
                "<div class='chart-frame-header reveal-card rd-1'>"
                "<div class='chart-frame-title'><i class='fa-solid fa-circle-dot'></i>GG Diagram — Traction Circle</div>"
                "<div class='chart-frame-meta'><span class='chart-frame-badge'><i class='fa-solid fa-grip'></i>&nbsp;G-FORCE</span></div>"
                "</div>",
                unsafe_allow_html=True,
            )
            plot_chart(apply_plotly_style(gg_fig, ""), "gg_diagram")

            # ── Advanced Analytics ─────────────────────────────────────────
            st.markdown(
                "<div class='reveal-card rd-1'><div class='section-sep'>"
                "<div class='section-sep-icon'><i class='fa-solid fa-cloud-sun'></i></div>"
                "<span class='section-sep-label'>Weather Impact</span>"
                "<div class='section-sep-line'></div>"
                "</div></div>",
                unsafe_allow_html=True,
            )
            _adv_analytics.render_weather_impact(session, drivers)
            st.markdown(
                "<div class='reveal-card rd-1'><div class='section-sep'>"
                "<div class='section-sep-icon'><i class='fa-solid fa-rotate'></i></div>"
                "<span class='section-sep-label'>Understeer / Oversteer</span>"
                "<div class='section-sep-line'></div>"
                "</div></div>",
                unsafe_allow_html=True,
            )
            _adv_analytics.render_understeer_oversteer(session, drivers)
            st.markdown(
                "<div class='reveal-card rd-1'><div class='section-sep'>"
                "<div class='section-sep-icon'><i class='fa-solid fa-fire'></i></div>"
                "<span class='section-sep-label'>Engine Braking</span>"
                "<div class='section-sep-line'></div>"
                "</div></div>",
                unsafe_allow_html=True,
            )
            _adv_analytics.render_engine_braking(session, drivers)

    render_structural_coach(metrics_data, use_expander=ai_debrief_expander)

    st.markdown(
        "<div class='reveal-card rd-1'>"
        "<div class='section-sep'>"
        "<div class='section-sep-icon'><i class='fa-solid fa-map-location-dot'></i></div>"
        "<span class='section-sep-label'>Telemetry Traces</span>"
        "<div class='section-sep-line'></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    s1_dist, s2_dist, dominance_bins, fastest_drivers = None, None, None, None
    
    if valid_drivers:
        ref_d = valid_drivers[0]
        ref_lap = laps_cache[ref_d]['lap']
        ref_tel = laps_cache[ref_d]['tel']
        try:
            s1_dist = ref_tel.loc[ref_tel['SessionTime'] <= ref_lap['Sector1SessionTime'], 'Distance'].max()
            s2_dist = ref_tel.loc[ref_tel['SessionTime'] <= ref_lap['Sector2SessionTime'], 'Distance'].max()
        except Exception:
            pass

        if len(valid_drivers) >= 2 and 'X' in ref_tel.columns and 'Y' in ref_tel.columns:
            max_dist = ref_tel['Distance'].max()
            dominance_bins = np.linspace(0, max_dist, num_microsectors + 1)
            driver_times = {}
            for d in valid_drivers:
                tel = laps_cache[d]['tel']
                times_sec = tel['SessionTime'].dt.total_seconds().values
                dists = tel['Distance'].values
                _, unique_idx = np.unique(dists, return_index=True)
                dists = dists[unique_idx]
                times_sec = times_sec[unique_idx]
                bin_times = np.interp(dominance_bins, dists, times_sec)
                driver_times[d] = np.diff(bin_times)
                
            time_matrix = np.array([driver_times[d] for d in valid_drivers])
            fastest_idx = np.argmin(time_matrix, axis=0)
            fastest_drivers = [valid_drivers[i] for i in fastest_idx]

    if metrics_data:
        with t_track:
            st.markdown(
                "<div style='display:flex; align-items:center; margin-bottom:16px;'>"
                "<i class='fa-solid fa-map-location-dot' style='color:#3b82f6; font-size:1.3rem; margin-right:10px;'></i>"
                "<h3 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:1.1rem;"
                " text-transform:uppercase; letter-spacing:1px;'>TRACK DOMINANCE MAP</h3></div>",
                unsafe_allow_html=True,
            )
            if dominance_bins is not None:
                track_fig = go.Figure()
                ref_x, ref_y, ref_d = ref_tel['X'].values, ref_tel['Y'].values, ref_tel['Distance'].values
                
                track_fig.add_trace(go.Scatter(x=ref_x, y=ref_y, mode='lines', line=dict(color='rgba(255, 255, 255, 0.05)', width=22), hoverinfo='skip', showlegend=False))
                bin_indices = np.clip(np.digitize(ref_d, dominance_bins) - 1, 0, num_microsectors - 1)
                point_winners = np.array(fastest_drivers)[bin_indices]
                
                for d in valid_drivers:
                    mask = (point_winners == d)
                    mask_combined = mask | np.roll(mask, 1)
                    plot_x = np.where(mask_combined, ref_x, np.nan)
                    plot_y = np.where(mask_combined, ref_y, np.nan)
                    track_fig.add_trace(go.Scatter(x=plot_x, y=plot_y, mode='lines', name=d + " shadow", line=dict(color=laps_cache[d]['color'], width=18), opacity=0.45, hoverinfo='skip', showlegend=False))
                    track_fig.add_trace(go.Scatter(x=plot_x, y=plot_y, mode='lines', name=d, line=dict(color=laps_cache[d]['color'], width=5), hovertemplate=f"<b>{d}</b><extra></extra>"))
                
                if circuit_info is not None:
                    track_fig.add_trace(go.Scatter(x=[ref_x[0]], y=[ref_y[0]], mode='markers', marker=dict(symbol='square', size=12, color='#21C55E', line=dict(color='#ffffff', width=2)), hoverinfo='skip', showlegend=False))
                    track_fig.add_annotation(x=ref_x[0], y=ref_y[0], text="<span style='font-weight: 600;'>START/FINISH</span>", showarrow=False, yshift=18, font=dict(color="#21C55E", size=12, family="Geist Mono"))
                    c_x, c_y = circuit_info.corners['X'].tolist(), circuit_info.corners['Y'].tolist()
                    c_num, c_hov = [f"<span style='font-weight: 600;'>{n}</span>" for n in circuit_info.corners['Number']], [f"Turn {n}" for n in circuit_info.corners['Number']]
                    track_fig.add_trace(go.Scatter(x=c_x, y=c_y, mode='text', text=c_num, textposition='middle center', textfont=dict(color="#ffffff", size=16, family="Geist Mono"), hoverinfo='text', hovertext=c_hov, showlegend=False))
                        
                apply_plotly_style(track_fig, "TRACK DOMINANCE MAP")
                track_fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
                    margin=dict(l=10, r=10, t=60, b=10),
                    showlegend=True,
                    height=650,
                    font=dict(family="Geist Mono, monospace", size=12),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=0.03,
                        xanchor="center", x=0.5,
                        font=dict(family="Geist Mono, monospace", color="#ffffff", size=13),
                        bgcolor="rgba(15,15,15,0.85)",
                        bordercolor="rgba(255,255,255,0.15)",
                        borderwidth=1, itemsizing="constant",
                    ),
                )
                st.markdown(
                    "<div class='chart-frame-header reveal-card rd-1'>"
                    "<div class='chart-frame-title'><i class='fa-solid fa-map'></i>Track Dominance Map</div>"
                    "<div class='chart-frame-meta'><span class='chart-frame-badge'><i class='fa-solid fa-road'></i>&nbsp;MICRO-SECTORS</span></div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                plot_chart(track_fig, "track_dominance")
            else:
                st.info("Select at least 2 drivers with valid positional data to generate Dominance Map.")
    if chs and laps_cache:
        def render_energy_trace_logic():
            st.markdown("""
            <div style="background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.2); border-left:4px solid #f59e0b; border-radius:8px; padding:12px 14px; margin-bottom:12px; display:flex; gap:10px; align-items:flex-start;">
                <i class="fa-solid fa-battery-half" style="color:#f59e0b; margin-top:2px;"></i>
                <div style="color:#a1a1aa; font-family:'Space Grotesk', sans-serif; font-size:0.88rem; line-height:1.5;">
                    <span style="color:#ffffff; font-family:'Geist Mono', monospace; font-size:0.78rem; letter-spacing:0.8px; margin-right:8px;">ENERGY TRACE LOGIC</span>
                    SOC stimato 0-100%. Scende in deployment (throttle+accel), sale in recovery (frenata, decel, lift-and-coast). Modello su Speed, Throttle, Brake, DRS, RPM, Gear con profili Mercedes/RB Ford/Ferrari.
                </div>
            </div>
            """, unsafe_allow_html=True)

        if sep_plots:
            energy_logic_rendered = False
            for ch in chs:
                fig = go.Figure()
                minor_dtick = 250 if ch == 'RPM' else (10 if ch == 'Speed' else (0.025 if ch == 'Delta' else (1 if ch == 'Gear' else (5 if ch == 'ERS_Energy_2026' else 5))))
                grid_color = "rgba(255, 255, 255, 0.03)" if (ch == 'Speed' and speed_dom) else "#1a1a1c"
                
                if ch == 'Delta':
                    if len(valid_drivers) >= 2:
                        ref_driver = min(valid_drivers, key=lambda d: laps_cache[d]['lap']['LapTime'])
                        ref_lap = laps_cache[ref_driver]['lap']
                        ref_tel = laps_cache[ref_driver]['tel']
                        fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=np.zeros(len(ref_tel)), name=f"{ref_driver} (REF)", line=dict(color=laps_cache[ref_driver]['color'], width=2, dash='dot'), hovertemplate="%{y:.3f}s"))
                        for target in valid_drivers:
                            if target != ref_driver:
                                delta_t, dt_ref_tel, _ = fastf1.utils.delta_time(ref_lap, laps_cache[target]['lap'])
                                fig.add_trace(go.Scatter(x=dt_ref_tel['Distance'], y=delta_t, name=f"{target} Delta", line=dict(color=laps_cache[target]['color'], width=3.5), fill='tozeroy' if len(valid_drivers) == 2 else 'none', hovertemplate="%{y:.3f}s"))
                    fig.update_yaxes(title_text=get_y_title('Delta', br_mode), title_font=dict(family="Geist Mono", size=11, color=TEXT_M), showgrid=True, gridcolor=grid_color, zeroline=False, minor=dict(ticklen=4, tickmode="linear", tick0=0, dtick=minor_dtick, showgrid=True, gridcolor=grid_color))
                else:
                    for drv in drivers:
                        if drv in laps_cache:
                            t = laps_cache[drv]['tel']
                            if ch == 'Gear': y_val = t['nGear'].astype(int)
                            elif ch == 'Brake' and br_mode == "On/Off": y_val = t['Brake'].astype(int)
                            elif ch == 'Brake' and br_mode == "Pressure": y_val = t['B_Pressure']
                            else: y_val = t[ch] if ch in t.columns else pd.Series(np.zeros(len(t)), index=t.index)
                            fill_mode = 'tozeroy' if (ch == 'Brake' and br_mode == "Pressure") else 'none'
                            htpl = "%{y:.1f}%<extra></extra>" if ch == 'ERS_Energy_2026' else "%{y:.1f}<extra></extra>"
                            fig.add_trace(go.Scatter(x=t['Distance'], y=y_val, name=drv, line=dict(color=laps_cache[drv]['color'], width=2.5 if fill_mode=='tozeroy' else 3.5), fill=fill_mode, hovertemplate=htpl))
                    
                    if ch == 'Speed' and speed_dom and dominance_bins is not None:
                        for i in range(num_microsectors):
                            w_color = laps_cache[fastest_drivers[i]]['color']
                            fig.add_vrect(x0=dominance_bins[i], x1=dominance_bins[i+1], fillcolor=w_color, opacity=0.15, layer="below", line_width=0)

                    fig.update_yaxes(title_text=get_y_title(ch, br_mode), title_font=dict(family="Geist Mono", size=11, color=TEXT_M), showgrid=True, gridcolor=grid_color, zeroline=False, minor=dict(ticklen=4, tickmode="linear", tick0=0, dtick=minor_dtick, showgrid=True, gridcolor=grid_color))
                    if ch == 'Brake' and br_mode == "On/Off": fig.update_yaxes(tickvals=[0, 1], ticktext=["OFF", "ON"], range=[-0.2, 1.2])
                    elif ch == 'Brake' and br_mode == "Pressure": fig.update_yaxes(range=[-5, 105])
                    elif ch == 'RPM': fig.update_yaxes(tickformat=",.0f")
                    elif ch == 'ERS_Energy_2026': fig.update_yaxes(range=[0, 100])

                    if ch == 'Speed' and show_apex and circuit_info is not None:
                        for idx, corner in circuit_info.corners.iterrows():
                            dist, c_num = corner['Distance'], corner['Number']
                            v_list = []
                            for d in drivers:
                                if d in laps_cache:
                                    tel_d = laps_cache[d]['tel']
                                    v_min = tel_d[(tel_d['Distance'] > dist - search_range) & (tel_d['Distance'] < dist + search_range)]['Speed'].min()
                                    v_list.append({'n': d, 'v': v_min, 'c': laps_cache[d]['color']})
                            if v_list:
                                v_list.sort(key=lambda x: x['v'], reverse=True)
                                v_f = v_list[0]
                                apex_html = f"<b style='color:{v_f['c']}; font-size:13px;'>{v_f['n']} {v_f['v']:.0f}</b>"
                                for v_o in v_list[1:]: apex_html += f"<br><b style='color:{v_o['c']}; font-size:13px;'>{v_o['n']} {v_o['v'] - v_f['v']:+.0f}</b>"
                                fig.add_vline(x=dist, line_width=1, line_dash="dot", line_color="#333")
                                fig.add_annotation(x=dist, y=v_f['v'] - 30, text=apex_html, showarrow=False, align="left", font=dict(family="Space Grotesk, sans-serif", size=13))
                                fig.add_trace(go.Scatter(x=[dist], y=[0], mode="text", text=[f"<span style='font-weight: 600;'>T{c_num}</span>"], textfont=dict(family="Geist Mono", size=12, color=TEXT_M), textposition="top center", showlegend=False, hoverinfo="skip"))

                if s1_dist and s2_dist:
                    fig.add_vline(x=s1_dist, line_width=0.8, line_dash="15px 15px", line_color=TEXT_M, opacity=0.6)
                    fig.add_vline(x=s2_dist, line_width=0.8, line_dash="15px 15px", line_color=TEXT_M, opacity=0.6)

                apply_plotly_style(fig, "")
                fig.update_xaxes(hoverformat=".0f m")
                fig.update_layout(height=400, hovermode='x unified', margin=dict(l=50, r=20, t=20, b=20), separators=".,")
                if ch == 'ERS_Energy_2026' and not energy_logic_rendered:
                    render_energy_trace_logic()
                    energy_logic_rendered = True
                plot_chart(fig, "telemetry_overlay", key=f"plot_{ch}", extra_config={'edits': {'annotationPosition': True}})

        else:
            if 'ERS_Energy_2026' in chs:
                render_energy_trace_logic()
            total_rows = len(chs)
            fig = make_subplots(rows=total_rows, cols=1, shared_xaxes=True, vertical_spacing=0.03)
            curr_row = 1

            for ch in chs:
                minor_dtick = 250 if ch == 'RPM' else (10 if ch == 'Speed' else (0.025 if ch == 'Delta' else (1 if ch == 'Gear' else (5 if ch == 'ERS_Energy_2026' else 5))))
                grid_color = "rgba(255, 255, 255, 0.03)" if (ch == 'Speed' and speed_dom) else "#1a1a1c"
                
                if ch == 'Delta':
                    if len(valid_drivers) >= 2:
                        ref_driver = min(valid_drivers, key=lambda d: laps_cache[d]['lap']['LapTime'])
                        ref_lap = laps_cache[ref_driver]['lap']
                        ref_tel = laps_cache[ref_driver]['tel']
                        fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=np.zeros(len(ref_tel)), name=f"{ref_driver} (REF)", legendgroup=ref_driver, line=dict(color=laps_cache[ref_driver]['color'], width=2, dash='dot'), hovertemplate="%{y:.3f}s"), row=curr_row, col=1)
                        for target in valid_drivers:
                            if target != ref_driver:
                                delta_t, dt_ref_tel, _ = fastf1.utils.delta_time(ref_lap, laps_cache[target]['lap'])
                                fig.add_trace(go.Scatter(x=dt_ref_tel['Distance'], y=delta_t, name=f"{target} Delta", legendgroup=target, line=dict(color=laps_cache[target]['color'], width=3.5), fill='tozeroy' if len(valid_drivers) == 2 else 'none', hovertemplate="%{y:.3f}s"), row=curr_row, col=1)
                    fig.update_yaxes(title_text=get_y_title('Delta', br_mode), title_font=dict(family="Geist Mono", size=11, color=TEXT_M), row=curr_row, col=1, showgrid=True, gridcolor=grid_color, zeroline=False, minor=dict(ticklen=4, tickmode="linear", tick0=0, dtick=minor_dtick, showgrid=True, gridcolor=grid_color))
                else:
                    for drv in drivers:
                        if drv in laps_cache:
                            t = laps_cache[drv]['tel']
                            if ch == 'Gear': y_val = t['nGear'].astype(int)
                            elif ch == 'Brake' and br_mode == "On/Off": y_val = t['Brake'].astype(int)
                            elif ch == 'Brake' and br_mode == "Pressure": y_val = t['B_Pressure']
                            else: y_val = t[ch] if ch in t.columns else pd.Series(np.zeros(len(t)), index=t.index)
                            fill_mode = 'tozeroy' if (ch == 'Brake' and br_mode == "Pressure") else 'none'
                            htpl = "%{y:.1f}%<extra></extra>" if ch == 'ERS_Energy_2026' else "%{y:.1f}<extra></extra>"
                            fig.add_trace(go.Scatter(x=t['Distance'], y=y_val, name=drv, legendgroup=drv, showlegend=(curr_row == 1), line=dict(color=laps_cache[drv]['color'], width=2.5 if fill_mode=='tozeroy' else 3.5), fill=fill_mode, hovertemplate=htpl), row=curr_row, col=1)
                    
                    if ch == 'Speed' and speed_dom and dominance_bins is not None:
                        for i in range(num_microsectors):
                            w_color = laps_cache[fastest_drivers[i]]['color']
                            fig.add_vrect(x0=dominance_bins[i], x1=dominance_bins[i+1], fillcolor=w_color, opacity=0.15, layer="below", line_width=0, row=curr_row, col=1)

                    fig.update_yaxes(title_text=get_y_title(ch, br_mode), title_font=dict(family="Geist Mono", size=11, color=TEXT_M), showgrid=True, gridcolor=grid_color, zeroline=False, minor=dict(ticklen=4, tickmode="linear", tick0=0, dtick=minor_dtick, showgrid=True, gridcolor=grid_color), row=curr_row, col=1)
                    if ch == 'Brake' and br_mode == "On/Off": fig.update_yaxes(tickvals=[0, 1], ticktext=["OFF", "ON"], range=[-0.2, 1.2], row=curr_row, col=1)
                    elif ch == 'Brake' and br_mode == "Pressure": fig.update_yaxes(range=[-5, 105], row=curr_row, col=1)
                    elif ch == 'RPM': fig.update_yaxes(tickformat=",.0f", row=curr_row, col=1)
                    elif ch == 'ERS_Energy_2026': fig.update_yaxes(range=[0, 100], row=curr_row, col=1)

                    if ch == 'Speed' and show_apex and circuit_info is not None:
                        for idx, corner in circuit_info.corners.iterrows():
                            dist, c_num = corner['Distance'], corner['Number']
                            v_list = []
                            for d in drivers:
                                if d in laps_cache:
                                    tel_d = laps_cache[d]['tel']
                                    v_min = tel_d[(tel_d['Distance'] > dist - search_range) & (tel_d['Distance'] < dist + search_range)]['Speed'].min()
                                    v_list.append({'n': d, 'v': v_min, 'c': laps_cache[d]['color']})
                            if v_list:
                                v_list.sort(key=lambda x: x['v'], reverse=True)
                                v_f = v_list[0]
                                apex_html = f"<b style='color:{v_f['c']}; font-size:13px;'>{v_f['n']} {v_f['v']:.0f}</b>"
                                for v_o in v_list[1:]: apex_html += f"<br><b style='color:{v_o['c']}; font-size:13px;'>{v_o['n']} {v_o['v'] - v_f['v']:+.0f}</b>"
                                fig.add_vline(x=dist, line_width=1, line_dash="dot", line_color="#333", row=curr_row, col=1)
                                fig.add_annotation(x=dist, y=v_f['v'] - 30, yref=f"y{curr_row}", text=apex_html, showarrow=False, align="left", row=curr_row, col=1)
                                fig.add_trace(go.Scatter(x=[dist], y=[0], mode="text", text=[f"<span style='font-weight: 600;'>T{c_num}</span>"], textfont=dict(family="Geist Mono", size=12, color=TEXT_M), textposition="top center", showlegend=False, hoverinfo="skip"), row=curr_row, col=1)

                curr_row += 1

            apply_plotly_style(fig, "")
            if s1_dist and s2_dist:
                for r in range(1, total_rows + 1):
                    fig.add_vline(x=s1_dist, line_width=0.8, line_dash="15px 15px", line_color=TEXT_M, opacity=0.6, row=r, col=1)
                    fig.add_vline(x=s2_dist, line_width=0.8, line_dash="15px 15px", line_color=TEXT_M, opacity=0.6, row=r, col=1)

            fig.update_xaxes(hoverformat=".0f m")
            fig.update_layout(height=450 * total_rows, hovermode='x unified', margin=dict(l=50, r=20, t=20, b=20), separators=".,")
            plot_chart(fig, "telemetry_trace", extra_config={'edits': {'annotationPosition': True}})

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


