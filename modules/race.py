import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plotting import get_driver_color, apply_plotly_style, get_comparison_colors
from utils.session_store import get_cached_laps
from utils.components import plot_chart
from modules.advanced_analytics import render_consistency_score
import base64
import os

BG_CARD = "#060608"
BORDER = "rgba(255,255,255,0.07)"
TEXT_M = "#a1a1aa" 
TEXT_W = "#ffffff"

_TEAM_LOGO_MAP = {
    "MCLAREN": "MCLAREN.png", "RED BULL RACING": "RED BULL RACING.png",
    "FERRARI": "FERRARI.png", "MERCEDES": "MERCEDES.png", "RACING BULLS": "RB.png",
    "AUDI": "AUDI.png", "ALPINE": "ALPINE.png", "ASTON MARTIN": "ASTON MARTIN.png",
    "HAAS F1 TEAM": "HAAS.png", "CADILLAC": "CADILLAC.png",
    "KICK SAUBER": "KICK SAUBER.png", "WILLIAMS": "WILLIAMS.png",
}

def _team_logo_img(team_name: str, size: int = 22) -> str:
    file_name = _TEAM_LOGO_MAP.get(str(team_name).upper())
    if file_name:
        path = os.path.join("logos", file_name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/png;base64,{b64}" style="height:{size}px; object-fit:contain; flex-shrink:0;">'
    return ''

def _get_driver_team(session, drv: str) -> str:
    try:
        return str(session.results.loc[session.results["Abbreviation"] == drv, "TeamName"].iloc[0])
    except Exception:
        try:
            return str(session.results.at[drv, "TeamName"])
        except Exception:
            return ""

def _format_lap_time(seconds):
    if pd.isna(seconds) or seconds == 0: return "0:00.000"
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"

def get_filtered_laps(laps, selected_drivers, lap_range, stints, exclude_slow, exclude_pits, exclude_sc):
    filtered_dict = {}
    for drv in selected_drivers:
        drv_laps = laps.pick_drivers(drv).copy()
        drv_laps = drv_laps[(drv_laps['LapNumber'] >= lap_range[0]) & (drv_laps['LapNumber'] <= lap_range[1])]
        
        if stints: 
            drv_laps = drv_laps[drv_laps['Stint'].isin(stints)]
            
        if exclude_sc:
            drv_laps = drv_laps[~drv_laps['TrackStatus'].astype(str).str.contains('4|6', regex=True)]
            
        if exclude_pits:
            drv_laps = drv_laps.pick_wo_box()
            
        if exclude_slow:
            best_lap = drv_laps['LapTime'].min()
            if pd.notna(best_lap):
                drv_laps = drv_laps[drv_laps['LapTime'].dt.total_seconds() <= best_lap.total_seconds() * 1.07]
                
        drv_laps = drv_laps.dropna(subset=['LapTime'])
        if not drv_laps.empty:
            filtered_dict[drv] = drv_laps
            
    return filtered_dict

def render_structural_race_debrief(filtered_laps_dict):
    if len(filtered_laps_dict) < 2: return
    
    metrics = []
    for drv, df in filtered_laps_dict.items():
        pace_sec = df['LapTime'].dt.total_seconds().median()
        std_sec = df['LapTime'].dt.total_seconds().std()
        top_spd = df['SpeedST'].max() if ('SpeedST' in df.columns and not df['SpeedST'].isna().all()) else 0
        
        s1 = df['Sector1Time'].dt.total_seconds().median() if 'Sector1Time' in df.columns else 0
        s2 = df['Sector2Time'].dt.total_seconds().median() if 'Sector2Time' in df.columns else 0
        s3 = df['Sector3Time'].dt.total_seconds().median() if 'Sector3Time' in df.columns else 0
        
        x = df['LapNumber'].values
        y = df['LapTime'].dt.total_seconds().values
        if len(x) > 3:
            try:
                slope, _ = np.polyfit(x, y, 1)
            except Exception:
                slope = 0
        else:
            slope = 0
            
        metrics.append({
            'Driver': drv, 'Pace': pace_sec, 'Cons': std_sec if pd.notna(std_sec) else 0,
            'TopSpeed': top_spd if pd.notna(top_spd) else 0,
            'S1': s1 if pd.notna(s1) else 0, 'S2': s2 if pd.notna(s2) else 0, 'S3': s3 if pd.notna(s3) else 0,
            'Deg': slope,
            'LapCount': len(df)
        })
        
    m_sorted = sorted(metrics, key=lambda x: x['Pace'])
    leader = m_sorted[0]
    
    # 1. OVERVIEW PROIEZIONE GARA
    overview_html = f"L'analisi telemetrica del long-run isola chiaramente <b>{leader['Driver']}</b> come benchmark assoluto della sessione, dettando un passo mediano chirurgico di <b>{_format_lap_time(leader['Pace'])}</b>."
    
    gaps_info = []
    for d in m_sorted[1:]:
        gap_lap = d['Pace'] - leader['Pace']
        proj_15 = gap_lap * 15 # Proiezione su 15 giri
        gaps_info.append(f"<b>{d['Driver']}</b> (+{gap_lap:.3f}s/giro &rarr; proiezione su 15 giri: <b>+{proj_15:.1f}s</b>)")
    
    overview_html += f" Il differenziale di passo è strutturale e si traduce in un ritardo cumulato letale per gli inseguitori: <br><span style='color:{TEXT_W}; font-family:\"Geist Mono\", monospace; font-size:0.9rem;'>" + " | ".join(gaps_info) + "</span>"
    
    # 2. ANALISI MATEMATICA DEGRADO E FUEL EFFECT
    deg_sorted = sorted(metrics, key=lambda x: x['Deg'])
    deg_best = deg_sorted[0]
    deg_worst = deg_sorted[-1]
    
    deg_text = ""
    # Valutazione del migliore (Negative slope = Fuel Burn > Degrado)
    if deg_best['Deg'] <= -0.015:
        deg_text += f"Analizzando la pendenza della regressione lineare, <b>{deg_best['Driver']}</b> esprime una curva di degrado negativa (<b>{deg_best['Deg']:+.3f}s/giro</b>): il calo di peso del carburante e il <i>track evolution</i> compensano e superano l'usura della mescola. Gomma preservata in modo magistrale. "
    elif deg_best['Deg'] < 0.03:
        deg_text += f"Il <i>Tyre Management</i> premia <b>{deg_best['Driver']}</b>, che lavora in perfetta finestra di temperatura stabilizzando il decadimento della gomma a un livello di puro equilibrio termico (<b>{deg_best['Deg']:+.3f}s/giro</b>). "
    else:
        deg_text += f"Nonostante sia il migliore del gruppo, <b>{deg_best['Driver']}</b> mostra un degrado comunque evidente (<b>{deg_best['Deg']:+.3f}s/giro</b>), segnale di una mescola che fatica a reggere il carico laterale prolungato. "

    # Valutazione del peggiore
    if deg_worst['Driver'] != deg_best['Driver']:
        if deg_worst['Deg'] > 0.06:
            deg_text += f"Situazione diametralmente opposta, e profondamente critica, per <b>{deg_worst['Driver']}</b>. La telemetria rileva un crollo verticale della prestazione (<i>Thermal Drop-off</i> di <b>{deg_worst['Deg']:+.3f}s/giro</b>), sintomo inequivocabile di <i>overheating</i> della carcassa, scivolamento superficiale e probabile innesco di graining/blistering."
        else:
            deg_text += f"<b>{deg_worst['Driver']}</b> chiude la classifica dell'usura con un decadimento di {deg_worst['Deg']:+.3f}s/giro, faticando più degli avversari a estrarre grip termico a mescola usurata."

    # 3. CONSISTENZA, TRAFFICO ED ERRORI (Deviazione Standard)
    cons_sorted = sorted(metrics, key=lambda x: x['Cons'])
    cons_best = cons_sorted[0]
    cons_worst = cons_sorted[-1]
    
    cons_text = ""
    if cons_best['Cons'] < 0.4:
        cons_text += f"A livello di ripetibilità, <b>{cons_best['Driver']}</b> guida come un metronomo. La sua deviazione standard è schiacciata a <b>&plusmn;{cons_best['Cons']:.3f}s</b>: indicatore assoluto di run in <i>clean air</i> (aria pulita) senza sbavature al pedale. "
    else:
        cons_text += f"Il pilota più costante risulta <b>{cons_best['Driver']}</b> (&plusmn;{cons_best['Cons']:.3f}s), pur mostrando minime fluttuazioni dettate dai doppiati o dal vento. "

    if cons_worst['Driver'] != cons_best['Driver']:
        if cons_worst['Cons'] > 0.9:
            cons_text += f"Fortemente irregolare l'esecuzione di <b>{cons_worst['Driver']}</b>. Il grafico estremamente frastagliato (StdDev: <b>&plusmn;{cons_worst['Cons']:.3f}s</b>) denuncia una guida sporca, traffico pesante da gestire, problemi di <i>dirty air</i> in scia o frequenti micro-bloccaggi in staccata che hanno distrutto il ritmo."
        else:
            cons_text += f"<b>{cons_worst['Driver']}</b> fatica a mantenere un passo costante (&plusmn;{cons_worst['Cons']:.3f}s), alternando giri veloci a pause necessarie per raffreddare gli pneumatici."

    # 4. AERO SETUP E SPATIAL DOMINANCE (Velocità vs Handling)
    spd_sorted = sorted(metrics, key=lambda x: x['TopSpeed'], reverse=True)
    vmax_drv = spd_sorted[0]
    vmin_drv = spd_sorted[-1]
    
    s1_dom = min([m for m in metrics if m['S1'] > 0], key=lambda x: x['S1'], default=leader)['Driver']
    s2_dom = min([m for m in metrics if m['S2'] > 0], key=lambda x: x['S2'], default=leader)['Driver']
    s3_dom = min([m for m in metrics if m['S3'] > 0], key=lambda x: x['S3'], default=leader)['Driver']
    
    speed_text = f"Il delta cronometrico nasce da filosofie di delibera vettura asimmetriche. <b>{vmax_drv['Driver']}</b> scarica l'ala e taglia il muro d'aria, dominando la Speed-Trap con <b>{vmax_drv['TopSpeed']:.1f} km/h</b>. All'estremo opposto c'è <b>{vmin_drv['Driver']}</b> (solo {vmin_drv['TopSpeed']:.1f} km/h), palesemente frenato da una configurazione <i>High Downforce</i> (alto carico) o da estremo clipping ERS. "
    
    dom_set = set([s1_dom, s2_dom, s3_dom])
    if len(dom_set) == 1:
        speed_text += f"Nonostante le velocità massime, l'analisi vettoriale dei macro-settori non ammette repliche: <b>{list(dom_set)[0]}</b> distrugge la concorrenza dominando il S1, S2 e S3. La sua monoposto esprime una <i>minimum rolling speed</i> e un grip laterale inavvicinabile lungo tutto lo sviluppo del tracciato."
    else:
        speed_text += f"L'incrocio spaziale rivela i compromessi raggiunti in griglia: "
        sec_claims = []
        if s1_dom: sec_claims.append(f"<b>{s1_dom}</b> capitalizza la scorrevolezza nel S1")
        if s2_dom: sec_claims.append(f"<b>{s2_dom}</b> estrae il grip meccanico/aerodinamico nelle curve complesse del S2")
        if s3_dom: sec_claims.append(f"<b>{s3_dom}</b> scarica a terra la potenza in trazione nel S3")
        speed_text += ", ".join(sec_claims) + ". Un bilanciamento dinamico completamente frammentato tra i piloti."

    # RENDER HTML (Attenzione: Nessun rientro a inizio riga per i tag HTML!)
    html_card = f"""<div style="background-color: #000000; border: 1px solid {BORDER}; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
<div style="display:flex; align-items:center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px;">
<div style="background-color: rgba(33, 197, 94, 0.1); padding: 10px; border-radius: 8px; margin-right: 15px;">
<i class="fa-solid fa-microchip" style="color: #21C55E; font-size: 1.6rem;"></i>
</div>
<div>
<h3 style="margin: 0; color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px;">LONG RUN DEBRIEF AVANZATO</h3>
<p style="margin: 0; color: #a1a1aa; font-family: 'Space Grotesk', sans-serif; font-size: 0.85rem;">Analisi strutturale passo, degrado termico, costanza di guida e handling. Dati calcolati sui filtri attivi.</p>
</div>
</div>

<div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.05);">
<p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 1.05rem; line-height: 1.5; margin: 0;">{overview_html}</p>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
<div style="background: #000000; border: 1px solid rgba(255,255,255,0.07); padding: 20px; border-radius: 8px;">
<h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 0.95rem; margin-top: 0; margin-bottom: 12px;"><i class="fa-solid fa-fire-flame-curved" style="color: #ef4444; margin-right: 8px;"></i> THERMAL DROP-OFF &amp; CONSISTENCY</h4>
<p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin-bottom: 12px;">{deg_text}</p>
<p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin: 0;">{cons_text}</p>
</div>
<div style="background: #000000; border: 1px solid rgba(255,255,255,0.07); padding: 20px; border-radius: 8px;">
<h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 0.95rem; margin-top: 0; margin-bottom: 12px;"><i class="fa-solid fa-gauge-high" style="color: #3b82f6; margin-right: 8px;"></i> AERO DRAG & HANDLING COMPROMISE</h4>
<p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin: 0;">{speed_text}</p>
</div>
</div>
<div style="margin-top: 15px; font-size: 0.6rem; color: #71717a; text-align: right; font-family: 'Geist Mono', monospace;">
GENERATED BY: RACE ENGINEER MODEL V4 (PROJECTION & DROP-OFF ANALYSIS)
</div>
</div>"""

    st.markdown(html_card, unsafe_allow_html=True)


def render_average_gap(laps, session):
    valid_laps = laps.pick_quicklaps().pick_wo_box().dropna(subset=['LapTime'])
    if valid_laps.empty: return None

    medians = valid_laps.groupby('Driver')['LapTime'].median().dt.total_seconds().sort_values()
    fastest_avg = medians.iloc[0]
    gaps = medians - fastest_avg
    
    fig = go.Figure()
    for drv, gap in gaps.items():
        text_str = f"<b>+{gap:.3f}s</b>" if gap > 0 else "<b>LEADER</b>"
        fig.add_trace(go.Bar(
            y=[drv], x=[gap], orientation='h',
            marker=dict(color=get_driver_color(drv, session)),
            text=[text_str], textposition='outside',
            textfont=dict(family="Space Grotesk", color=TEXT_W, size=16),
            hovertemplate=f"<b>{drv}</b><br>Avg Gap: +{gap:.3f}s<extra></extra>", showlegend=False
        ))
    fig.update_layout(yaxis={'categoryorder': 'total descending'}, height=450, margin=dict(l=10, r=40, t=50, b=10))
    fig.update_xaxes(title="AVERAGE GAP (S)", title_font=dict(family="Geist Mono", size=11, color=TEXT_M))
    return apply_plotly_style(fig, "")


def render_top_speed(laps, session):
    if 'SpeedST' in laps.columns and not laps['SpeedST'].isna().all():
        speeds = laps.groupby('Driver')['SpeedST'].max().sort_values()
    else: return None

    fig = go.Figure()
    for drv, speed in speeds.items():
        fig.add_trace(go.Bar(
            y=[drv], x=[speed], orientation='h',
            marker=dict(color=get_driver_color(drv, session)),
            text=[f"<b>{speed:.0f} km/h</b>"], 
            textposition='outside', 
            textfont=dict(family="Space Grotesk", color=TEXT_W, size=16), 
            showlegend=False
        ))
    min_speed = speeds.min() - 10 if not speeds.empty else 0
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450, margin=dict(l=10, r=40, t=50, b=10))
    fig.update_xaxes(range=[min_speed, speeds.max() + 20], title="TOP SPEED (KM/H)", title_font=dict(family="Geist Mono", size=11, color=TEXT_M))
    return apply_plotly_style(fig, "")


