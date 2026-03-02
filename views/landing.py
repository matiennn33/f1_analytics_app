import streamlit as st
import base64
import os

def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def render():
    logo_b64 = get_base64_img("logo.png")
    logo_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

    st.markdown(f"""
    <style>
        /* =========================================
           1. ANIMAZIONI (TRIPLE RIPPLE & SLOW BREATH)
           ========================================= */
        @keyframes ripple {{
            0% {{ box-shadow: 0 0 0 0 rgba(33, 197, 94, 0.4); opacity: 1; }}
            100% {{ box-shadow: 0 0 0 60px rgba(33, 197, 94, 0); opacity: 0; }}
        }}

        @keyframes slow-breathing {{
            0%, 100% {{ transform: scale(1); filter: brightness(1); }}
            50% {{ transform: scale(1.006); filter: brightness(1.02); }}
        }}

        /* =========================================
           2. HEADER BAR (HEIGHT 100PX & TEXT BUTTONS)
           ========================================= */
        div[data-testid="stHorizontalBlock"]:first-of-type {{
            background: #121212 !important; 
            border: 1px solid #27272a !important; 
            border-radius: 30px !important;
            padding: 30px 40px !important; 
            width: 100% !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        }}

        /* Posizionamento Logo */
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:first-child {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            height: 100% !important;
        }}

        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"] > div {{
            display: flex !important;
            align-items: center !important;
            height: 100% !important;
        }}

        div[data-testid="stHorizontalBlock"]:first-of-type img {{
            height: 52px !important;
            display: block !important;
            position: relative !important;
            top: -7.5px !important;
        }}

        /* Header Buttons: Solo Testo, no container */
        html body div.stApp div[data-testid="stHorizontalBlock"]:first-of-type div.stButton > button {{
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            transform: none !important;
            padding: 0 !important;
            width: auto !important;
            min-height: 0 !important;
        }}
        
        html body div.stApp div[data-testid="stHorizontalBlock"]:first-of-type div.stButton > button p {{
            color: #a1a1aa !important;
            font-family: 'Geist Mono', monospace !important;
            font-size: 0.9rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            transition: color 0.3s ease, text-shadow 0.3s ease !important;
        }}

        html body div.stApp div[data-testid="stHorizontalBlock"]:first-of-type div.stButton > button:hover p {{
            color: #ffffff !important;
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.4) !important;
        }}

        /* =========================================
           3. HERO & BADGE (3 ONDE + SLOW BREATH)
           ========================================= */
        .saas-badge-container {{
            position: relative;
            display: inline-block;
            margin-bottom: 45px;
        }}

        .saas-badge {{
            position: relative;
            z-index: 10;
            padding: 12px 28px;
            background: rgba(33, 197, 94, 0.09) !important;
            border: 1px solid rgba(33, 197, 94, 0.4);
            border-radius: 50px;
            color: #21C55E;
            font-family: 'Geist Mono', monospace;
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 22px rgba(33, 197, 94, 0.25), inset 0 0 18px rgba(33, 197, 94, 0.12);
            animation: slow-breathing 14s ease-in-out infinite;
        }}

        .wave {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 50px;
            animation: ripple 4s linear infinite;
        }}
        .wave2 {{ animation-delay: 1.3s; }}
        .wave3 {{ animation-delay: 2.6s; }}

        .hero-title span {{
            background: linear-gradient(135deg, #21C55E 0%, #047857 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 30px rgba(33, 197, 94, 0.5));
        }}

        /* =========================================
           4. MOCKUP CARD (lc_telemetry_uplink.exe)
           ========================================= */
        .hero-visual {{ 
            margin: 60px auto 0 auto; width: 100%; max-width: 1050px; height: 480px; 
            background: linear-gradient(180deg, rgba(18,18,18,0.95) 0%, rgba(5,5,5,0.98) 100%); 
            border: 1px solid #3f3f46; border-radius: 16px; 
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.9); 
            display: flex; flex-direction: column; overflow: hidden; 
        }}
        .mockup-header {{ height: 40px; border-bottom: 1px solid #27272a; display: flex; align-items: center; padding: 0 20px; gap: 10px; background: #0a0a0a; }}
        .dot {{ width: 11px; height: 11px; border-radius: 50%; }}
        .mockup-body {{ flex: 1; padding: 25px; display: grid; grid-template-columns: 2fr 1fr; gap: 25px; background-image: linear-gradient(rgba(33, 197, 94, 0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(33, 197, 94, 0.02) 1px, transparent 1px); background-size: 30px 30px; }}
        .chart-box {{ background: rgba(0,0,0,0.4); border: 1px solid #27272a; border-radius: 10px; position: relative; overflow: hidden; }}

        /* Hover Bento Cards */
        .bento-card {{
            background: rgba(18, 18, 18, 0.7);
            border: 1px solid #27272a;
            border-radius: 20px;
            padding: 40px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .bento-card:hover {{
            transform: translateY(-15px);
            border-color: #21C55E !important;
            box-shadow: 0 25px 50px rgba(33, 197, 94, 0.2) !important;
        }}

        .landing-credits {{
            text-align: center;
            margin: 10px 0 24px 0;
            font-family: 'Geist Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: #71717a;
        }}
        .landing-credits span {{
            color: #d4d4d8;
        }}
    </style>
    """, unsafe_allow_html=True)

    # --- NAVBAR ---
    nav_cols = st.columns([7.5, 1.2, 1.3], vertical_alignment="center")
    with nav_cols[0]:
        st.markdown(f'<img src="{logo_src}">', unsafe_allow_html=True)
    with nav_cols[1]:
        if st.button("Architecture", key="nav_arch"): 
            st.session_state['current_route'] = 'architecture'
            st.rerun()
    with nav_cols[2]:
        if st.button("Documentation", key="nav_doc"): 
            st.session_state['current_route'] = 'documentation'
            st.rerun()

    # --- HERO ---
    st.markdown(f"""
    <div class="hero-section" style="text-align: center; margin-top: 50px;">
        <div class="saas-badge-container">
            <div class="wave wave1"></div>
            <div class="wave wave2"></div>
            <div class="wave wave3"></div>
            <div class="saas-badge">High-Performance Analytics</div>
        </div>
        <h1 class="hero-title" style="font-family: 'Geist Mono'; font-size: 6.5rem; font-weight: 900; text-transform: uppercase; margin-bottom: 25px; color: #fff;">
            Dominating<br><span>Telemetry Data</span>
        </h1>
        <p style="font-family: 'Space Grotesk'; font-size: 1.3rem; color: #a1a1aa; max-width: 850px; margin: 0 auto 50px auto; line-height: 1.6;">
            Progettata per l'ottimizzazione assoluta. Analizza le metriche, decodifica il limite del veicolo e trasforma i dati grezzi in un vantaggio competitivo netto.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("INITIALIZE UPLINK", type="primary"):
        st.session_state['current_route'] = 'dashboard'
        st.rerun()

    # --- MOCKUP (REINTEGRATO) ---
    st.markdown("""
    <div class="hero-visual">
        <div class="mockup-header">
            <div class="dot" style="background: #ff5f57;"></div>
            <div class="dot" style="background: #ffbd2e;"></div>
            <div class="dot" style="background: #27c93f;"></div>
            <span style="margin-left: 15px; font-family: 'Geist Mono', monospace; color: #52525b; font-size: 0.85rem; letter-spacing: 1px;">lc_telemetry_uplink.exe</span>
        </div>
        <div class="mockup-body">
            <div class="chart-box">
                <div style="padding: 12px 18px; font-family: 'Geist Mono', monospace; color: #71717a; font-size: 0.75rem; border-bottom: 1px solid #27272a; background: rgba(0,0,0,0.5);">
                    <i class="fa-solid fa-wave-square" style="margin-right: 10px; color: #21C55E;"></i> LIVE_TELEMETRY_STREAM [Hz: 100]
                </div>
                <div style="position: absolute; bottom: 50px; left: -5%; width: 110%; height: 2px; background: #21C55E; box-shadow: 0 0 15px #21C55E; transform: rotate(-8deg);"></div>
                <div style="position: absolute; bottom: 90px; left: -5%; width: 110%; height: 2px; background: rgba(239, 68, 68, 0.6); transform: rotate(-2deg);"></div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div class="chart-box" style="flex: 1.2; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(33,197,94,0.12) 0%, transparent 70%);">
                    <div style="width: 85px; height: 85px; border-radius: 50%; border: 5px solid #27272a; border-top-color: #21C55E; border-right-color: #21C55E; transform: rotate(-45deg);"></div>
                </div>
                <div class="chart-box" style="flex: 1; padding: 20px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-family: 'Geist Mono', monospace; color: #71717a; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">S1 Delta</div>
                    <div style="font-family: 'Geist Mono', monospace; color: #ef4444; font-size: 2rem; font-weight: 800;">+0.124s</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- BENTO GRID ---
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 35px; max-width: 1300px; margin: 120px auto; padding: 0 20px;">
        <div class="bento-card">
            <i class="fa-solid fa-gauge-high" style="font-size: 2.5rem; color: #21C55E; margin-bottom: 25px; display: block;"></i>
            <h3 style="font-family: 'Geist Mono'; color: #fff; margin-bottom: 15px; font-size: 1.5rem;">Vehicle Dynamics</h3>
            <p style="color: #71717a; font-family: 'Space Grotesk'; line-height: 1.6;">Analisi millimetrica degli input pedaliera e bilanciamento aero-meccanico.</p>
        </div>
        <div class="bento-card">
            <i class="fa-solid fa-fire-flame-curved" style="font-size: 2.5rem; color: #21C55E; margin-bottom: 25px; display: block;"></i>
            <h3 style="font-family: 'Geist Mono'; color: #fff; margin-bottom: 15px; font-size: 1.5rem;">Thermal Degradation</h3>
            <p style="color: #71717a; font-family: 'Space Grotesk'; line-height: 1.6;">Modelli predittivi sul consumo gomma e regressione statistica del passo gara.</p>
        </div>
        <div class="bento-card">
            <i class="fa-solid fa-map-location-dot" style="font-size: 2.5rem; color: #21C55E; margin-bottom: 25px; display: block;"></i>
            <h3 style="font-family: 'Geist Mono'; color: #fff; margin-bottom: 15px; font-size: 1.5rem;">Spatial Domain</h3>
            <p style="color: #71717a; font-family: 'Space Grotesk'; line-height: 1.6;">Mappatura micro-settoriale per identificare perdite di performance croniche.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="landing-credits">Powered by <span>Mattia Russo</span></div>', unsafe_allow_html=True)
