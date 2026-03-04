import streamlit as st
from utils.components import render_navbar


def render():
    render_navbar("features")
    st.markdown("""
    <style>
        @keyframes stag-in { from { opacity:0; transform:translateY(22px); } to { opacity:1; transform:translateY(0); } }
        .feat-card {
            background: linear-gradient(145deg, #141416 0%, #0e0e10 100%);
            border: 1px solid #232326; border-radius: 16px; padding: 28px 32px;
            transition: all 0.4s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden;
        }
        .feat-card::before {
            content:""; position:absolute; inset:0;
            background:linear-gradient(135deg, rgba(255,255,255,0.022) 0%, transparent 55%);
            pointer-events:none;
        }
        .feat-card:hover { transform:translateY(-10px); border-color:rgba(33,197,94,0.45)!important; box-shadow:0 24px 56px rgba(33,197,94,0.1)!important; }
        .feat-icon { width:44px; height:44px; border-radius:12px; background:rgba(33,197,94,0.08); border:1px solid rgba(33,197,94,0.18); display:flex; align-items:center; justify-content:center; font-size:1.2rem; color:#21C55E; margin-bottom:20px; }
        .feat-tag { display:inline-block; background:rgba(33,197,94,0.08); border:1px solid rgba(33,197,94,0.2); border-radius:99px; padding:3px 12px; font-family:'Geist Mono',monospace; font-size:0.6rem; font-weight:700; color:#21C55E; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:14px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="page-hero">
        <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(33,197,94,0.07); border:1px solid rgba(33,197,94,0.25); border-radius:99px; padding:8px 20px; margin-bottom:32px; font-family:'Geist Mono',monospace; font-size:0.7rem; color:#21C55E; letter-spacing:1.8px; text-transform:uppercase;">
            <i class="fa-solid fa-circle-nodes"></i> Platform Capabilities
        </div>
        <h1>Feature Matrix</h1>
        <p>High-resolution technical analysis across every aspect of on-track performance, from raw telemetry to pit-stop strategy.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title"><i class="fa-solid fa-layer-group"></i> Analysis Modules</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-icon"><i class="fa-solid fa-microchip"></i></div>
            <div class="feat-tag">Telemetry</div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:1.05rem; margin-bottom:10px; font-weight:700;">Lap Analysis</h3>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.88rem; line-height:1.6;">Full speed, throttle, brake, steering and gear overlay for benchmark laps. DRS and ERS channels included.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-icon"><i class="fa-solid fa-flag-checkered"></i></div>
            <div class="feat-tag">Race</div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:1.05rem; margin-bottom:10px; font-weight:700;">Race Pace Model</h3>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.88rem; line-height:1.6;">Raw and fuel-corrected race pace per stint. Linear regression and tyre degradation cliff detection.</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-icon"><i class="fa-solid fa-screwdriver-wrench"></i></div>
            <div class="feat-tag">Strategy</div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:1.05rem; margin-bottom:10px; font-weight:700;">Pit Strategy</h3>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.88rem; line-height:1.6;">Stint visualisation, undercut windows, compound comparison and long-run pace analysis per tyre compound.</p>
        </div>""", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3, gap="medium")
    with c4:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-icon"><i class="fa-solid fa-code-compare"></i></div>
            <div class="feat-tag">Multi-Session</div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:1.05rem; margin-bottom:10px; font-weight:700;">Cross-Session Delta</h3>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.88rem; line-height:1.6;">Telemetric comparison across different sessions. Isolate setup evolution from FP1 → Qualifying → Race.</p>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-icon"><i class="fa-solid fa-chart-line"></i></div>
            <div class="feat-tag">Sectors</div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:1.05rem; margin-bottom:10px; font-weight:700;">Sector Speed Maps</h3>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.88rem; line-height:1.6;">Speed heatmap across the full track layout. Mini-sectors and time-delta heatmap against a reference lap.</p>
        </div>""", unsafe_allow_html=True)
    with c6:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-icon"><i class="fa-solid fa-brain"></i></div>
            <div class="feat-tag">Advanced</div>
            <h3 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:1.05rem; margin-bottom:10px; font-weight:700;">Advanced Analytics</h3>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.88rem; line-height:1.6;">Driver performance scoring, lap consistency index, cornering efficiency and brake balance inference from raw data.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title"><i class="fa-solid fa-puzzle-piece"></i> Platform Features</div>', unsafe_allow_html=True)

    f1, f2 = st.columns(2, gap="medium")
    with f1:
        st.markdown("""
        <div class="feat-card" style="display:flex; gap:20px; align-items:flex-start;">
            <div class="feat-icon" style="flex-shrink:0;"><i class="fa-solid fa-database"></i></div>
            <div>
                <h4 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:0.95rem; margin-bottom:8px; font-weight:700;">Intelligent Cache</h4>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.85rem; line-height:1.55;">FastF1 local cache with disk persistence. Subsequent loads are instant — zero latency after the first fetch.</p>
            </div>
        </div>""", unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feat-card" style="display:flex; gap:20px; align-items:flex-start;">
            <div class="feat-icon" style="flex-shrink:0;"><i class="fa-solid fa-star"></i></div>
            <div>
                <h4 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:0.95rem; margin-bottom:8px; font-weight:700;">Favourite Drivers</h4>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.85rem; line-height:1.55;">Persistent favourites system for quick-select of frequently analysed drivers. Zero configuration required.</p>
            </div>
        </div>""", unsafe_allow_html=True)

    f3, f4 = st.columns(2, gap="medium")
    with f3:
        st.markdown("""
        <div class="feat-card" style="display:flex; gap:20px; align-items:flex-start;">
            <div class="feat-icon" style="flex-shrink:0; background:rgba(59,130,246,0.08); border-color:rgba(59,130,246,0.18);"><i class="fa-solid fa-palette" style="color:#3b82f6;"></i></div>
            <div>
                <h4 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:0.95rem; margin-bottom:8px; font-weight:700;">Driver Color System</h4>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.85rem; line-height:1.55;">Official FastF1 colours auto-assigned per team and driver. Visual consistency across all charts and plots.</p>
            </div>
        </div>""", unsafe_allow_html=True)
    with f4:
        st.markdown("""
        <div class="feat-card" style="display:flex; gap:20px; align-items:flex-start;">
            <div class="feat-icon" style="flex-shrink:0; background:rgba(245,158,11,0.08); border-color:rgba(245,158,11,0.18);"><i class="fa-solid fa-share-nodes" style="color:#f59e0b;"></i></div>
            <div>
                <h4 style="font-family:'Geist Mono',monospace; color:#f4f4f5; font-size:0.95rem; margin-bottom:8px; font-weight:700;">Export Ready</h4>
                <p style="font-family:'Space Grotesk',sans-serif; color:#71717a; font-size:0.85rem; line-height:1.55;">Export Plotly charts as high-resolution PNG or raw CSV directly from the dashboard in one click.</p>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