def render_sectors_times(laps, session, sec_mode="MEDIAN"):
    valid_laps = laps.pick_quicklaps().dropna(subset=['Sector1Time', 'Sector2Time', 'Sector3Time'])
    if valid_laps.empty: return None
    
    if sec_mode == "BEST":
        agg_sectors = valid_laps.groupby('Driver')[['Sector1Time', 'Sector2Time', 'Sector3Time']].min()
        title = "BEST SECTORS TIMES"
    elif sec_mode == "AVERAGE":
        agg_sectors = valid_laps.groupby('Driver')[['Sector1Time', 'Sector2Time', 'Sector3Time']].mean()
        title = "AVERAGE SECTORS TIMES"
    else:
        agg_sectors = valid_laps.groupby('Driver')[['Sector1Time', 'Sector2Time', 'Sector3Time']].median()
        title = "MEDIAN SECTORS TIMES"
        
    for col in agg_sectors.columns: agg_sectors[col] = agg_sectors[col].dt.total_seconds()
    
    fig = make_subplots(rows=1, cols=3, shared_yaxes=False, subplot_titles=("SECTOR 1", "SECTOR 2", "SECTOR 3"))
    
    for i, sector in enumerate(['Sector1Time', 'Sector2Time', 'Sector3Time'], 1):
        s_data = agg_sectors[sector].sort_values()
        min_v = s_data.min()
        max_v = s_data.max()
        
        for drv, val in s_data.items():
            text_str = f"<b>{val:.3f}s</b>" if val == min_v else f"<b>+{(val - min_v):.3f}s</b>"
            
            fig.add_trace(go.Bar(
                x=[drv], y=[val],
                marker=dict(color=get_driver_color(drv, session)),
                text=[text_str], 
                textposition='outside', 
                textangle=0,
                showlegend=False
            ), row=1, col=i)
            
        fig.update_yaxes(range=[min_v - 0.2, max_v + 1.5], title="TIME (S)" if i==1 else "", title_font=dict(family="Geist Mono", size=11, color=TEXT_M), row=1, col=i)

    fig.update_layout(height=450, margin=dict(l=10, r=10, t=50, b=10))
    for annotation in fig['layout']['annotations']: annotation['font'] = dict(family="Geist Mono", size=15, color=TEXT_W)
    
    fig = apply_plotly_style(fig, "")
    fig.update_traces(textfont_size=6, textfont_family="Space Grotesk", constraintext='none', cliponaxis=False)
    
    return fig


