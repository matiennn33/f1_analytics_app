import streamlit as st

def inject_global_css():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" crossorigin="anonymous">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" crossorigin="anonymous">
    <style>
        :root { --bg-card: #121212; --border: #27272a; --text-m: #71717a; --text-w: #ffffff; --accent: #21C55E; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #71717a; }
        .stApp { background-color: #0a0a0a; font-family: 'Space Grotesk', sans-serif !important; font-weight: 400 !important; }
        footer {visibility: hidden;}
        .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; max-width: 95% !important; }
        /* Header bar + logo alignment */
        div[data-testid="stHorizontalBlock"]:first-of-type {
            padding: 30px 40px !important;
        }
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:first-child,
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:first-child > div {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"] > div {
            display: flex !important;
            align-items: center !important;
            height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:first-child img {
            display: block !important;
            margin: 0 !important;
            position: relative !important;
            top: -7.5px !important;
        }
        h1, .stMarkdown h1 { font-family: 'Geist Mono', monospace !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 2px !important; color: var(--text-w) !important; }
        h2, h3, h4, h5, h6, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 { font-family: 'Geist Mono', monospace !important; font-weight: 500 !important; color: var(--text-w) !important; }
        .stWidgetLabel p, label p, [data-testid="stWidgetLabel"] p { font-family: 'Geist Mono', monospace !important; font-weight: 500 !important; color: #8f8f9d !important; font-size: 0.75rem !important; text-transform: uppercase !important; letter-spacing: 0.8px !important; margin-bottom: 8px !important; }
        
        /* =========================================
           BOTTONI GLOBALI (SECONDARY)
           ========================================= */
        button[kind="secondary"] {
            width: 100% !important;
            border-radius: 8px !important;
            background: linear-gradient(180deg, #1a1a1c 0%, #121212 100%) !important;
            border: 1px solid #3f3f46 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
            padding: 6px 12px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
        }
        button[kind="secondary"] p {
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 500 !important; 
            color: #ffffff !important;
            font-size: 0.95rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin: 0 !important;
        }
        button[kind="secondary"]:hover {
            background: linear-gradient(180deg, #27272a 0%, #1a1a1c 100%) !important;
            border-color: var(--accent) !important;
            box-shadow: 0 0 20px rgba(33, 197, 94, 0.2) !important;
            transform: translateY(-2px) !important; 
        }
        button[kind="secondary"]:hover p { color: var(--accent) !important; }
        button[kind="secondary"]:active { transform: translateY(2px) scale(0.98) !important; }

        /* =========================================
           BOTTONE PRIMARY (CTA FIGMA STYLE) - ISOLATO E CENTRATO
           ========================================= */
        /* Contenitori Streamlit Forzati al Centro */
        div.element-container:has(button[kind="primary"]),
        div[data-testid="stButton"]:has(button[kind="primary"]) {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            margin-top: 10px !important;
            margin-bottom: 50px !important;
        }

        button[kind="primary"] {
            all: unset !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            
            /* Nuovo Gradiente: Rosso in alto a sx verso il nero in basso a dx */
            background: linear-gradient(135deg, rgba(160, 25, 25, 0.95) 0%, rgba(30, 30, 30, 1) 45%, rgba(15, 15, 15, 1) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 14px !important;
            height: 75px !important;
            width: 380px !important; 
            max-width: 90vw !important;
            box-shadow: 0 12px 30px rgba(0,0,0,0.6), inset 0 1px 1px rgba(255,255,255,0.15) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            margin: 0 auto !important; /* Forza il centro */
        }
        
        button[kind="primary"] p {
            color: #ffffff !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.3rem !important; 
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.3) !important;
        }

        /* Icona FontAwesome BIANCA */
        button[kind="primary"] p::before {
            content: "\\f0e7";
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            margin-right: 14px;
            color: #ffffff !important; /* FORZATO A BIANCO */
            font-size: 1.4rem !important;
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.3) !important;
        }
        
        button[kind="primary"]:hover {
            transform: translateY(-4px) !important;
            background: linear-gradient(135deg, rgba(200, 35, 35, 1) 0%, rgba(45, 45, 45, 1) 45%, rgba(20, 20, 20, 1) 100%) !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8), 0 0 20px rgba(255,255,255,0.05) !important;
            border-color: rgba(255, 255, 255, 0.3) !important;
        }
        button[kind="primary"]:active { transform: translateY(2px) scale(0.98) !important; }

        /* =========================================
           RESTO DEL CSS GLOBALE
           ========================================= */
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a0a 0%, #121212 100%) !important; border-right: 1px solid var(--border) !important; padding-top: 1rem !important; }
        [data-testid="stTabs"] { margin-bottom: 20px; }
        [data-testid="stTabs"] [data-baseweb="tab-list"] { background-color: #121212 !important; border: 1px solid #27272a !important; border-radius: 12px !important; padding: 6px !important; gap: 0px !important; z-index: 0; }
        [data-testid="stTabs"] [data-baseweb="tab"] { background-color: transparent !important; border: none !important; padding: 12px 24px !important; z-index: 2 !important; }
        html body .stApp [data-testid="stTabs"] [data-baseweb="tab"] p { font-family: 'Geist Mono', monospace !important; font-weight: 500 !important; font-size: 0.85rem !important; color: #71717a !important; text-transform: uppercase !important; margin: 0 !important; transition: color 0.3s ease !important; }
        html body .stApp [data-testid="stTabs"] [data-baseweb="tab"]:hover p, html body .stApp [data-testid="stTabs"] [aria-selected="true"] p { color: #ffffff !important; }
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #1f1f22 !important; border: 1px solid #3f3f46 !important; border-radius: 8px !important; height: calc(100% - 12px) !important; top: 6px !important; z-index: 1 !important; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), width 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important; }
        [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
        [data-testid="stTabs"] [data-baseweb="tab"] p::before { font-family: "Font Awesome 6 Free" !important; font-weight: 900 !important; margin-right: 8px !important; display: inline-block; }
        [data-testid="stTabs"] > div > div > div > [data-baseweb="tab"]:nth-child(1) p::before { content: "\\f080"; color: var(--accent) !important; }
        [data-testid="stTabs"] > div > div > div > [data-baseweb="tab"]:nth-child(2) p::before { content: "\\f2f2"; color: var(--accent) !important; }
        [data-testid="stTabs"] > div > div > div > [data-baseweb="tab"]:nth-child(3) p::before { content: "\\f11e"; color: var(--accent) !important; }
        div[data-baseweb="select"] > div { background-color: #0d0d0d !important; border: 1px solid #27272a !important; border-radius: 8px !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5) !important; transition: border-color 0.3s ease, box-shadow 0.3s ease !important; }
        div[data-baseweb="select"] > div:hover, div[data-baseweb="select"] > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 10px rgba(33, 197, 94, 0.15) !important; }
        div[data-baseweb="select"] div, div[data-baseweb="popover"] li { font-family: 'Space Grotesk', sans-serif !important; font-weight: 400 !important; color: var(--text-w) !important; font-size: 0.9rem !important; }
        div[data-baseweb="popover"] ul { background-color: rgba(18, 18, 18, 0.9) !important; backdrop-filter: blur(16px) !important; border: 1px solid #3f3f46 !important; border-radius: 10px !important; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8) !important; }
        div[data-baseweb="popover"] li:hover { background-color: #27272a !important; color: var(--accent) !important; }
        div[data-baseweb="select"] span[data-baseweb="tag"] { background-color: rgba(33, 197, 94, 0.1) !important; color: var(--accent) !important; font-family: 'Geist Mono', monospace !important; font-weight: 500 !important; border-radius: 6px !important; border: 1px solid rgba(33, 197, 94, 0.3) !important; padding: 4px 10px !important; }
        div[data-testid="stExpander"] { background-color:#121212 !important; border:1px solid #27272a !important; border-radius:12px !important; }
        div[data-testid="stExpander"] summary { padding:15px 20px !important; border-bottom:1px solid rgba(255,255,255,0.05) !important; }
        div[data-testid="stExpander"] summary p { font-family:'Geist Mono', monospace !important; font-size:1.05rem !important; font-weight:500 !important; color:#ffffff !important; }
        div[data-testid="stExpander"] summary p::before { content:"\\f0b0"; font-family:"Font Awesome 6 Free"; font-weight:900; margin-right:10px; color:var(--accent); display: inline-block; }
        div[data-testid="stExpanderDetails"] { padding:20px !important; background-color:#0a0a0a !important; }
        .f1-card { background-color: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 20px; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease; }
        .f1-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5); border-color: #3f3f46 !important; }
                            @keyframes reveal {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .hero-section {
                animation: reveal 1s cubic-bezier(0.19, 1, 0.22, 1);
            }
        @keyframes pulse-glow { 0% { box-shadow: 0 0 0 0 rgba(33, 197, 94, 0.4); transform: scale(1); } 70% { box-shadow: 0 0 0 20px rgba(33, 197, 94, 0); transform: scale(1.05); } 100% { box-shadow: 0 0 0 0 rgba(33, 197, 94, 0); transform: scale(1); } }
        .radar-icon-animated { animation: pulse-glow 2s infinite cubic-bezier(0.4, 0, 0.2, 1); border-radius: 50%; background-color: rgba(33, 197, 94, 0.05); padding: 20px; }
        [data-testid="stAlert"] p, [data-testid="stToast"] p, [data-testid="stSpinner"], [data-testid="stNotificationContent"] { font-family: 'Space Grotesk', sans-serif !important; font-weight: 500; letter-spacing: 0.2px; }
    </style>
    """, unsafe_allow_html=True)
