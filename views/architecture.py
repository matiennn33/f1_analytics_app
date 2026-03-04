import streamlit as st
from utils.components import render_navbar


def render():
    render_navbar("architecture")
    st.markdown("""
    <style>
        .arch-layer {
            border: 1px solid #232326; border-radius: 14px; padding: 24px 28px;
            background: linear-gradient(145deg, #141416 0%, #0e0e10 100%);
            position: relative; overflow: hidden; margin-bottom: 0;
        }
        .arch-layer::before {
            content:""; position:absolute; top:0; left:0; right:0; height:2px;
        }
        .arch-layer.l-ui::before    { background:linear-gradient(90deg, transparent, #3b82f6, transparent); }
        .arch-layer.l-logic::before { background:linear-gradient(90deg, transparent, #21C55E, transparent); }
        .arch-layer.l-data::before  { background:linear-gradient(90deg, transparent, #f59e0b, transparent); }
        .arch-layer.l-cache::before { background:linear-gradient(90deg, transparent, #a855f7, transparent); }
        .arch-label { font-family:'Geist Mono',monospace; font-size:0.58rem; font-weight:700; text-transform:uppercase; letter-spacing:2px; margin-bottom:14px; display:flex; align-items:center; gap:8px; }
        .tech-pill { display:inline-flex; align-items:center; gap:7px; background:rgba(255,255,255,0.04); border:1px solid #2e2e33; border-radius:8px; padding:6px 14px; font-family:'Space Grotesk',sans-serif; font-size:0.82rem; color:#d4d4d8; margin:4px; transition:all 0.22s; cursor:default; }
        .tech-pill:hover { border-color:#3a3a3f; background:rgba(255,255,255,0.07); color:#f4f4f5; }
        .tech-pill i { font-size:0.78rem; }
        .flow-arrow { display:flex; justify-content:center; align-items:center; padding:12px 0; color:#3a3a3f; font-size:1.1rem; }
        .data-flow-step {
            display:flex; align-items:center; gap:16px; padding:16px 20px;
            background:rgba(255,255,255,0.02); border:1px solid #1e1e22; border-radius:10px; margin-bottom:8px;
            transition: border-color 0.22s;
        }
        .data-flow-step:hover { border-color:#3a3a3f; }
        .step-num { width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:'Geist Mono',monospace; font-size:0.72rem; font-weight:700; flex-shrink:0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="page-hero">
        <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(59,130,246,0.07); border:1px solid rgba(59,130,246,0.25); border-radius:99px; padding:8px 20px; margin-bottom:32px; font-family:'Geist Mono',monospace; font-size:0.7rem; color:#3b82f6; letter-spacing:1.8px; text-transform:uppercase;">
            <i class="fa-solid fa-sitemap"></i> Infrastructure
        </div>
        <h1>System Architecture</h1>
        <p>Technology stack, data flow and modular architecture of the telemetry analytics platform.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title"><i class="fa-solid fa-layer-group"></i> Technology Stack</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="arch-layer l-ui">
        <div class="arch-label" style="color:#3b82f6;"><i class="fa-solid fa-display" style="color:#3b82f6;"></i> UI Layer — Presentation</div>
        <div>
            <span class="tech-pill"><i class="fa-brands fa-python" style="color:#f59e0b;"></i> Streamlit 1.55</span>
            <span class="tech-pill"><i class="fa-solid fa-palette" style="color:#3b82f6;"></i> Custom CSS Design System</span>
            <span class="tech-pill"><i class="fa-solid fa-icons" style="color:#3b82f6;"></i> Font Awesome 6</span>
            <span class="tech-pill"><i class="fa-solid fa-font" style="color:#3b82f6;"></i> Geist Mono + Space Grotesk</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="flow-arrow"><i class="fa-solid fa-arrow-down"></i></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="arch-layer l-logic">
        <div class="arch-label" style="color:#21C55E;"><i class="fa-solid fa-gears" style="color:#21C55E;"></i> Logic Layer — Analysis Modules</div>
        <div>
            <span class="tech-pill"><i class="fa-solid fa-microchip" style="color:#21C55E;"></i> telemetry.py</span>
            <span class="tech-pill"><i class="fa-solid fa-flag-checkered" style="color:#21C55E;"></i> race.py</span>
            <span class="tech-pill"><i class="fa-solid fa-screwdriver-wrench" style="color:#21C55E;"></i> strategy.py</span>
            <span class="tech-pill"><i class="fa-solid fa-code-compare" style="color:#21C55E;"></i> multi_session.py</span>
            <span class="tech-pill"><i class="fa-solid fa-chart-line" style="color:#21C55E;"></i> sectors_speed.py</span>
            <span class="tech-pill"><i class="fa-solid fa-brain" style="color:#21C55E;"></i> advanced_analytics.py</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="flow-arrow"><i class="fa-solid fa-arrow-down"></i></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="arch-layer l-data">
        <div class="arch-label" style="color:#f59e0b;"><i class="fa-solid fa-database" style="color:#f59e0b;"></i> Data Layer — Processing</div>
        <div>
            <span class="tech-pill"><i class="fa-brands fa-python" style="color:#f59e0b;"></i> FastF1</span>
            <span class="tech-pill"><i class="fa-solid fa-table" style="color:#f59e0b;"></i> Pandas</span>
            <span class="tech-pill"><i class="fa-solid fa-calculator" style="color:#f59e0b;"></i> NumPy</span>
            <span class="tech-pill"><i class="fa-solid fa-chart-area" style="color:#f59e0b;"></i> Plotly Graph Objects</span>
            <span class="tech-pill"><i class="fa-solid fa-image" style="color:#f59e0b;"></i> Matplotlib</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="flow-arrow"><i class="fa-solid fa-arrow-down"></i></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="arch-layer l-cache">
        <div class="arch-label" style="color:#a855f7;"><i class="fa-solid fa-hard-drive" style="color:#a855f7;"></i> Persistence Layer — Cache</div>
        <div>
            <span class="tech-pill"><i class="fa-solid fa-bolt" style="color:#a855f7;"></i> FastF1 Local Cache</span>
            <span class="tech-pill"><i class="fa-solid fa-file-zipper" style="color:#a855f7;"></i> ff1pkl Serialization</span>
            <span class="tech-pill"><i class="fa-solid fa-network-wired" style="color:#a855f7;"></i> FIA LiveTiming API</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title"><i class="fa-solid fa-route"></i> Data Flow</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="max-width:800px;">
        <div class="data-flow-step">
            <div class="step-num" style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.3); color:#3b82f6;">01</div>
            <div>
                <div style="font-family:'Geist Mono',monospace; font-size:0.82rem; font-weight:700; color:#f4f4f5; margin-bottom:4px;">User Request</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:0.84rem; color:#71717a;">Select Year, GP and Session from the sidebar. Pressing "Load Session" triggers the data pipeline.</div>
            </div>
        </div>
        <div class="data-flow-step">
            <div class="step-num" style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3); color:#f59e0b;">02</div>
            <div>
                <div style="font-family:'Geist Mono',monospace; font-size:0.82rem; font-weight:700; color:#f4f4f5; margin-bottom:4px;">Cache Check</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:0.84rem; color:#71717a;">FastF1 checks the local cache in <code style="font-family:'Geist Mono',monospace; background:#1a1a1e; padding:1px 5px; border-radius:4px;">cache/</code>. If found, remote fetch is skipped — latency reduced to tens of ms.</div>
            </div>
        </div>
        <div class="data-flow-step">
            <div class="step-num" style="background:rgba(168,85,247,0.1); border:1px solid rgba(168,85,247,0.3); color:#a855f7;">03</div>
            <div>
                <div style="font-family:'Geist Mono',monospace; font-size:0.82rem; font-weight:700; color:#f4f4f5; margin-bottom:4px;">API Fetch + Decode</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:0.84rem; color:#71717a;">FIA LiveTiming server query. SignalR protocol decode, parsing of timing, car data and position data into DataFrames.</div>
            </div>
        </div>
        <div class="data-flow-step">
            <div class="step-num" style="background:rgba(33,197,94,0.1); border:1px solid rgba(33,197,94,0.3); color:#21C55E;">04</div>
            <div>
                <div style="font-family:'Geist Mono',monospace; font-size:0.82rem; font-weight:700; color:#f4f4f5; margin-bottom:4px;">Spatial Alignment</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:0.84rem; color:#71717a;">Distance-based interpolation of multi-driver telemetry channels. Homogenisation at fixed step for direct comparison.</div>
            </div>
        </div>
        <div class="data-flow-step">
            <div class="step-num" style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); color:#ef4444;">05</div>
            <div>
                <div style="font-family:'Geist Mono',monospace; font-size:0.82rem; font-weight:700; color:#f4f4f5; margin-bottom:4px;">Module Rendering</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:0.84rem; color:#71717a;">Normalised data is routed to isolated modules. Each module generates independent Plotly figures exposed in tabs.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