GREEN  = "#21C55E"
ORANGE = "#f59e0b"
RED    = "#ef4444"
BLUE   = "#3b82f6"
PURPLE = "#c084fc"


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


def render_fuel_corrected_pace(filtered_laps_dict, session, total_laps: int, fuel_effect: float, color_map=None):
    """Pace chart with fuel mass effect subtracted per lap."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:12px;'>"
        f"<i class='fa-solid fa-gas-pump' style='color:{ORANGE}; font-size:1.2rem; margin-right:10px;'></i>"
        "<h4 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:0.95rem;"
        " text-transform:uppercase; letter-spacing:1px;'>FUEL-CORRECTED PACE</h4>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{TEXT_M}; font-family:Space Grotesk,sans-serif; font-size:0.82rem;"
        " margin-bottom:12px; line-height:1.5;'>"
        "Ogni giro viene corretto sottraendo l'effetto del calo carburante: "
        f"<b style='color:#fff;'>{fuel_effect:.3f}s/giro</b> (≈ 0.034s/kg × carburante bruciato). "
        "Il risultato mostra il <b>degrado puro della mescola</b>, depurato dall'alleggerimento della vettura.</p>",
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    for drv, drv_laps in filtered_laps_dict.items():
        color = (color_map.get(drv) if color_map else None) or get_driver_color(drv, session)
        raw_sec = drv_laps["LapTime"].dt.total_seconds()
        lap_nums = drv_laps["LapNumber"].values
        # Fuel correction: lap N burns (N-1) * fuel_effect more fuel already gone → subtract
        correction = (total_laps - lap_nums) * fuel_effect - (total_laps - lap_nums[0]) * fuel_effect
        corrected = raw_sec.values + correction   # add back the fuel weight effect
        corrected_dt = pd.to_datetime(corrected, unit="s")

        fig.add_trace(go.Scatter(
            x=lap_nums, y=corrected_dt,
            mode="lines+markers", name=drv,
            line=dict(color=color, width=2.5),
            marker=dict(color=color, size=5),
            hovertemplate=f"<b>{drv}</b> Lap %{{x}}<br>Fuel-corr: %{{y|%M:%S.%L}}<extra></extra>",
        ))
        if len(lap_nums) > 4:
            try:
                slope, intercept = np.polyfit(lap_nums, corrected, 1)
                trend_y = pd.to_datetime(slope * lap_nums + intercept, unit="s")
                fig.add_trace(go.Scatter(
                    x=lap_nums, y=trend_y, mode="lines",
                    line=dict(color=color, width=1.5, dash="dot"),
                    opacity=0.5, showlegend=False, hoverinfo="skip",
                ))
                mid = len(lap_nums) // 2
                fig.add_annotation(
                    x=lap_nums[mid], y=trend_y.iloc[mid],
                    text=f"<b style='color:{color};'>{drv} {slope:+.3f}s/lap</b>",
                    showarrow=False, yshift=-18,
                    font=dict(family="Geist Mono", size=10, color=color),
                )
            except Exception:
                pass

    apply_plotly_style(fig, "")
    fig.update_layout(height=480, hovermode="x unified", margin=dict(l=50, r=20, t=60, b=20))
    fig.update_xaxes(title_text="LAP NUMBER")
    fig.update_yaxes(title_text="CORRECTED LAP TIME", tickformat="%M:%S.%L")
    plot_chart(fig, "race_lap_times")


def render_h2h_card(filtered_laps_dict, session, color_map=None):
    """Head-to-head comparison card for exactly 2 drivers."""
    drivers = list(filtered_laps_dict.keys())
    if len(drivers) < 2:
        return
    drv_a, drv_b = drivers[0], drivers[1]
    col_a = (color_map.get(drv_a) if color_map else None) or get_driver_color(drv_a, session)
    col_b = (color_map.get(drv_b) if color_map else None) or get_driver_color(drv_b, session)

    def _stat(df):
        sec = df["LapTime"].dt.total_seconds()
        pace = sec.median()
        std  = sec.std() if len(sec) > 1 else 0.0
        s1   = df["Sector1Time"].dt.total_seconds().median() if "Sector1Time" in df.columns else np.nan
        s2   = df["Sector2Time"].dt.total_seconds().median() if "Sector2Time" in df.columns else np.nan
        s3   = df["Sector3Time"].dt.total_seconds().median() if "Sector3Time" in df.columns else np.nan
        spd  = df["SpeedST"].max() if ("SpeedST" in df.columns and not df["SpeedST"].isna().all()) else np.nan
        x    = df["LapNumber"].values
        try:
            deg = np.polyfit(x, sec.values, 1)[0] if len(x) > 3 else 0.0
        except Exception:
            deg = 0.0
        return dict(pace=pace, std=std, s1=s1, s2=s2, s3=s3, spd=spd, deg=deg)

    sa = _stat(filtered_laps_dict[drv_a])
    sb = _stat(filtered_laps_dict[drv_b])

    # Dimensions: lower is better for pace/std/s1/s2/s3/deg, higher for spd
    dims = [
        ("Median Pace",   sa["pace"], sb["pace"],  False, "s"),
        ("Consistency",   sa["std"],  sb["std"],   False, "±s"),
        ("Sector 1",      sa["s1"],   sb["s1"],    False, "s"),
        ("Sector 2",      sa["s2"],   sb["s2"],    False, "s"),
        ("Sector 3",      sa["s3"],   sb["s3"],    False, "s"),
        ("Top Speed",     sa["spd"],  sb["spd"],   True,  "km/h"),
        ("Degradation",   sa["deg"],  sb["deg"],   False, "s/lap"),
    ]

    html_rows = ""
    wins_a = wins_b = 0
    for label, va, vb, higher_better, unit in dims:
        if pd.isna(va) or pd.isna(vb):
            continue
        if higher_better:
            a_wins = va > vb
        else:
            a_wins = va < vb
        if a_wins:
            wins_a += 1
            win_col_a, win_col_b = GREEN, TEXT_M
            icon_a, icon_b = "fa-chevron-right", ""
        else:
            wins_b += 1
            win_col_a, win_col_b = TEXT_M, GREEN
            icon_a, icon_b = "", "fa-chevron-left"
        delta = abs(va - vb)
        fmt = ".3f" if unit in ("s", "±s", "s/lap") else ".1f"
        html_rows += f"""
