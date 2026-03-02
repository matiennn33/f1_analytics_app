import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plotting import get_driver_color, apply_plotly_style
from utils.session_store import get_cached_laps

BG_CARD = "#121212"
BORDER = "#27272a"
TEXT_M = "#a1a1aa" 
TEXT_W = "#ffffff"

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
    html_card = f"""<div style="background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
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
<div style="background: #0a0a0a; border: 1px solid #1a1a1c; padding: 20px; border-radius: 8px;">
<h4 style="color: #ffffff; font-family: 'Geist Mono', monospace; font-size: 0.95rem; margin-top: 0; margin-bottom: 12px;"><i class="fa-solid fa-fire-flame-curved" style="color: #ef4444; margin-right: 8px;"></i> THERMAL DROP-OFF & CONSISTENCY</h4>
<p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin-bottom: 12px;">{deg_text}</p>
<p style="color: #d4d4d8; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; line-height: 1.6; margin: 0;">{cons_text}</p>
</div>
<div style="background: #0a0a0a; border: 1px solid #1a1a1c; padding: 20px; border-radius: 8px;">
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
    return apply_plotly_style(fig, "AVERAGE RACE PACE GAP")


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
    return apply_plotly_style(fig, "SPEED TRAP (MAXIMUM SPEED)")


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
    
    fig = apply_plotly_style(fig, title)
    fig.update_traces(textfont_size=6, textfont_family="Space Grotesk", constraintext='none', cliponaxis=False)
    
    return fig


def render_driver_pace(filtered_laps_dict, session):
    fig = go.Figure()
    for drv, drv_laps in filtered_laps_dict.items():
        color = get_driver_color(drv, session)
        
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
    
    return apply_plotly_style(fig, "RACE PACE & DEGRADATION")


def render(session):
    st.markdown("### <i class='fa-solid fa-flag-checkered'></i> Race History", unsafe_allow_html=True)
    
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
    
    # 2. RENDER MOTORE DI ANALISI STRUTTURALE SUI DATI FILTRATI
    if len(filtered_laps_dict) >= 2:
        render_structural_race_debrief(filtered_laps_dict)
    elif len(filtered_laps_dict) == 1:
        st.info("Seleziona almeno 2 piloti e assicurati che abbiano giri validi nel range indicato per abilitare il Debriefing.")

    # 3. RENDER RACE PACE CHART
    st.markdown(f"<div class='f1-card' style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; padding:15px; margin-bottom:20px;'>", unsafe_allow_html=True)
    if filtered_laps_dict:
        pace_fig = render_driver_pace(filtered_laps_dict, session)
        if pace_fig: st.plotly_chart(pace_fig, width="stretch")
    else: 
        st.warning("Nessun giro valido trovato per i piloti e i filtri selezionati.")
    st.markdown("</div>", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown(f"<div class='f1-card' style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; padding:15px; margin-bottom:20px;'>", unsafe_allow_html=True)
        g_fig = render_average_gap(laps, session)
        if g_fig: st.plotly_chart(g_fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown(f"<div class='f1-card' style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; padding:15px; margin-bottom:20px;'>", unsafe_allow_html=True)
        ts_fig = render_top_speed(laps, session)
        if ts_fig: st.plotly_chart(ts_fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='f1-card' style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; padding:15px;'>", unsafe_allow_html=True)
    
    sec_mode = st.radio("SECTORS CALCULATION MODE", ["BEST", "AVERAGE", "MEDIAN"], horizontal=True)
    sec_fig = render_sectors_times(laps, session, sec_mode)
    if sec_fig: st.plotly_chart(sec_fig, width="stretch")
    
    st.markdown("</div>", unsafe_allow_html=True)
