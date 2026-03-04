import streamlit as st
from utils.components import render_navbar


def render():
    render_navbar("documentation")

    st.markdown("""
    <style>
        .doc-card {
            background: linear-gradient(145deg, #141416 0%, #0e0e10 100%);
            border: 1px solid #232326; border-radius: 16px; padding: 28px 32px;
            margin-bottom: 16px; position: relative; overflow: hidden;
            transition: border-color 0.3s ease;
        }
        .doc-card::before {
            content:""; position:absolute; inset:0;
            background:linear-gradient(135deg, rgba(255,255,255,0.018) 0%, transparent 55%);
            pointer-events:none;
        }
        .doc-card:hover { border-color: rgba(33,197,94,0.3); }
        .doc-step {
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; border-radius: 50%;
            background: rgba(33,197,94,0.1); border: 1px solid rgba(33,197,94,0.3);
            font-family: 'Geist Mono', monospace; font-size: 0.72rem; font-weight: 700;
            color: #21C55E; flex-shrink: 0; margin-right: 14px;
        }
        .doc-card h3 {
            font-family: 'Geist Mono', monospace; font-size: 0.95rem; font-weight: 700;
            color: #f4f4f5; margin: 0 0 12px 0; display: flex; align-items: center;
        }
        .doc-card p {
            font-family: 'Space Grotesk', sans-serif; color: #71717a;
            font-size: 0.88rem; line-height: 1.65; margin: 0;
        }
        .doc-tip {
            background: rgba(33,197,94,0.05); border: 1px solid rgba(33,197,94,0.18);
            border-radius: 10px; padding: 14px 18px; margin-top: 10px;
            font-family: 'Space Grotesk', sans-serif; font-size: 0.84rem; color: #71717a;
            display: flex; gap: 10px; align-items: flex-start;
        }
        .doc-tip i { color: #21C55E; font-size: 0.8rem; margin-top: 2px; flex-shrink: 0; }
        kbd {
            background: #1a1a1e; border: 1px solid #2e2e33; border-radius: 4px;
            padding: 1px 6px; font-family: 'Geist Mono', monospace;
            font-size: 0.78rem; color: #d4d4d8;
        }
    </style>
    """, unsafe_allow_html=True)

    # PAGE HERO
    st.markdown("""
    <div class="page-hero">
        <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(33,197,94,0.07); border:1px solid rgba(33,197,94,0.25); border-radius:99px; padding:8px 20px; margin-bottom:32px; font-family:'Geist Mono',monospace; font-size:0.7rem; color:#21C55E; letter-spacing:1.8px; text-transform:uppercase;">
            <i class="fa-solid fa-book-open"></i> User Guide
        </div>
        <h1>Documentation</h1>
        <p>Step-by-step operational guide for using the telemetry analytics platform.</p>
    </div>
    """, unsafe_allow_html=True)

    # QUICK START
    st.markdown('<div class="section-title"><i class="fa-solid fa-rocket"></i> Quick Start</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="doc-card">
        <h3><span class="doc-step">01</span> Session Initialisation</h3>
        <p>From the Home page, click <strong style="color:#d4d4d8;">INITIALIZE UPLINK</strong> to access the Dashboard.
        Use the left sidebar to configure <kbd>Year</kbd>, <kbd>Grand Prix</kbd> and
        <kbd>Session</kbd> (FP1–FP3, Qualifying, Sprint, Race).</p>
    </div>
    <div class="doc-card">
        <h3><span class="doc-step">02</span> Data Synchronisation</h3>
        <p>Press <strong style="color:#d4d4d8;">LOAD SESSION</strong>. FastF1 will check the local cache first.
        If the session is cached, load time is near-instant. A remote fetch from the FIA LiveTiming API
        is only triggered on the first load for a given session.</p>
        <div class="doc-tip">
            <i class="fa-solid fa-circle-info"></i>
            <span>Cached sessions reload in milliseconds. Internet connection is only needed for the initial fetch.</span>
        </div>
    </div>
    <div class="doc-card">
        <h3><span class="doc-step">03</span> Driver Selection</h3>
        <p>Use the <kbd>Select Drivers</kbd> multiselect in the sidebar to choose up to 2 drivers
        for overlaid chart comparisons. Use the <strong style="color:#d4d4d8;">Favourite Drivers</strong>
        panel to pin frequently used drivers for quick-select.</p>
    </div>
    <div class="doc-card">
        <h3><span class="doc-step">04</span> Tab Navigation</h3>
        <p>Navigate between the four analysis tabs at the top of the dashboard:</p>
        <div style="margin-top:14px; display:flex; flex-wrap:wrap; gap:8px;">
            <span style="background:rgba(33,197,94,0.08); border:1px solid rgba(33,197,94,0.2); border-radius:8px; padding:5px 14px; font-family:'Geist Mono',monospace; font-size:0.72rem; color:#21C55E;">Telemetry Analysis</span>
            <span style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2); border-radius:8px; padding:5px 14px; font-family:'Geist Mono',monospace; font-size:0.72rem; color:#3b82f6;">Race History</span>
            <span style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2); border-radius:8px; padding:5px 14px; font-family:'Geist Mono',monospace; font-size:0.72rem; color:#f59e0b;">Strategy &amp; Tyres</span>
            <span style="background:rgba(168,85,247,0.08); border:1px solid rgba(168,85,247,0.2); border-radius:8px; padding:5px 14px; font-family:'Geist Mono',monospace; font-size:0.72rem; color:#a855f7;">Multi-Session</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ANALYSIS MODULES
    st.markdown('<div class="section-title"><i class="fa-solid fa-microchip"></i> Analysis Modules</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("""
        <div class="doc-card">
            <h3 style="font-family:'Geist Mono',monospace; font-size:0.95rem; font-weight:700; color:#f4f4f5; margin:0 0 12px;">
                <i class="fa-solid fa-wave-square" style="color:#21C55E; margin-right:10px;"></i>Telemetry Analysis
            </h3>
            <p>Compare raw speed, throttle, brake, steering angle, gear and DRS channel traces for any two drivers
            on their respective fastest laps. Delta time trace shows where time is gained or lost corner by corner.</p>
        </div>
        <div class="doc-card">
            <h3 style="font-family:'Geist Mono',monospace; font-size:0.95rem; font-weight:700; color:#f4f4f5; margin:0 0 12px;">
                <i class="fa-solid fa-chart-line" style="color:#f59e0b; margin-right:10px;"></i>Strategy &amp; Tyres
            </h3>
            <p>Stint timeline with compound colour-coding, undercut window detection and lap-time regression
            per tyre compound over long runs. Identifies degradation cliffs and optimal stop windows.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="doc-card">
            <h3 style="font-family:'Geist Mono',monospace; font-size:0.95rem; font-weight:700; color:#f4f4f5; margin:0 0 12px;">
                <i class="fa-solid fa-flag-checkered" style="color:#3b82f6; margin-right:10px;"></i>Race History
            </h3>
            <p>Race pace raw and fuel-corrected lap times plotted per stint. Position history chart shows
            on-track battles and the impact of pit windows on final classification throughout the race.</p>
        </div>
        <div class="doc-card">
            <h3 style="font-family:'Geist Mono',monospace; font-size:0.95rem; font-weight:700; color:#f4f4f5; margin:0 0 12px;">
                <i class="fa-solid fa-code-compare" style="color:#a855f7; margin-right:10px;"></i>Multi-Session
            </h3>
            <p>Cross-session telemetry comparison to isolate setup evolution across the race weekend
            (FP1 → Qualifying → Race). Load a secondary session from the sidebar to enable this module.</p>
        </div>
        """, unsafe_allow_html=True)

    # TIPS
    st.markdown('<div class="section-title"><i class="fa-solid fa-lightbulb"></i> Tips &amp; Shortcuts</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="doc-card">
        <p style="margin-bottom:10px;">A few things to keep in mind while using the platform:</p>
        <div class="doc-tip"><i class="fa-solid fa-bolt"></i>
            <span>The cache is stored in the <kbd>cache/</kbd> directory. Delete it to force a fresh data fetch.</span>
        </div>
        <div class="doc-tip" style="margin-top:8px;"><i class="fa-solid fa-star"></i>
            <span>Pin your most-used drivers via <strong style="color:#d4d4d8;">Manage Favourite Drivers</strong> in the sidebar for one-click access.</span>
        </div>
        <div class="doc-tip" style="margin-top:8px;"><i class="fa-solid fa-download"></i>
            <span>All Plotly charts support in-chart export — hover a chart and click the camera icon to save as PNG.</span>
        </div>
        <div class="doc-tip" style="margin-top:8px;"><i class="fa-solid fa-rotate"></i>
            <span>Changing the session or year in the sidebar and pressing <strong style="color:#d4d4d8;">LOAD SESSION</strong> again replaces the active session.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)