<tr style="border-bottom:1px solid {BORDER};">
  <td style="padding:8px 10px; text-align:right; color:{win_col_a}; font-family:'Geist Mono',monospace; font-size:0.82rem; font-weight:700; width:28%;">
    {va:{fmt}} {unit}
    {"<i class='fa-solid fa-chevron-right' style='margin-left:6px; font-size:0.65rem;'></i>" if a_wins else ""}
  </td>
  <td style="padding:8px 10px; text-align:center; color:{TEXT_M}; font-family:'Geist Mono',monospace; font-size:0.68rem; letter-spacing:1px; width:44%;">
    {label.upper()}<br>
    <span style="color:#444; font-size:0.6rem;">&Delta; {delta:{fmt}}</span>
  </td>
  <td style="padding:8px 10px; text-align:left; color:{win_col_b}; font-family:'Geist Mono',monospace; font-size:0.82rem; font-weight:700; width:28%;">
    {"<i class='fa-solid fa-chevron-left' style='margin-right:6px; font-size:0.65rem;'></i>" if not a_wins else ""}
    {vb:{fmt}} {unit}
  </td>
</tr>"""

    overall_a = GREEN if wins_a >= wins_b else TEXT_M
    overall_b = GREEN if wins_b > wins_a else TEXT_M

    st.markdown(
        f"""
