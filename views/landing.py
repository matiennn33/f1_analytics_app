import streamlit as st
import streamlit.components.v1 as components
from utils.components import render_navbar
from utils.i18n import t


def render():
    st.markdown(f"""
    <style>
        /* ── LOCAL KEYFRAMES ── */
        @keyframes ripple {{
            0%   {{ box-shadow: 0 0 0 0 rgba(33,197,94,0.42); opacity: 1; }}
            100% {{ box-shadow: 0 0 0 70px rgba(33,197,94,0); opacity: 0; }}
        }}
        @keyframes slow-breath {{
            0%,100% {{ transform: scale(1);     filter: brightness(1);    }}
            50%      {{ transform: scale(1.007); filter: brightness(1.04); }}
        }}
        @keyframes scanline {{
            0%   {{ top: -6px; opacity: 0; }}
            10%  {{ opacity: 1; }}
            90%  {{ opacity: 1; }}
            100% {{ top: 100%; opacity: 0; }}
        }}
        @keyframes bar-grow {{
            from {{ transform: scaleY(0); }}
            to   {{ transform: scaleY(1); }}
        }}
        @keyframes stagger-in {{
            from {{ opacity: 0; transform: translateY(30px) scale(0.97); }}
            to   {{ opacity: 1; transform: translateY(0)   scale(1); }}
        }}
        @keyframes count-in {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes grid-breathe {{
            0%,100% {{ opacity: 0.018; }}
            50%     {{ opacity: 0.038; }}
        }}
        @keyframes hero-line-in {{
            from {{ opacity: 0; transform: translateY(22px) skewY(1.5deg); }}
            to   {{ opacity: 1; transform: translateY(0)    skewY(0deg); }}
        }}
        @keyframes badge-pulse {{
            0%,100% {{ box-shadow: 0 0 0 0 rgba(33,197,94,0.35), 0 0 28px rgba(33,197,94,0.18); }}
            50%     {{ box-shadow: 0 0 0 8px rgba(33,197,94,0), 0 0 45px rgba(33,197,94,0.32); }}
        }}
        @keyframes orb-1 {{
            0%,100% {{ transform: translate(0,0) scale(1); }}
            40%     {{ transform: translate(60px,-40px) scale(1.08); }}
            70%     {{ transform: translate(-30px,25px) scale(0.94); }}
        }}
        @keyframes orb-2 {{
            0%,100% {{ transform: translate(0,0) scale(1); }}
            35%     {{ transform: translate(-50px,35px) scale(1.06); }}
            65%     {{ transform: translate(40px,-30px) scale(0.96); }}
        }}
        @keyframes orb-3 {{
            0%,100% {{ transform: translate(0,0) scale(1); }}
            45%     {{ transform: translate(35px,45px) scale(1.04); }}
            80%     {{ transform: translate(-45px,-20px) scale(0.97); }}
        }}
        @keyframes separator-grow {{
            from {{ width: 0; opacity: 0; }}
            to   {{ width: 100%; opacity: 1; }}
        }}
        @keyframes bento-shimmer {{
            0%   {{ transform: translateX(-130%) skewX(-20deg); }}
            100% {{ transform: translateX(230%) skewX(-20deg); }}
        }}

        /* ── BACKGROUND ORBS ── */
        .hero-orb {{
            position: fixed; border-radius: 50%; pointer-events: none; z-index: -1; filter: blur(90px);
        }}
        .hero-orb-1 {{
            width: 420px; height: 420px;
            background: radial-gradient(circle, rgba(33,197,94,0.095) 0%, transparent 70%);
            top: -100px; left: -80px;
            animation: orb-1 18s ease-in-out infinite;
        }}
        .hero-orb-2 {{
            width: 360px; height: 360px;
            background: radial-gradient(circle, rgba(33,197,94,0.07) 0%, transparent 70%);
            top: 200px; right: -100px;
            animation: orb-2 22s ease-in-out infinite;
        }}
        .hero-orb-3 {{
            width: 280px; height: 280px;
            background: radial-gradient(circle, rgba(13,148,136,0.06) 0%, transparent 70%);
            top: 500px; left: 20%;
            animation: orb-3 26s ease-in-out infinite;
        }}

        /* ── HERO BADGE ── */
        .saas-badge-container {{ position: relative; display: inline-block; margin-bottom: 40px; }}
        .saas-badge {{
            position: relative; z-index: 10;
            padding: 10px 28px;
            background: rgba(33,197,94,0.07) !important;
            border: 1px solid rgba(33,197,94,0.32);
            border-radius: 50px;
            color: #21C55E;
            font-family: 'Geist Mono', monospace; font-size: 0.76rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 2.5px;
            animation: badge-pulse 3.5s ease-in-out infinite;
        }}
        .wave {{ position: absolute; top:0;left:0;right:0;bottom:0; border-radius: 50px; animation: ripple 4.2s linear infinite; }}
        .wave2 {{ animation-delay: 1.4s; }}
        .wave3 {{ animation-delay: 2.8s; }}

        /* ── HERO TITLE ── */
        .hero-title-line1 {{
            display: block;
            animation: hero-line-in 0.8s 0.15s cubic-bezier(0.19,1,0.22,1) both;
        }}
        .hero-title-line2 {{
            display: block;
            background: linear-gradient(130deg, #21C55E 0%, #16a34a 55%, #0d9488 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 32px rgba(33,197,94,0.45));
            animation: hero-line-in 0.8s 0.32s cubic-bezier(0.19,1,0.22,1) both;
        }}
        .hero-desc-anim {{
            animation: hero-line-in 0.8s 0.52s cubic-bezier(0.19,1,0.22,1) both;
        }}

        /* ── MOCKUP ── */
        .hero-visual {{
            margin: 50px auto 0 auto; width: 100%; max-width: 1100px; height: 490px;
            background: linear-gradient(180deg, rgba(14,14,16,0.98) 0%, rgba(3,3,5,0.99) 100%);
            border: 1px solid #252528; border-radius: 20px;
            box-shadow: 0 50px 100px -24px rgba(0,0,0,0.98), 0 0 0 1px rgba(255,255,255,0.035), 0 0 80px rgba(33,197,94,0.04);
            display: flex; flex-direction: column; overflow: hidden; position: relative;
            animation: stagger-in 0.9s 0.55s cubic-bezier(0.19,1,0.22,1) both;
        }}
        .mockup-scanline {{
            position: absolute; top: -6px; left: 0; right: 0; height: 6px;
            background: linear-gradient(180deg, transparent 0%, rgba(33,197,94,0.22) 50%, transparent 100%);
            animation: scanline 5s ease-in-out infinite; pointer-events: none; z-index: 10;
        }}
        .mockup-header {{
            height: 42px; border-bottom: 1px solid #1c1c20; display: flex; align-items: center;
            padding: 0 20px; gap: 10px; background: rgba(4,4,6,0.92); flex-shrink: 0;
        }}
        .dot {{ width: 11px; height: 11px; border-radius: 50%; }}
        .mockup-body {{
            flex: 1; padding: 22px; display: grid; grid-template-columns: 2.2fr 1fr; gap: 20px;
            background-image:
                linear-gradient(rgba(33,197,94,0.016) 1px, transparent 1px),
                linear-gradient(90deg, rgba(33,197,94,0.016) 1px, transparent 1px);
            background-size: 32px 32px;
            animation: grid-breathe 9s ease-in-out infinite;
        }}
        .chart-box {{
            background: rgba(0,0,0,0.52); border: 1px solid #1c1c20; border-radius: 12px;
            position: relative; overflow: hidden; transition: border-color 0.3s ease;
        }}
        .chart-box:hover {{ border-color: rgba(33,197,94,0.15); }}
        .chart-bar {{
            position: absolute; bottom: 0; background: var(--bar-color, #21C55E);
            border-radius: 3px 3px 0 0; opacity: 0.7;
            transform-origin: bottom; animation: bar-grow 1.2s cubic-bezier(0.4,0,0.2,1) both;
        }}

        /* ── BENTO CARDS ── */
        .bento-card {{
            background: linear-gradient(145deg, rgba(18,18,20,0.92) 0%, rgba(10,10,12,0.97) 100%);
            border: 1px solid #222224; border-radius: 22px; padding: 40px;
            transition: all 0.5s cubic-bezier(0.4,0,0.2,1);
            position: relative; overflow: hidden;
        }}
        .bento-card::before {{
            content: ""; position: absolute; inset: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.022) 0%, transparent 55%);
            pointer-events: none; border-radius: inherit;
        }}
        .bento-card::after {{
            content: ""; position: absolute; top: 0; left: 0;
            width: 45%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(33,197,94,0.055), transparent);
            transform: translateX(-130%) skewX(-20deg); pointer-events: none;
        }}
        .bento-card:hover {{ transform: translateY(-14px) scale(1.008); border-color: rgba(33,197,94,0.45) !important; box-shadow: 0 32px 64px rgba(33,197,94,0.1), 0 0 0 1px rgba(33,197,94,0.16) !important; }}
        .bento-card:hover::after {{ animation: bento-shimmer 0.65s ease forwards; }}
        .bento-card:nth-child(1) {{ animation: stagger-in 0.7s 0.05s cubic-bezier(0.19,1,0.22,1) both; }}
        .bento-card:nth-child(2) {{ animation: stagger-in 0.7s 0.18s cubic-bezier(0.19,1,0.22,1) both; }}
        .bento-card:nth-child(3) {{ animation: stagger-in 0.7s 0.31s cubic-bezier(0.19,1,0.22,1) both; }}
        .bento-card:nth-child(4) {{ animation: stagger-in 0.7s 0.44s cubic-bezier(0.19,1,0.22,1) both; }}
        .bento-card:nth-child(5) {{ animation: stagger-in 0.7s 0.57s cubic-bezier(0.19,1,0.22,1) both; }}
        .bento-card:nth-child(6) {{ animation: stagger-in 0.7s 0.70s cubic-bezier(0.19,1,0.22,1) both; }}
        .bento-icon {{
            width: 50px; height: 50px; border-radius: 14px;
            background: rgba(33,197,94,0.07); border: 1px solid rgba(33,197,94,0.16);
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 26px; font-size: 1.3rem; color: #21C55E; transition: all 0.3s ease;
        }}
        .bento-card:hover .bento-icon {{
            background: rgba(33,197,94,0.12); border-color: rgba(33,197,94,0.3);
            box-shadow: 0 0 20px rgba(33,197,94,0.15);
        }}

        /* ── STATS ROW ── */
        .stats-row {{
            display: flex; align-items: center; justify-content: center; gap: 60px;
            margin: 80px auto 0 auto; max-width: 920px;
            padding: 40px 48px;
            background: rgba(6,6,8,0.7);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 24px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 8px 40px rgba(0,0,0,0.8);
            animation: stagger-in 0.8s 0.65s cubic-bezier(0.19,1,0.22,1) both;
        }}
        .stat-item {{ text-align: center; }}
        .stat-number {{
            font-family: 'Geist Mono', monospace; font-size: 2.9rem; font-weight: 900;
            color: #f4f4f5; line-height: 1; text-shadow: 0 0 30px rgba(255,255,255,0.08);
        }}
        .stat-number span {{ color: #21C55E; text-shadow: 0 0 20px rgba(33,197,94,0.5); }}
        .stat-label {{
            font-family: 'Space Grotesk', sans-serif; font-size: 0.76rem;
            color: #52525b; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 8px;
        }}
        .stat-sep {{
            width: 1px; height: 65px;
            background: linear-gradient(180deg, transparent, rgba(58,58,63,0.8), transparent);
        }}

        /* ── SECTION SEPARATOR ── */
        .section-sep {{
            height: 1px; max-width: 900px; margin: 90px auto 0 auto;
            background: linear-gradient(90deg, transparent, rgba(33,197,94,0.18) 30%, rgba(33,197,94,0.18) 70%, transparent);
        }}
        .section-label-row {{
            text-align: center; margin: 60px 0 48px 0;
            animation: count-in 0.7s 0.35s cubic-bezier(0.19,1,0.22,1) both;
        }}
        .section-badge {{
            display: inline-flex; align-items: center; gap: 9px;
            background: rgba(33,197,94,0.06); border: 1px solid rgba(33,197,94,0.2);
            border-radius: 99px; padding: 8px 22px;
            font-family: 'Geist Mono', monospace; font-size: 0.68rem; font-weight: 700;
            color: #21C55E; letter-spacing: 2px; text-transform: uppercase;
        }}

        /* ── FOOTER ── */
        .landing-footer {{
            text-align: center; margin: 20px 0 36px 0; padding: 24px;
            border-top: 1px solid rgba(255,255,255,0.04);
        }}
        .landing-credits {{
            font-family: 'Geist Mono', monospace; font-size: 0.7rem;
            letter-spacing: 1.4px; text-transform: uppercase; color: #3a3a3f;
        }}
        .landing-credits span {{ color: #71717a; }}
    </style>
    """, unsafe_allow_html=True)

    # ── Background orbs ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-orb hero-orb-1"></div>
    <div class="hero-orb hero-orb-2"></div>
    <div class="hero-orb hero-orb-3"></div>
    """, unsafe_allow_html=True)

    render_navbar("landing")

    # ── HERO ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-section" style="text-align:center; margin-top:60px; padding:0 16px;">
        <div class="saas-badge-container">
            <div class="wave"></div><div class="wave wave2"></div><div class="wave wave3"></div>
            <div class="saas-badge">
                <i class="fa-solid fa-circle-dot" style="margin-right:8px; font-size:0.65rem; animation:blink-dot 1.6s infinite;"></i>
                {t("badge")}
            </div>
        </div>
        <div style="font-family:'Geist Mono',monospace; font-size:clamp(3.4rem,7vw,6.4rem); font-weight:900; text-transform:uppercase; margin:0 0 10px 0; color:#f4f4f5; line-height:1.02; letter-spacing:-0.01em;">
            <span class="hero-title-line1">{t("hero_line1")}</span>
            <span class="hero-title-line2">{t("hero_line2")}</span>
        </div>
        <p class="hero-desc-anim" style="font-family:'Space Grotesk',sans-serif; font-size:1.18rem; color:#71717a; max-width:720px; margin:0 auto 54px auto; line-height:1.7;">
            {t("hero_desc")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA Button ───────────────────────────────────────────────────────────
    if st.button(t("cta_btn"), type="primary", key="cta_main"):
        st.session_state["current_route"] = "dashboard"
        st.rerun()

    # ── MOCKUP ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-visual">
        <div class="mockup-scanline"></div>
        <div class="mockup-header">
            <div class="dot" style="background:#ff5f57;"></div>
            <div class="dot" style="background:#ffbd2e;"></div>
            <div class="dot" style="background:#27c93f;"></div>
            <span style="margin-left:18px; font-family:'Geist Mono',monospace; color:#4a4a52; font-size:0.78rem; letter-spacing:1.2px;">
                <i class="fa-solid fa-terminal" style="margin-right:8px; color:#3a3a3f;"></i>lc_telemetry_uplink.sys
            </span>
            <span style="margin-left:auto; font-family:'Geist Mono',monospace; color:#21C55E; font-size:0.66rem; letter-spacing:1px;">
                <i class="fa-circle fa-solid" style="font-size:0.42rem; margin-right:6px; animation:blink-dot 1.6s infinite;"></i>LIVE
            </span>
        </div>
        <div class="mockup-body">
            <div class="chart-box">
                <div style="padding:10px 16px; font-family:'Geist Mono',monospace; color:#4a4a52; font-size:0.7rem; border-bottom:1px solid #161618; background:rgba(0,0,0,0.65); display:flex; align-items:center; gap:10px;">
                    <i class="fa-solid fa-wave-square" style="color:#21C55E;"></i>
                    {t("mockup_stream")}
                    <span style="margin-left:auto; color:#333336;">Hz: 100</span>
                </div>
                <div style="position:absolute; bottom:58px; left:-5%; width:110%; height:2px; background:linear-gradient(90deg,transparent,#21C55E,transparent); box-shadow:0 0 18px #21C55E; transform:rotate(-6deg); animation:slow-breath 4s infinite;"></div>
                <div style="position:absolute; bottom:98px; left:-5%; width:110%; height:1.5px; background:linear-gradient(90deg,transparent,rgba(239,68,68,0.7),transparent); transform:rotate(-2.5deg);"></div>
                <div style="position:absolute; bottom:28px; left:-5%; width:110%; height:1px; background:linear-gradient(90deg,transparent,rgba(59,130,246,0.5),transparent); transform:rotate(-4deg);"></div>
                <div style="position:absolute; bottom:14px; left:20px; display:flex; gap:16px; align-items:center;">
                    <span style="font-family:'Geist Mono',monospace; font-size:0.58rem; color:#21C55E; letter-spacing:0.8px;">VER</span>
                    <span style="font-family:'Geist Mono',monospace; font-size:0.58rem; color:#ef4444; letter-spacing:0.8px;">LEC</span>
                    <span style="font-family:'Geist Mono',monospace; font-size:0.58rem; color:#3b82f6; letter-spacing:0.8px;">HAM</span>
                </div>
            </div>
            <div style="display:flex; flex-direction:column; gap:16px;">
                <div class="chart-box" style="flex:1.2; display:flex; align-items:center; justify-content:center; background:radial-gradient(circle, rgba(33,197,94,0.09) 0%, transparent 65%);">
                    <div style="text-align:center;">
                        <div style="width:76px; height:76px; border-radius:50%; border:3px solid #1c1c20; border-top-color:#21C55E; border-right-color:#21C55E; transform:rotate(-45deg); margin:0 auto;"></div>
                        <div style="font-family:'Geist Mono',monospace; font-size:0.6rem; color:#4a4a52; margin-top:12px; letter-spacing:1px;">SECTOR LOSS</div>
                    </div>
                </div>
                <div class="chart-box" style="flex:1; padding:16px 18px; display:flex; flex-direction:column; justify-content:center; gap:4px;">
                    <div style="font-family:'Geist Mono',monospace; color:#4a4a52; font-size:0.6rem; text-transform:uppercase; letter-spacing:1.2px;">S1 Delta</div>
                    <div style="font-family:'Geist Mono',monospace; color:#ef4444; font-size:1.9rem; font-weight:800; line-height:1;">+0.124s</div>
                    <div style="height:2px; background:linear-gradient(90deg,#ef4444,transparent); border-radius:99px; margin-top:4px;"></div>
                </div>
                <div class="chart-box" style="flex:0.8; padding:13px 16px; display:flex; align-items:center; gap:13px;">
                    <div style="width:8px; height:8px; border-radius:50%; background:#21C55E; box-shadow:0 0 8px #21C55E; animation:blink-dot 1.6s infinite; flex-shrink:0;"></div>
                    <div>
                        <div style="font-family:'Geist Mono',monospace; color:#4a4a52; font-size:0.56rem; text-transform:uppercase; letter-spacing:1px;">{t("mockup_uplink_label")}</div>
                        <div style="font-family:'Geist Mono',monospace; color:#21C55E; font-size:0.78rem; font-weight:700; letter-spacing:0.5px;">{t("mockup_uplink_status")}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STATS ROW ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-item">
            <div class="stat-number" id="cnt-gp">100<span>+</span></div>
            <div class="stat-label">{t("stat_1_label")}</div>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
            <div class="stat-number" id="cnt-dp">18<span>k</span></div>
            <div class="stat-label">{t("stat_2_label")}</div>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
            <div class="stat-number" id="cnt-mod">4</div>
            <div class="stat-label">{t("stat_3_label")}</div>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
            <div class="stat-number"><span>&lt;</span>1ms</div>
            <div class="stat-label">{t("stat_4_label")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION SEPARATOR ────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-sep"></div>
    <div class="section-label-row">
        <div class="section-badge">
            <i class="fa-solid fa-layer-group"></i>
            Analysis Modules
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── BENTO GRID ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:26px; max-width:1280px; margin:0 auto 90px auto; padding:0 16px;">
        <div class="bento-card">
            <div class="bento-icon"><i class="fa-solid fa-gauge-high"></i></div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; margin-bottom:14px; font-size:1.22rem; font-weight:700;">{t("bento_1_title")}</h3>
            <p style="color:#71717a; font-family:'Space Grotesk',sans-serif; line-height:1.65; font-size:0.93rem;">{t("bento_1_desc")}</p>
        </div>
        <div class="bento-card">
            <div class="bento-icon"><i class="fa-solid fa-fire-flame-curved"></i></div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; margin-bottom:14px; font-size:1.22rem; font-weight:700;">{t("bento_2_title")}</h3>
            <p style="color:#71717a; font-family:'Space Grotesk',sans-serif; line-height:1.65; font-size:0.93rem;">{t("bento_2_desc")}</p>
        </div>
        <div class="bento-card">
            <div class="bento-icon"><i class="fa-solid fa-map-location-dot"></i></div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; margin-bottom:14px; font-size:1.22rem; font-weight:700;">{t("bento_3_title")}</h3>
            <p style="color:#71717a; font-family:'Space Grotesk',sans-serif; line-height:1.65; font-size:0.93rem;">{t("bento_3_desc")}</p>
        </div>
        <div class="bento-card">
            <div class="bento-icon"><i class="fa-solid fa-sliders"></i></div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; margin-bottom:14px; font-size:1.22rem; font-weight:700;">{t("bento_4_title")}</h3>
            <p style="color:#71717a; font-family:'Space Grotesk',sans-serif; line-height:1.65; font-size:0.93rem;">{t("bento_4_desc")}</p>
        </div>
        <div class="bento-card">
            <div class="bento-icon"><i class="fa-solid fa-code-compare"></i></div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; margin-bottom:14px; font-size:1.22rem; font-weight:700;">{t("bento_5_title")}</h3>
            <p style="color:#71717a; font-family:'Space Grotesk',sans-serif; line-height:1.65; font-size:0.93rem;">{t("bento_5_desc")}</p>
        </div>
        <div class="bento-card">
            <div class="bento-icon"><i class="fa-solid fa-bolt"></i></div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; margin-bottom:14px; font-size:1.22rem; font-weight:700;">{t("bento_6_title")}</h3>
            <p style="color:#71717a; font-family:'Space Grotesk',sans-serif; line-height:1.65; font-size:0.93rem;">{t("bento_6_desc")}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FOOTER ───────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="landing-footer"><div class="landing-credits">'
        f'{t("footer_by")} <span>Mattia Russo</span> — {t("footer_platform")}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── JAVASCRIPT: count-up animation ───────────────────────────────────────
    components.html("""
<script>
(function() {
    var doc = (window.parent || window).document;
    function countUp(id, target, suf, delay) {
        setTimeout(function() {
            var el = doc.getElementById(id);
            if (!el) return;
            var t0 = performance.now(), dur = 1500;
            function ease(t) { return 1 - Math.pow(1-t, 3); }
            function step(now) {
                var p = Math.min((now - t0) / dur, 1);
                el.innerHTML = Math.round(ease(p) * target) + '<span>' + suf + '</span>';
                if (p < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        }, delay);
    }
    function init() {
        if (!doc.getElementById('cnt-gp')) { return setTimeout(init, 400); }
        countUp('cnt-gp',  100, '+', 200);
        countUp('cnt-dp',  18,  'k', 380);
        countUp('cnt-mod', 4,   '',  560);
    }
    if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init);
    else setTimeout(init, 200);
})();
</script>
""", height=0, scrolling=False)