<div style="background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; overflow:hidden; margin-bottom:20px;">
  <div style="display:grid; grid-template-columns:1fr auto 1fr; align-items:center; padding:16px 20px;
              background:rgba(255,255,255,0.04); border-bottom:1px solid {BORDER};">
    <div style="text-align:center;">
      <div style="width:5px; height:26px; background:{col_a}; border-radius:3px; display:inline-block; margin-bottom:6px;"></div>
      <div style="font-family:'Geist Mono',monospace; font-size:1.1rem; color:{col_a}; font-weight:700;">{drv_a}</div>
      <div style="font-family:'Geist Mono',monospace; font-size:1.6rem; color:{overall_a}; font-weight:700; margin-top:4px;">{wins_a}</div>
      <div style="font-size:0.58rem; color:{TEXT_M}; font-family:'Geist Mono',monospace; letter-spacing:1px;">WINS</div>
    </div>
    <div style="text-align:center; padding:0 20px;">
      <i class="fa-solid fa-bolt" style="color:{ORANGE}; font-size:1.4rem;"></i>
      <div style="font-family:'Geist Mono',monospace; font-size:0.6rem; color:{TEXT_M}; letter-spacing:2px; margin-top:4px;">H2H</div>
    </div>
    <div style="text-align:center;">
      <div style="width:5px; height:26px; background:{col_b}; border-radius:3px; display:inline-block; margin-bottom:6px;"></div>
      <div style="font-family:'Geist Mono',monospace; font-size:1.1rem; color:{col_b}; font-weight:700;">{drv_b}</div>
      <div style="font-family:'Geist Mono',monospace; font-size:1.6rem; color:{overall_b}; font-weight:700; margin-top:4px;">{wins_b}</div>
      <div style="font-size:0.58rem; color:{TEXT_M}; font-family:'Geist Mono',monospace; letter-spacing:1px;">WINS</div>
    </div>
  </div>
  <table style="width:100%; border-collapse:collapse;">
    <tbody>{html_rows}</tbody>
  </table>
</div>""",
        unsafe_allow_html=True,
    )


def render_position_tracker(laps, session, selected_drivers, color_map=None):
    """Lap-by-lap position chart for selected drivers."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:14px;'>"
        f"<i class='fa-solid fa-arrow-up-9-1' style='color:{BLUE}; font-size:1.2rem; margin-right:10px;'></i>"
        "<h4 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:0.95rem;"
        " text-transform:uppercase; letter-spacing:1px;'>POSITION TRACKER</h4></div>",
        unsafe_allow_html=True,
    )

    pos_data = laps[["Driver", "LapNumber", "Position"]].dropna(subset=["Position", "LapNumber"]).copy()
    pos_data["Position"] = pos_data["Position"].astype(int)
    drivers_here = [d for d in selected_drivers if d in pos_data["Driver"].unique()]

    if not drivers_here:
        st.info("Dati di posizione non disponibili. Verifica che la sessione sia una Gara.")
        return

    _cmp = color_map or {}
    fig = go.Figure()

    for drv in drivers_here:
        drv_pos = pos_data[pos_data["Driver"] == drv].sort_values("LapNumber")
        color   = _cmp.get(drv, get_driver_color(drv, session))

        fig.add_trace(go.Scatter(
            x=drv_pos["LapNumber"],
            y=drv_pos["Position"],
            mode="lines+markers",
            name=drv,
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color),
            hovertemplate=f"<b>{drv}</b> Lap %{{x}}: <b>P%{{y}}</b><extra></extra>",
        ))

        # Annotate start and final position
        if not drv_pos.empty:
            start_pos = int(drv_pos.iloc[0]["Position"])
            end_pos   = int(drv_pos.iloc[-1]["Position"])
            end_lap   = int(drv_pos.iloc[-1]["LapNumber"])
            gained    = start_pos - end_pos
            label     = f"P{end_pos}"

            fig.add_annotation(
                x=end_lap, y=end_pos,
                text=label,
                showarrow=False,
                xanchor="left", xshift=8,
                font=dict(color=color, size=11, family="Geist Mono"),
            )

    apply_plotly_style(fig, "")
    fig.update_layout(
        height=440,
        hovermode="x unified",
        margin=dict(l=50, r=40, t=60, b=20),
    )
    fig.update_yaxes(
        autorange="reversed",
        title_text="POSITION",
        dtick=1,
        tickprefix="P",
    )
    fig.update_xaxes(title_text="LAP NUMBER")
    plot_chart(fig, "race_positions")

    # Positions-gained summary tiles
    st.markdown("<div style='display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;'>", unsafe_allow_html=True)
    for drv in drivers_here:
        drv_pos = pos_data[pos_data["Driver"] == drv].sort_values("LapNumber")
        if drv_pos.empty:
            continue
        color      = _cmp.get(drv, get_driver_color(drv, session))
        start_pos  = int(drv_pos.iloc[0]["Position"])
        end_pos    = int(drv_pos.iloc[-1]["Position"])
        gained     = start_pos - end_pos
        gain_color = GREEN if gained > 0 else (RED if gained < 0 else TEXT_M)
        gain_icon  = "fa-arrow-up" if gained > 0 else ("fa-arrow-down" if gained < 0 else "fa-minus")
        gain_label = f"+{gained}" if gained > 0 else str(gained)
        team_name  = _get_driver_team(session, drv)
        logo_html  = _team_logo_img(team_name, size=22)

        st.markdown(
            f"<div style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:10px;"
            f" padding:10px 14px; flex:1; min-width:150px; display:flex; align-items:center; gap:10px;'>"
            f"<div style='flex-shrink:0; display:flex; align-items:center;'>{logo_html}</div>"
            f"<div>"
            f"<div style='font-family:Geist Mono,monospace; font-size:0.8rem; color:{color};"
            f" font-weight:700; margin-bottom:5px; letter-spacing:0.5px;'>{drv}</div>"
            f"<div style='font-size:0.72rem; color:{TEXT_M}; font-family:Geist Mono,monospace;'>"
            f"P{start_pos} <span style='color:{TEXT_M};'>→</span> P{end_pos}"
            f"&nbsp;&nbsp;<i class='fa-solid {gain_icon}' style='color:{gain_color};'></i>"
            f" <b style='color:{gain_color};'>{gain_label}</b></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_driver_pace(filtered_laps_dict, session, color_map=None):
    fig = go.Figure()
    for drv, drv_laps in filtered_laps_dict.items():
        color = (color_map.get(drv) if color_map and drv in color_map else None) or get_driver_color(drv, session)
        
        y_seconds = drv_laps['LapTime'].dt.total_seconds()
        y_datetime = pd.to_datetime(y_seconds, unit='s')
        
        s1 = drv_laps['Sector1Time'].dt.total_seconds().fillna(0).round(3)
        s2 = drv_laps['Sector2Time'].dt.total_seconds().fillna(0).round(3)
        s3 = drv_laps['Sector3Time'].dt.total_seconds().fillna(0).round(3)
        pos = drv_laps['Position'].fillna(0).astype(int)
        
        custom_d = np.stack((
            drv_laps['Compound'], 
            drv_laps['TyreLife'], 
            drv_laps['Stint'],
            s1,
            s2,
            s3,
            pos
        ), axis=-1)
        
        fig.add_trace(go.Scatter(
            x=drv_laps['LapNumber'], y=y_datetime, mode='lines+markers',
            customdata=custom_d,
            name=drv, line=dict(color=color, width=2), marker=dict(color=color, size=6),
            hovertemplate="<b>%{name}</b> (Pos: %{customdata[6]})<br>Lap: %{x}<br>Time: <b>%{y|%M:%S.%L}</b><br>Tyre: %{customdata[0]} (Laps: %{customdata[1]})<br>Stint: %{customdata[2]}<br><br><b>S1:</b> %{customdata[3]}s | <b>S2:</b> %{customdata[4]}s | <b>S3:</b> %{customdata[5]}s<extra></extra>"
        ))
        
        if len(drv_laps) > 3:
            trend_sec = y_seconds.rolling(3, min_periods=1).mean()
            trend_dt = pd.to_datetime(trend_sec, unit='s')
            fig.add_trace(go.Scatter(x=drv_laps['LapNumber'], y=trend_dt, mode='lines', line=dict(color=color, width=3, dash='dot'), opacity=0.4, showlegend=False, hoverinfo='skip'))

    fig.update_layout(height=550, hovermode='x unified', margin=dict(l=10, r=10, t=50, b=10))
    fig.update_xaxes(title="LAP NUMBER", title_font=dict(family="Geist Mono", size=11, color=TEXT_M))
    fig.update_yaxes(title="LAP TIME", tickformat="%M:%S.%L", title_font=dict(family="Geist Mono", size=11, color=TEXT_M))
    
    return apply_plotly_style(fig, "")


# ─────────────────────────────────────────────────────────────────────────────
# Stint Degradation & Tyre Cliff helpers
# ─────────────────────────────────────────────────────────────────────────────

def _compute_stint_degradation(combined: pd.DataFrame):
    """
    Returns one row per (Driver, Stint, Compound): slope s/lap, intercept, r2, lap_count.
    Works on a plain DataFrame (no FastF1 Laps type required).
    Min 2 laps per group.
    """
    rows = []
    for (drv, stint, compound), grp in combined.groupby(["Driver", "Stint", "Compound"], sort=False):
        grp = grp.sort_values("LapNumber").dropna(subset=["LapTime"])
        if len(grp) < 2:
            continue
        times = grp["LapTime"].dt.total_seconds().values
        laps  = grp["LapNumber"].values.astype(float)
        try:
            coeffs = np.polyfit(laps, times, 1)
            slope, intercept = float(coeffs[0]), float(coeffs[1])
            y_hat  = slope * laps + intercept
            ss_res = np.sum((times - y_hat) ** 2)
            ss_tot = np.sum((times - times.mean()) ** 2)
            r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
        except Exception:
            slope, intercept, r2 = 0.0, float(times.mean()), 0.0
        rows.append(dict(
            Driver=drv, Stint=stint, Compound=str(compound).upper(),
            Slope=slope, Intercept=intercept, R2=r2,
            LapCount=len(grp), AvgLap=float(times.mean()),
            StartLap=int(laps.min()), EndLap=int(laps.max()),
        ))
    return pd.DataFrame(rows)


def _find_tyre_cliff(drv: str, df: pd.DataFrame, threshold: float = 1.5):
    """Detect first cliff lap per stint for a single driver."""
    cliffs = []
    for (stint, compound), grp in df[df["Driver"] == drv].groupby(["Stint", "Compound"]):
        grp = grp.sort_values("LapNumber").dropna(subset=["LapTime"])
        if len(grp) < 5:
            continue
        times  = grp["LapTime"].dt.total_seconds().values
        laps   = grp["LapNumber"].values
        deltas = np.gradient(times)
        baseline = float(np.median(deltas[:max(2, len(deltas) // 3)]))
        for i in range(2, len(deltas) - 1):
            if deltas[i] > baseline * threshold and deltas[i] > 0.05:
                cliffs.append(dict(Driver=drv, Stint=stint, Compound=str(compound).upper(),
                                   CliffLap=int(laps[i]), CliffDelta=float(deltas[i])))
                break
    return cliffs


def render_stint_degradation(filtered_laps_dict: dict, session, color_map: dict = None):
    """Per-stint degradation slope bar chart. Uses already-filtered laps dict."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:14px;'>"
        f"<i class='fa-solid fa-arrow-trend-down' style='color:{RED}; font-size:1.2rem; margin-right:10px;'></i>"
        "<h4 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:0.95rem;"
        " text-transform:uppercase; letter-spacing:1px;'>STINT-BY-STINT DEGRADATION</h4></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{TEXT_M}; font-size:0.82rem; font-family:Space Grotesk,sans-serif;"
        " margin-bottom:16px;'>Pendenza (s/giro) per ciascuno stint calcolata con regressione lineare."
        " Rosso = degrado critico (&gt;0.08 s/lap), arancio = moderato, verde = stabile.</p>",
        unsafe_allow_html=True,
    )

    combined = pd.concat(
        [df.assign(Driver=drv) if "Driver" not in df.columns else df
         for drv, df in filtered_laps_dict.items()],
        ignore_index=True,
    )
    combined = combined.dropna(subset=["LapTime", "Stint", "Compound"])
    deg_df = _compute_stint_degradation(combined)
    if deg_df.empty:
        st.info("Dati di stint insufficienti (sono necessari almeno 2 giri per stint senza pit).")
        return

    drivers = list(filtered_laps_dict.keys())
    _cmp = color_map or {}

    fig = go.Figure()
    for drv in drivers:
        sub = deg_df[deg_df["Driver"] == drv].sort_values("StartLap")
        if sub.empty:
            continue
        drv_color = _cmp.get(drv, get_driver_color(drv, session))
        for _, row in sub.iterrows():
            bar_color = RED if row["Slope"] > 0.08 else (ORANGE if row["Slope"] > 0.03 else GREEN)
            fig.add_trace(go.Bar(
                x=[f"{drv} S{int(row['Stint'])}"],
                y=[row["Slope"]],
                marker_color=bar_color,
                marker_line_color=drv_color, marker_line_width=2,
                name=drv,
                legendgroup=drv,
                showlegend=False,
                customdata=[[drv, row["Stint"], row["Compound"], row["LapCount"],
                             row["StartLap"], row["EndLap"], row["AvgLap"]]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b> Stint %{customdata[1]} (%{customdata[2]})<br>"
                    "Slope: <b>%{y:+.4f} s/lap</b><br>"
                    "Giri: %{customdata[4]}\u2013%{customdata[5]} (%{customdata[3]} laps)<br>"
                    "Avg lap: %{customdata[6]:.3f}s<extra></extra>"
                ),
            ))

    fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.add_hline(y=0.03, line_color=ORANGE, line_width=1, line_dash="dot",
                  annotation_text="MILD", annotation_font_color=ORANGE, annotation_font_size=9)
    fig.add_hline(y=0.08, line_color=RED, line_width=1, line_dash="dot",
                  annotation_text="HIGH", annotation_font_color=RED, annotation_font_size=9)

    apply_plotly_style(fig, "")
    fig.update_layout(height=360, barmode="group", margin=dict(l=50, r=20, t=60, b=60))
    fig.update_yaxes(title_text="SLOPE (S/LAP)", zeroline=False)
    fig.update_xaxes(tickangle=-30, tickfont=dict(family="Geist Mono", size=10))
    plot_chart(fig, "tyre_degradation_rate")

    # Summary tiles
    st.markdown("<div style='display:flex; gap:8px; flex-wrap:wrap; margin-top:4px;'>", unsafe_allow_html=True)
    for drv in drivers:
        sub = deg_df[deg_df["Driver"] == drv]
        if sub.empty:
            continue
        drv_color = _cmp.get(drv, get_driver_color(drv, session))
        stints_html = "".join(
            f"<span style='margin-right:8px; font-size:0.7rem; color:"
            f"{'#ef4444' if r.Slope>0.08 else ('#f59e0b' if r.Slope>0.03 else '#21C55E')};'>"
            f"S{int(r.Stint)}({r.Compound[:1]}): {r.Slope:+.3f}s</span>"
            for r in sub.itertuples()
        )
        st.markdown(
            f"<div style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:8px;"
            f" padding:10px 14px; flex:1; min-width:160px;'>"
            f"<div style='font-family:Geist Mono,monospace; font-size:0.8rem; color:{drv_color};"
            f" font-weight:700; margin-bottom:6px;'>{drv}</div>{stints_html}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_cliff_detector(filtered_laps_dict: dict, session, color_map: dict = None):
    """Tyre cliff detection on filtered laps."""
    st.markdown(
        "<div style='display:flex; align-items:center; margin-bottom:14px;'>"
        f"<i class='fa-solid fa-triangle-exclamation' style='color:{RED}; font-size:1.2rem; margin-right:10px;'></i>"
        "<h4 style='margin:0; color:#fff; font-family:Geist Mono,monospace; font-size:0.95rem;"
        " text-transform:uppercase; letter-spacing:1px;'>TYRE CLIFF DETECTOR</h4></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.2); border-left:4px solid {RED}; border-radius:8px;"
        " padding:14px 16px; margin-bottom:16px;'>"
        f"<p style='color:#d4d4d8; font-size:0.85rem; font-family:Space Grotesk,sans-serif; margin:0; line-height:1.5;'>"
        "Rilevato quando il delta lap-time supera <b>1.5\u00d7 il baseline</b> (prima met\u00e0 stint) e &gt;0.05s."
        " Il marker <b style='color:#ef4444;'>\u00d7</b> indica il giro esatto del crollo.</p></div>",
        unsafe_allow_html=True,
    )

    combined = pd.concat(
        [df.assign(Driver=drv) if "Driver" not in df.columns else df
         for drv, df in filtered_laps_dict.items()],
        ignore_index=True,
    )
    combined = combined.dropna(subset=["LapTime", "Stint", "Compound"])
    drivers  = list(filtered_laps_dict.keys())
    _cmp     = color_map or {}

    all_cliffs = []
    for drv in drivers:
        all_cliffs.extend(_find_tyre_cliff(drv, combined))

    fig = go.Figure()
    for drv in drivers:
        drv_laps = combined[combined["Driver"] == drv].sort_values("LapNumber")
        if drv_laps.empty:
            continue
        color    = _cmp.get(drv, get_driver_color(drv, session))
        times_dt = pd.to_datetime(drv_laps["LapTime"].dt.total_seconds(), unit="s")
        fig.add_trace(go.Scatter(
            x=drv_laps["LapNumber"], y=times_dt,
            mode="lines", name=drv,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{drv}</b> Lap %{{x}}: %{{y|%M:%S.%2f}}<extra></extra>",
        ))

    for cliff in all_cliffs:
        drv   = cliff["Driver"]
        c_lap = cliff["CliffLap"]
        color = _cmp.get(drv, get_driver_color(drv, session))
        row   = combined[(combined["Driver"] == drv) & (combined["LapNumber"] == c_lap)]
        if row.empty:
            continue
        cliff_t = pd.to_datetime(row["LapTime"].dt.total_seconds().values[0], unit="s")
        fig.add_trace(go.Scatter(
            x=[c_lap], y=[cliff_t],
            mode="markers",
            marker=dict(color=RED, size=14, symbol="x-open", line=dict(color=RED, width=3)),
            showlegend=False,
            hovertemplate=f"<b>{drv}</b> CLIFF @ Lap {c_lap} (+{cliff['CliffDelta']:.3f}s spike)<extra></extra>",
        ))

    apply_plotly_style(fig, "")
    fig.update_layout(height=420, hovermode="x unified", margin=dict(l=50, r=20, t=60, b=20))
    fig.update_xaxes(title_text="LAP NUMBER")
    fig.update_yaxes(title_text="LAP TIME", tickformat="%M:%S.%2f")
    plot_chart(fig, "race_lap_evolution")

    if all_cliffs:
        st.markdown(
            "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr));"
            " gap:10px; margin-top:8px;'>",
            unsafe_allow_html=True,
        )
        for cliff in all_cliffs:
            drv   = cliff["Driver"]
            color = _cmp.get(drv, get_driver_color(drv, session))
            st.markdown(
                f"<div style='background:{BG_CARD}; border:1px solid {RED}40; border-left:3px solid {RED};"
                f" border-radius:8px; padding:12px;'>"
                f"<div style='font-family:Geist Mono,monospace; font-size:0.82rem; color:{color};"
                f" font-weight:700; margin-bottom:4px;'>{drv} \u2014 Stint {cliff['Stint']} ({cliff['Compound'][:1]})</div>"
                f"<div style='font-family:Geist Mono,monospace; font-size:0.7rem; color:{RED};'>CLIFF @ LAP {cliff['CliffLap']}"
                f"<br><span style='color:{TEXT_M};'>Rate: +{cliff['CliffDelta']:.3f}s/lap</span></div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("Nessun cliff rilevato. Ottima gestione gomme.")


def render(session):
    with st.spinner("Caricamento dati gara..."):
        try:
            laps = get_cached_laps(session)
            drivers = [session.get_driver(d)["Abbreviation"] for d in session.drivers]
            max_laps = int(laps['LapNumber'].max()) if not laps.empty else 50
            available_stints = sorted(laps['Stint'].dropna().unique().tolist())
        except Exception as e:
            st.error(f"Errore nel caricamento: {e}")
            return

    with st.expander("ADVANCED DRIVER & PACE CONFIGURATION", expanded=True):
        c1, c2, c3, c4 = st.columns([1.5, 1.2, 1.2, 1.2])
        with c1: 
            selected_drivers = st.multiselect("DRIVER SELECTION", drivers, default=drivers[:3])
        with c2: 
            lap_range = st.slider("LAP RANGE", 1, max_laps, (1, max_laps))
        with c3: 
            stints_selected = st.multiselect("FILTER BY STINT", available_stints, default=[])
        with c4: 
            exclude_pits = st.toggle("EXCLUDE PIT LAPS", value=True)
            exclude_sc = st.toggle("EXCLUDE SC / VSC", value=True)
            exclude_slow = st.toggle("EXCLUDE SLOW (>107%)", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. ESTRAZIONE DEI GIRI FILTRATI IN BASE ALLA CONFIGURAZIONE
    filtered_laps_dict = get_filtered_laps(laps, selected_drivers, lap_range, stints_selected, exclude_slow, exclude_pits, exclude_sc)

    # Comparison colors: second driver of same team gets yellow
    _cmp_colors = get_comparison_colors(selected_drivers, session)
    
    # 2. RENDER MOTORE DI ANALISI STRUTTURALE SUI DATI FILTRATI
    if len(filtered_laps_dict) >= 2:
        render_structural_race_debrief(filtered_laps_dict)
    elif len(filtered_laps_dict) == 1:
        st.info("Seleziona almeno 2 piloti e assicurati che abbiano giri validi nel range indicato per abilitare il Debriefing.")

    # 3. RENDER RACE PACE CHART
    st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-chart-line'></i></div><span class='section-sep-label'>Race Pace &amp; Degradation</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
    if filtered_laps_dict:
        st.markdown(
            "<div class='chart-frame-header'>"
            "<div class='chart-frame-title'><i class='fa-solid fa-chart-area'></i>Driver Pace — Lap-by-Lap</div>"
            "<div class='chart-frame-meta'><span class='chart-frame-badge'><i class='fa-solid fa-tachometer-alt'></i>&nbsp;PACE</span></div>"
            "</div>",
            unsafe_allow_html=True,
        )
        pace_fig = render_driver_pace(filtered_laps_dict, session, color_map=_cmp_colors)
        if pace_fig: plot_chart(pace_fig, "pace_analysis")
    else:
        st.warning("Nessun giro valido trovato per i piloti e i filtri selezionati.")

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("<div class='reveal-card rd-1'><div class='section-sep' style='margin-top:8px;'><div class='section-sep-icon'><i class='fa-solid fa-clock-rotate-left'></i></div><span class='section-sep-label'>Avg Pace Gap</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
        g_fig = render_average_gap(laps, session)
        if g_fig: plot_chart(g_fig, "gap_evolution")

    with c_right:
        st.markdown("<div class='reveal-card rd-2'><div class='section-sep' style='margin-top:8px;'><div class='section-sep-icon'><i class='fa-solid fa-gauge-high'></i></div><span class='section-sep-label'>Speed Trap</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
        ts_fig = render_top_speed(laps, session)
        if ts_fig: plot_chart(ts_fig, "tyre_stint")

    st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-stopwatch'></i></div><span class='section-sep-label'>Sector Times</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
    sec_mode = st.radio("SECTORS CALCULATION MODE", ["BEST", "AVERAGE", "MEDIAN"], horizontal=True)
    sec_fig = render_sectors_times(laps, session, sec_mode)
    if sec_fig: plot_chart(sec_fig, "sector_comparison")
    # 4. CONSISTENCY SCORE & LAP TIME DISTRIBUTION (race laps only)
    st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-chart-bar'></i></div><span class='section-sep-label'>Consistency & Distribution</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
    if filtered_laps_dict:
        render_consistency_score(session, list(filtered_laps_dict.keys()), race_mode=True, filtered_laps_dict=filtered_laps_dict)

    # 5. FUEL-CORRECTED PACE
    st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-gas-pump'></i></div><span class='section-sep-label'>Fuel-Corrected Pace</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
    if filtered_laps_dict:
        _fe_col1, _fe_col2 = st.columns([3, 1])
        with _fe_col2:
            fuel_effect = st.number_input(
                "FUEL EFFECT (s/lap)",
                min_value=0.010, max_value=0.150, value=0.065, step=0.005, format="%.3f",
                help="Typical F1: ~0.034s per kg × ~2kg/lap ≈ 0.065s/lap. Adjust for specific circuit.",
            )
        render_fuel_corrected_pace(filtered_laps_dict, session, max_laps, fuel_effect, _cmp_colors)

    # 6. HEAD-TO-HEAD CARD (2 drivers)
    if len([d for d in selected_drivers if d in filtered_laps_dict]) == 2:
        st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-bolt'></i></div><span class='section-sep-label'>Head-to-Head</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
        render_h2h_card(filtered_laps_dict, session, _cmp_colors)

    # 7. STINT DEGRADATION
    if filtered_laps_dict:
        st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-arrow-trend-down'></i></div><span class='section-sep-label'>Stint Degradation</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
        render_stint_degradation(filtered_laps_dict, session, _cmp_colors)

    # 8. TYRE CLIFF DETECTOR
    if filtered_laps_dict:
        st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-triangle-exclamation'></i></div><span class='section-sep-label'>Tyre Cliff Detector</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
        render_cliff_detector(filtered_laps_dict, session, _cmp_colors)

    # 9. POSITION TRACKER
    st.markdown("<div class='reveal-card rd-1'><div class='section-sep'><div class='section-sep-icon'><i class='fa-solid fa-arrow-up-9-1'></i></div><span class='section-sep-label'>Position Tracker</span><div class='section-sep-line'></div></div></div>", unsafe_allow_html=True)
    render_position_tracker(laps, session, list(filtered_laps_dict.keys()), _cmp_colors)