import json
import streamlit as st
import streamlit.components.v1 as components


def inject_global_css():
    _FONT_LINKS = [
        "https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css",
    ]
    _CSS = r"""
/* DESIGN TOKENS */
:root {
    --bg-base:      #010101;
    --bg-card:      #0a0a0c;
    --bg-raised:    #111113;
    --bg-glass:     #010101;
    --bg-input:     #030305;
    --border:       #232326;
    --border-mid:   #3a3a3f;
    --border-hi:    #56565e;
    --text-w:       #f4f4f5;
    --text-s:       #d4d4d8;
    --text-m:       #71717a;
    --text-d:       #4a4a52;
    --accent:       #21C55E;
    --accent-dim:   rgba(33,197,94,0.13);
    --accent-glow:  rgba(33,197,94,0.28);
    --accent-deep:  rgba(33,197,94,0.05);
    --red:          #ef4444;
    --orange:       #f97316;
    --amber:        #f59e0b;
    --blue:         #3b82f6;
    --purple:       #a855f7;

    /* ── SPACING SYSTEM (8-pt grid) — Cognitive Load: consistent rhythm ── */
    --sp-1:  4px;
    --sp-2:  8px;
    --sp-3:  12px;
    --sp-4:  16px;
    --sp-5:  20px;
    --sp-6:  24px;
    --sp-7:  28px;
    --sp-8:  32px;
    --sp-10: 40px;
    --sp-12: 48px;
    --sp-16: 64px;
    /* Section rhythm: content blocks breathe */
    --section-gap:   48px;
    --block-gap:     28px;
    --card-pad:      24px;
    --card-pad-sm:   16px;

    /* ── TYPOGRAPHY SCALE — clear hierarchy (H1→caption, 5 levels) ── */
    --text-xs:   0.6rem;
    --text-sm:   0.72rem;
    --text-base: 0.88rem;
    --text-md:   1rem;
    --text-lg:   1.2rem;
    --text-xl:   1.6rem;
    --text-2xl:  2.2rem;
    --text-3xl:  3rem;
    --leading-tight: 1.2;
    --leading-base:  1.55;
    --leading-loose: 1.75;

    /* ── ELEVATION (5 levels — depth = hierarchy) ── */
    --elev-0: none;
    --elev-1: 0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.7);
    --elev-2: 0 4px 16px rgba(0,0,0,0.6), 0 2px 6px rgba(0,0,0,0.5);
    --elev-3: 0 8px 32px rgba(0,0,0,0.7), 0 4px 12px rgba(0,0,0,0.6);
    --elev-4: 0 16px 56px rgba(0,0,0,0.85), 0 8px 24px rgba(0,0,0,0.7);
    --elev-float: 0 24px 80px rgba(0,0,0,0.95), 0 12px 32px rgba(0,0,0,0.8);

    --radius-xs:    4px;
    --radius-sm:    6px;
    --radius-md:    10px;
    --radius-lg:    14px;
    --radius-xl:    18px;
    --radius-2xl:   24px;

    /* ── MOTION (purposeful, not decorative) ── */
    --ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);
    --ease-out:     cubic-bezier(0.25, 0.46, 0.45, 0.94);
    --ease-in-out:  cubic-bezier(0.4, 0, 0.2, 1);
    --transition:   0.22s cubic-bezier(0.4,0,0.2,1);
    --transition-slow: 0.45s cubic-bezier(0.4,0,0.2,1);
    --transition-spring: 0.38s cubic-bezier(0.34,1.56,0.64,1);

    --font-mono:    'Geist Mono', monospace;
    --font-sans:    'Space Grotesk', sans-serif;
    --shadow-card:  0 4px 24px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.4);
    --shadow-lift:  0 16px 48px rgba(0,0,0,0.7), 0 4px 12px rgba(0,0,0,0.5);
    --shadow-glow:  0 0 0 1px var(--accent-glow), 0 8px 32px rgba(33,197,94,0.15);
}
/* ── Accessibility: reduced motion ── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* KEYFRAMES */
@keyframes reveal-up {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes reveal-fade {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes pulse-glow {
    0%,100% { box-shadow: 0 0 0 0 rgba(33,197,94,0.5); }
    50%     { box-shadow: 0 0 0 18px rgba(33,197,94,0); }
}
@keyframes breathe {
    0%,100% { opacity: 0.6; transform: scale(1); }
    50%     { opacity: 1;   transform: scale(1.04); }
}
@keyframes blink-dot {
    0%,100% { opacity: 1; }
    50%     { opacity: 0.25; }
}
@keyframes counter-slide {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes accent-top-line {
    from { opacity: 0.4; }
    to   { opacity: 1; }
}
@keyframes tab-content-enter {
    from { opacity: 0; transform: translateY(10px) scale(0.998); }
    to   { opacity: 1; transform: translateY(0)   scale(1); }
}
@keyframes tab-active-glow {
    0%,100% { box-shadow: 0 2px 12px rgba(0,0,0,0.7), 0 0 14px rgba(33,197,94,0.06), inset 0 1px 0 rgba(33,197,94,0.10); }
    50%     { box-shadow: 0 2px 12px rgba(0,0,0,0.7), 0 0 28px rgba(33,197,94,0.16), inset 0 1px 0 rgba(33,197,94,0.20); }
}
@keyframes stagger-card {
    from { opacity: 0; transform: translateY(18px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0)    scale(1);    }
}
@keyframes banner-shimmer {
    0%   { transform: translateX(-120%) skewX(-18deg); }
    100% { transform: translateX(220%)  skewX(-18deg); }
}
@keyframes sep-line-grow {
    from { transform: scaleX(0); opacity: 0; }
    to   { transform: scaleX(1); opacity: 1; }
}
@keyframes icon-bounce {
    0%,100% { transform: translateY(0); }
    40%     { transform: translateY(-4px); }
    70%     { transform: translateY(-1px); }
}
@property --liq-angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}
@keyframes liq-rotate {
    to { --liq-angle: 360deg; }
}
@keyframes card-pop {
    0%   { opacity: 0; transform: scale(0.90) translateY(16px); }
    60%  { opacity: 1; transform: scale(1.018) translateY(-3px); }
    100% { transform: scale(1) translateY(0); }
}
@keyframes slide-from-left {
    from { opacity: 0; transform: translateX(-24px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slide-from-right {
    from { opacity: 0; transform: translateX(24px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes fill-bar {
    from { transform: scaleX(0); }
    to   { transform: scaleX(1); }
}
@keyframes number-count {
    from { opacity: 0; transform: translateY(10px) scale(0.84); }
    to   { opacity: 1; transform: translateY(0)    scale(1); }
}
@keyframes ripple-out {
    to   { transform: scale(3.8); opacity: 0; }
}
@keyframes skeleton-wave {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
}
@keyframes glow-trace {
    0%,100% { box-shadow: 0 0 0 0 var(--accent-glow); }
    50%      { box-shadow: 0 0 0 6px rgba(33,197,94,0); }
}
@keyframes border-run {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* SCROLLBARS */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 99px; transition: background var(--transition); }
::-webkit-scrollbar-thumb:hover { background: var(--border-hi); }

/* BASE APP */
.stApp {
    background-color: #010101 !important;
    font-family: var(--font-sans) !important;
    font-weight: 400 !important;
    background-image: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(33,197,94,0.055) 0%, transparent 60%);
}
footer { visibility: hidden; }
.block-container { padding-top: 3rem !important; padding-bottom: 4rem !important; max-width: 98% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
.main .block-container { animation: reveal-fade 0.6s ease both; }

/* SHARED PAGE HERO */
.page-hero { text-align: center; padding: 60px 20px 50px; }
.page-hero h1 { font-family: var(--font-mono); font-size: 3.2rem; font-weight: 900; text-transform: uppercase; color: var(--text-w); margin-bottom: 16px; letter-spacing: 2px; }
.page-hero p { font-family: var(--font-sans); font-size: 1.1rem; color: var(--text-m); max-width: 600px; margin: 0 auto; line-height: 1.6; }

/* SHARED SECTION TITLE */
.section-title { font-family: var(--font-mono); font-size: 0.62rem; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 2.5px; margin: var(--section-gap) 0 var(--sp-6); display: flex; align-items: center; gap: 12px; }
.section-title::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, var(--accent-glow), transparent); }

/* TYPOGRAPHY — 5-level scale for clear visual hierarchy (Recognition vs Recall) */
h1, .stMarkdown h1 { font-family: var(--font-mono) !important; font-size: var(--text-2xl) !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 2px !important; color: var(--text-w) !important; line-height: var(--leading-tight) !important; margin-bottom: var(--sp-4) !important; }
h2, .stMarkdown h2 { font-family: var(--font-mono) !important; font-size: var(--text-xl) !important; font-weight: 700 !important; color: var(--text-w) !important; line-height: var(--leading-tight) !important; margin-top: var(--sp-8) !important; margin-bottom: var(--sp-4) !important; letter-spacing: 1px !important; }
h3, .stMarkdown h3 { font-family: var(--font-mono) !important; font-size: var(--text-md) !important; font-weight: 700 !important; color: var(--text-s) !important; line-height: var(--leading-base) !important; margin-top: var(--sp-6) !important; margin-bottom: var(--sp-3) !important; }
h4, h5, h6, .stMarkdown h4 { font-family: var(--font-mono) !important; font-size: var(--text-base) !important; font-weight: 600 !important; color: var(--text-s) !important; }
/* Widget labels: readable size + sufficient contrast (Cognitive Load) */
.stWidgetLabel p, label p, [data-testid="stWidgetLabel"] p {
    font-family: var(--font-mono) !important; font-weight: 600 !important; color: var(--text-m) !important;
    font-size: 0.74rem !important; text-transform: uppercase !important; letter-spacing: 1px !important; margin-bottom: var(--sp-2) !important;
}
p, .stMarkdown p { font-family: var(--font-sans) !important; font-size: var(--text-base) !important; color: var(--text-s) !important; line-height: var(--leading-base) !important; }

/* BUTTON SECONDARY */
/* BUTTON SECONDARY — Fitts's Law: targets must be large enough to hit */
button[kind="secondary"] {
    width: 100% !important; border-radius: var(--radius-md) !important;
    background: #060608 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 2px 8px rgba(0,0,0,0.6) !important;
    padding: 10px 18px !important; min-height: 40px !important; transition: all var(--transition) !important; cursor: pointer !important;
}
button[kind="secondary"] p {
    font-family: var(--font-sans) !important; font-weight: 600 !important; color: var(--text-s) !important;
    font-size: 0.88rem !important; text-transform: uppercase !important; letter-spacing: 0.8px !important;
    margin: 0 !important; transition: color var(--transition) !important;
}
button[kind="secondary"]:hover {
    background: #0a0a0d !important;
    border-color: rgba(255,255,255,0.14) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 6px 20px rgba(0,0,0,0.7) !important;
    transform: translateY(-1px) !important;
}
button[kind="secondary"]:hover p { color: var(--text-w) !important; }
button[kind="secondary"]:active { transform: translateY(1px) scale(0.99) !important; }

/* BUTTON PRIMARY CTA */
@keyframes cta-glow {
    0%,100% { box-shadow: 0 0 28px rgba(33,197,94,0.18), 0 16px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(33,197,94,0.12), inset 0 1px 1px rgba(255,255,255,0.07); }
    50%     { box-shadow: 0 0 55px rgba(33,197,94,0.42), 0 16px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(33,197,94,0.35), inset 0 1px 1px rgba(255,255,255,0.1); }
}
@keyframes cta-shimmer {
    0%   { transform: translateX(-130%) skewX(-20deg); }
    100% { transform: translateX(250%) skewX(-20deg); }
}
div.element-container:has(button[kind="primary"]),
div[data-testid="stButton"]:has(button[kind="primary"]) {
    display: flex !important; justify-content: center !important; align-items: center !important;
    width: 100% !important; background: transparent !important; border: none !important;
    box-shadow: none !important; margin-top: 14px !important; margin-bottom: 52px !important;
}
button[kind="primary"] {
    all: unset !important; cursor: pointer !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    background: linear-gradient(135deg, rgba(6,32,16,0.98) 0%, rgba(15,15,18,1) 55%, rgba(4,4,6,1) 100%) !important;
    border: 1px solid rgba(33,197,94,0.45) !important; border-radius: var(--radius-xl) !important;
    height: 72px !important; width: 410px !important; max-width: 90vw !important;
    box-shadow: 0 0 28px rgba(33,197,94,0.18), 0 16px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(33,197,94,0.12), inset 0 1px 1px rgba(255,255,255,0.07) !important;
    transition: all var(--transition-slow) !important; margin: 0 auto !important;
    position: relative !important; overflow: hidden !important;
    animation: cta-glow 2.8s ease-in-out infinite !important;
}
button[kind="primary"]::after {
    content: "" !important; position: absolute !important; top: 0 !important; left: 0 !important;
    width: 40% !important; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(33,197,94,0.08), transparent) !important;
    transform: translateX(-130%) skewX(-20deg) !important;
    animation: cta-shimmer 4s ease-in-out infinite !important;
    pointer-events: none !important;
}
button[kind="primary"] p {
    color: #21C55E !important; font-family: var(--font-sans) !important; font-weight: 700 !important;
    font-size: 1.12rem !important; letter-spacing: 3px !important; text-transform: uppercase !important;
    margin: 0 !important; display: flex !important; align-items: center !important;
    text-shadow: 0 0 18px rgba(33,197,94,0.75) !important;
}
button[kind="primary"] p::before {
    content: "\f0e7"; font-family: "Font Awesome 6 Free"; font-weight: 900;
    margin-right: 14px; color: #21C55E !important; font-size: 1.1rem !important;
    text-shadow: 0 0 14px rgba(33,197,94,0.9) !important;
}
button[kind="primary"]:hover {
    transform: translateY(-6px) scale(1.01) !important;
    background: linear-gradient(135deg, rgba(10,50,25,0.98) 0%, rgba(20,20,24,1) 52%, rgba(7,7,9,1) 100%) !important;
    box-shadow: 0 0 70px rgba(33,197,94,0.5), 0 28px 52px rgba(0,0,0,0.85), 0 0 0 1px rgba(33,197,94,0.55), inset 0 1px 1px rgba(255,255,255,0.12) !important;
    border-color: rgba(33,197,94,0.72) !important;
    animation: none !important;
}
button[kind="primary"]:active { transform: translateY(2px) scale(0.99) !important; animation: none !important; }

/* TEXT INPUT */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input, [data-testid="stTimeInput"] input {
    background-color: #060608 !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important; color: var(--text-s) !important;
    font-family: var(--font-sans) !important; font-size: 0.88rem !important; padding: 9px 13px !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), inset 0 2px 8px rgba(0,0,0,0.7) !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(33,197,94,0.5) !important;
    box-shadow: 0 0 0 3px rgba(33,197,94,0.08), inset 0 1px 0 rgba(255,255,255,0.04), inset 0 2px 8px rgba(0,0,0,0.7), 0 0 12px rgba(33,197,94,0.05) !important; outline: none !important;
}
[data-testid="stTextInput"] input::placeholder, [data-testid="stNumberInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: var(--text-d) !important; }
[data-testid="stNumberInput"] button {
    background: var(--bg-raised) !important; border: 1px solid var(--border) !important;
    color: var(--text-m) !important; border-radius: var(--radius-sm) !important; transition: all var(--transition) !important;
}
[data-testid="stNumberInput"] button:hover { border-color: var(--accent) !important; color: var(--accent) !important; background: rgba(33,197,94,0.07) !important; }
[data-baseweb="input"] {
    background-color: #060608 !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important; transition: border-color var(--transition), box-shadow var(--transition) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
[data-baseweb="input"]:focus-within { border-color: rgba(33,197,94,0.5) !important; box-shadow: 0 0 0 3px rgba(33,197,94,0.08), inset 0 1px 0 rgba(255,255,255,0.04), 0 0 12px rgba(33,197,94,0.05) !important; }
[data-baseweb="base-input"] { background: transparent !important; color: var(--text-s) !important; font-family: var(--font-sans) !important; font-size: 0.88rem !important; }
[data-baseweb="textarea"] {
    background-color: #060608 !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important; color: var(--text-s) !important;
    font-family: var(--font-sans) !important; font-size: 0.88rem !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
[data-baseweb="textarea"]:focus-within { border-color: rgba(33,197,94,0.5) !important; box-shadow: 0 0 0 3px rgba(33,197,94,0.08), inset 0 1px 0 rgba(255,255,255,0.04), 0 0 12px rgba(33,197,94,0.05) !important; }

/* SELECT AND MULTISELECT */
* { outline: none !important; }
*:focus, *:focus-visible { outline: none !important; box-shadow: none !important; }
div[data-baseweb="select"],
div[data-baseweb="select"] *,
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div *,
[data-testid="stSelectbox"],
[data-testid="stMultiSelect"] {
    outline: none !important;
    -webkit-tap-highlight-color: transparent !important;
}
div[data-baseweb="select"] > div {
    background-color: #030305 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), inset 0 2px 6px rgba(0,0,0,0.7) !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important; min-height: 38px !important;
    outline: none !important;
}
div[data-baseweb="select"] > div:hover, div[data-baseweb="select"] > div:focus-within {
    border-color: rgba(33,197,94,0.4) !important;
    box-shadow: 0 0 0 2px rgba(33,197,94,0.07), inset 0 1px 0 rgba(255,255,255,0.03), inset 0 2px 6px rgba(0,0,0,0.7) !important;
    outline: none !important;
}
div[data-baseweb="select"] div, div[data-baseweb="popover"] li {
    font-family: var(--font-sans) !important; font-weight: 400 !important; color: var(--text-w) !important; font-size: 0.88rem !important;
}
div[data-baseweb="popover"] ul {
    background-color: #060608 !important;
    border: 1px solid rgba(255,255,255,0.09) !important; border-radius: var(--radius-lg) !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.95), 0 0 0 1px rgba(255,255,255,0.06), inset 0 1px 0 rgba(255,255,255,0.05) !important; padding: 5px !important;
}
div[data-baseweb="popover"] li { border-radius: var(--radius-sm) !important; padding: 9px 13px !important; transition: background var(--transition), color var(--transition) !important; }
div[data-baseweb="popover"] li:hover { background-color: rgba(33,197,94,0.09) !important; color: var(--accent) !important; }
div[data-baseweb="popover"] li[aria-selected="true"] { background-color: var(--accent-dim) !important; color: var(--accent) !important; }
div[data-baseweb="popover"] li[aria-selected="true"] div { color: var(--accent) !important; }
div[data-baseweb="select"] span[data-baseweb="tag"] {
    background-color: rgba(33,197,94,0.09) !important; color: var(--accent) !important;
    font-family: var(--font-mono) !important; font-weight: 600 !important;
    border-radius: var(--radius-xs) !important; border: 1px solid rgba(33,197,94,0.28) !important;
    padding: 3px 10px !important; font-size: 0.72rem !important; animation: counter-slide 0.2s ease both;
}
div[data-baseweb="select"] span[data-baseweb="tag"] span[role="presentation"] { color: var(--accent) !important; opacity: 0.55 !important; }
div[data-baseweb="select"] span[data-baseweb="tag"] span[role="presentation"]:hover { opacity: 1 !important; }

/* SLIDER */
[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child { background: var(--border-mid) !important; height: 3px !important; border-radius: 99px !important; }
[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child > div:last-child { background: linear-gradient(90deg, rgba(33,197,94,0.7) 0%, var(--accent) 100%) !important; }
[data-testid="stSlider"] [role="slider"] {
    background: var(--bg-base) !important; border: 2px solid var(--accent) !important;
    width: 16px !important; height: 16px !important; border-radius: 50% !important;
    box-shadow: 0 0 0 3px rgba(33,197,94,0.18), 0 2px 6px rgba(0,0,0,0.6) !important;
    transition: box-shadow var(--transition), transform var(--transition) !important;
}
[data-testid="stSlider"] [role="slider"]:hover, [data-testid="stSlider"] [role="slider"]:focus {
    box-shadow: 0 0 0 7px rgba(33,197,94,0.18), 0 2px 10px rgba(0,0,0,0.7) !important; transform: scale(1.2) !important;
}
[data-testid="stSlider"] [data-testid="stThumbValue"], [data-testid="stSlider"] [data-baseweb="tooltip"] {
    background: var(--bg-raised) !important; border: 1px solid var(--border-mid) !important;
    border-radius: var(--radius-sm) !important; color: var(--accent) !important;
    font-family: var(--font-mono) !important; font-size: 0.7rem !important; font-weight: 700 !important; padding: 2px 8px !important;
}
[data-testid="stSlider"] [data-testid="stTickBarMin"], [data-testid="stSlider"] [data-testid="stTickBarMax"] { color: var(--text-d) !important; font-family: var(--font-mono) !important; font-size: 0.66rem !important; }

/* CHECKBOX */
[data-baseweb="checkbox"] label { gap: 10px !important; align-items: center !important; cursor: pointer !important; }
[data-baseweb="checkbox"] label span:first-child {
    width: 16px !important; height: 16px !important; border: 2px solid var(--border-mid) !important;
    border-radius: 4px !important; background: var(--bg-input) !important; transition: all var(--transition) !important; flex-shrink: 0 !important;
}
[data-baseweb="checkbox"] label:hover span:first-child { border-color: var(--accent) !important; background: rgba(33,197,94,0.06) !important; }
[data-baseweb="checkbox"] [aria-checked="true"] ~ label span:first-child,
[data-baseweb="checkbox"] input:checked ~ label span:first-child,
[data-baseweb="checkbox"] label[aria-checked="true"] span:first-child { background: var(--accent) !important; border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(33,197,94,0.15) !important; }
[data-baseweb="checkbox"] label span:last-child { font-family: var(--font-sans) !important; font-size: 0.88rem !important; color: var(--text-s) !important; }

/* RADIO */
[data-baseweb="radio"] label { gap: 10px !important; align-items: center !important; margin-bottom: 4px !important; cursor: pointer !important; }
[data-baseweb="radio"] label span:first-child {
    width: 16px !important; height: 16px !important; border: 2px solid var(--border-mid) !important;
    border-radius: 50% !important; background: var(--bg-input) !important; transition: all var(--transition) !important; flex-shrink: 0 !important;
}
[data-baseweb="radio"] label:hover span:first-child { border-color: var(--accent) !important; background: rgba(33,197,94,0.06) !important; }
[data-baseweb="radio"] label[aria-checked="true"] span:first-child,
[data-baseweb="radio"] input:checked ~ label span:first-child {
    border-color: var(--accent) !important; background: radial-gradient(circle at center, var(--accent) 42%, transparent 42%) !important;
    box-shadow: 0 0 0 3px rgba(33,197,94,0.16) !important;
}
[data-baseweb="radio"] label span:last-child { font-family: var(--font-sans) !important; font-size: 0.88rem !important; color: var(--text-s) !important; }

/* TOGGLE */
[data-testid="stToggle"] label div[role="checkbox"] { background-color: var(--border-mid) !important; transition: background var(--transition) !important; }
[data-testid="stToggle"] label div[role="checkbox"][aria-checked="true"] { background-color: var(--accent) !important; box-shadow: 0 0 10px rgba(33,197,94,0.3) !important; }
[data-testid="stToggle"] p { font-family: var(--font-sans) !important; font-size: 0.88rem !important; color: var(--text-s) !important; }

/* SPINNER */
[data-testid="stSpinner"] > div { border-top-color: var(--accent) !important; border-right-color: var(--accent) !important; }
[data-testid="stSpinner"] p, [data-testid="stSpinner"] span { font-family: var(--font-sans) !important; color: var(--text-m) !important; font-size: 0.84rem !important; }

/* PROGRESS BAR */
[data-testid="stProgressBar"] > div { background: var(--border) !important; border-radius: 99px !important; height: 3px !important; overflow: hidden !important; }
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--accent) 0%, rgba(33,197,94,0.65) 100%) !important;
    border-radius: 99px !important; transition: width 0.5s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 0 6px var(--accent-glow) !important;
}

/* METRIC */
[data-testid="stMetric"] {
    background: #060608 !important;
    border: 1px solid rgba(255,255,255,0.07) !important; border-radius: var(--radius-lg) !important;
    padding: 18px 22px !important; position: relative !important; overflow: hidden !important;
    transition: border-color var(--transition), box-shadow var(--transition), transform var(--transition) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 20px rgba(0,0,0,0.8) !important;
}
[data-testid="stMetric"]::before {
    content: "" !important; position: absolute !important; inset: -1px !important;
    border-radius: inherit !important; padding: 1px !important; z-index: 0 !important;
    background: conic-gradient(from var(--liq-angle) at 50% 0%, rgba(255,255,255,0.22) 0deg, transparent 55deg, rgba(33,197,94,0.12) 190deg, transparent 255deg, rgba(255,255,255,0.09) 315deg, transparent 360deg) !important;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0) !important;
    -webkit-mask-composite: destination-out !important; mask-composite: exclude !important;
    pointer-events: none !important; animation: liq-rotate 10s linear infinite !important;
}
[data-testid="stMetric"]:hover { border-color: rgba(255,255,255,0.12) !important; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 12px 40px rgba(0,0,0,0.9) !important; transform: translateY(-2px) !important; }
[data-testid="stMetricLabel"] p {
    font-family: var(--font-mono) !important; font-size: 0.62rem !important; font-weight: 700 !important;
    color: var(--text-d) !important; text-transform: uppercase !important; letter-spacing: 1.2px !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important; font-size: 1.9rem !important;
    font-weight: 800 !important; color: var(--text-w) !important; line-height: 1.15 !important;
    animation: counter-slide 0.4s ease both;
}
[data-testid="stMetricDelta"] { font-family: var(--font-mono) !important; font-size: 0.75rem !important; font-weight: 700 !important; }
[data-testid="stMetricDeltaIcon"] { display: none !important; }

/* ALERTS */
[data-testid="stAlertContainer"] {
    border-radius: var(--radius-md) !important; padding: 20px 16px !important;
    font-family: var(--font-sans) !important; border-left-width: 4px !important;
    align-items: center !important; min-height: 56px !important; height: auto !important;
}
[data-testid="stAlertContainer"] > div {
    top: -8px !important; position: relative !important; display: flex !important; align-items: center !important; background: none !important;
}
/* info */
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
    border: 1px solid rgba(59,130,246,0.2) !important; border-left: 4px solid var(--blue) !important; background: rgba(59,130,246,0.05) !important;
}
/* success */
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {
    border: 1px solid rgba(33,197,94,0.2) !important; border-left: 4px solid var(--accent) !important; background: rgba(33,197,94,0.05) !important;
}
/* warning */
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {
    border: 1px solid rgba(245,158,11,0.2) !important; border-left: 4px solid var(--amber) !important; background: rgba(245,158,11,0.05) !important;
}
/* error */
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {
    border: 1px solid rgba(239,68,68,0.2) !important; border-left: 4px solid var(--red) !important; background: rgba(239,68,68,0.05) !important;
}
[data-testid="stAlertContainer"] p {
    font-family: var(--font-sans) !important; font-size: 0.85rem !important; line-height: 1.5 !important; font-weight: 500 !important; margin: 0 !important; color: var(--text-s) !important;
}
[data-testid="stAlertContainer"] svg { flex-shrink: 0 !important; }

/* TOAST */
[data-testid="stToast"] {
    background: #0a0a0c !important; border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: var(--radius-lg) !important; box-shadow: 0 16px 48px rgba(0,0,0,0.9), inset 0 1px 0 rgba(255,255,255,0.06) !important;
    animation: reveal-up 0.3s cubic-bezier(0.4,0,0.2,1) both;
}
[data-testid="stToast"] p { font-family: var(--font-sans) !important; font-size: 0.88rem !important; color: var(--text-s) !important; font-weight: 500 !important; }

/* DATAFRAME */
[data-testid="stDataFrame"], [data-testid="stDataframe"] { border: 1px solid rgba(255,255,255,0.07) !important; border-radius: var(--radius-lg) !important; overflow: hidden !important; box-shadow: var(--shadow-card) !important; }
[data-testid="stDataFrame"] iframe, [data-testid="stDataframe"] iframe { border-radius: var(--radius-lg) !important; }
[data-testid="stTable"] table { font-family: var(--font-mono) !important; font-size: 0.82rem !important; border-collapse: collapse !important; width: 100% !important; }
[data-testid="stTable"] thead tr { background: #080808 !important; border-bottom: 1px solid var(--border) !important; }
[data-testid="stTable"] thead th { color: var(--text-d) !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.9px !important; font-size: 0.65rem !important; padding: 11px 15px !important; }
[data-testid="stTable"] tbody tr { border-bottom: 1px solid var(--border) !important; transition: background var(--transition) !important; }
[data-testid="stTable"] tbody tr:hover { background: rgba(33,197,94,0.03) !important; }
[data-testid="stTable"] tbody td { color: var(--text-s) !important; padding: 9px 15px !important; }

/* EXPANDER */
div[data-testid="stExpander"] {
    background-color: #060608 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: var(--radius-lg) !important; transition: border-color var(--transition), box-shadow var(--transition) !important; overflow: hidden !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 4px 20px rgba(0,0,0,0.6) !important;
}
div[data-testid="stExpander"]:has(summary:hover) { border-color: rgba(255,255,255,0.12) !important; }
div[data-testid="stExpander"] summary { padding: 14px 20px !important; border-bottom: 1px solid rgba(255,255,255,0.07) !important; cursor: pointer !important; }
div[data-testid="stExpander"] summary p { font-family: var(--font-mono) !important; font-size: 0.82rem !important; font-weight: 600 !important; color: var(--text-d) !important; text-transform: uppercase !important; letter-spacing: 0.6px !important; }
div[data-testid="stExpander"] summary p::before { content: "\f0b0"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 10px; color: var(--accent); display: inline-block; }
div[data-testid="stExpanderDetails"] { padding: 20px !important; background-color: #040406 !important; }

/* TABS */
[data-testid="stTabs"] { margin-bottom: 24px; }
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #060608 !important;
    border: 1px solid rgba(255,255,255,0.07) !important; border-radius: var(--radius-lg) !important;
    padding: 5px !important; gap: 2px !important; z-index: 0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 20px rgba(0,0,0,0.8) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important; border: none !important;
    padding: 10px 26px !important; z-index: 2 !important;
    transition: all var(--transition) !important; border-radius: var(--radius-md) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    background: rgba(33,197,94,0.04) !important;
}
html body .stApp [data-testid="stTabs"] [data-baseweb="tab"] p {
    font-family: var(--font-mono) !important; font-weight: 700 !important; font-size: 0.72rem !important;
    color: var(--text-d) !important; text-transform: uppercase !important; margin: 0 !important;
    transition: color var(--transition), text-shadow var(--transition) !important; letter-spacing: 1px !important;
}
html body .stApp [data-testid="stTabs"] [data-baseweb="tab"]:hover p { color: var(--text-s) !important; }
html body .stApp [data-testid="stTabs"] [aria-selected="true"] p {
    color: var(--accent) !important;
    text-shadow: 0 0 14px rgba(33,197,94,0.5) !important;
}
html body .stApp [data-testid="stTabs"] [aria-selected="true"] p::before {
    text-shadow: 0 0 10px rgba(33,197,94,0.8) !important;
    transform: scale(1.18) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: linear-gradient(135deg, rgba(33,197,94,0.10) 0%, #0d0d10 100%) !important;
    border: 1px solid rgba(33,197,94,0.28) !important; border-radius: var(--radius-md) !important;
    height: calc(100% - 10px) !important; top: 5px !important; z-index: 1 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.7), 0 0 20px rgba(33,197,94,0.08), inset 0 1px 0 rgba(33,197,94,0.12) !important;
    animation: tab-active-glow 3s ease-in-out infinite !important;
    transition: transform 0.4s cubic-bezier(0.4,0,0.2,1), width 0.4s cubic-bezier(0.4,0,0.2,1) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
[data-baseweb="tab-panel"] {
    animation: tab-content-enter 0.42s cubic-bezier(0.25,0.46,0.45,0.94) both !important;
    padding-top: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] p::before {
    font-family: "Font Awesome 6 Free" !important; font-weight: 900 !important; margin-right: 8px !important;
    display: inline-block; transition: transform var(--transition), text-shadow var(--transition) !important;
}
/* NESTED TABS (sub-modules) — underline style, visually distinct */
[data-baseweb="tab-panel"] [data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important; border: none !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 0 !important; padding: 0 0 0 2px !important; gap: 0 !important;
    box-shadow: none !important;
}
[data-baseweb="tab-panel"] [data-testid="stTabs"] [data-baseweb="tab"] {
    padding: 9px 20px !important; border-radius: 0 !important;
    border-bottom: 2px solid transparent !important; transition: border-color var(--transition), background var(--transition) !important;
}
[data-baseweb="tab-panel"] [data-testid="stTabs"] [data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.025) !important;
}
[data-baseweb="tab-panel"] [data-testid="stTabs"] [aria-selected="true"] {
    border-bottom: 2px solid var(--accent) !important;
}
[data-baseweb="tab-panel"] [data-testid="stTabs"] [aria-selected="true"] p {
    color: var(--text-w) !important; text-shadow: none !important;
}
[data-baseweb="tab-panel"] [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: transparent !important; border: none !important;
    border-radius: 0 !important; box-shadow: none !important; animation: none !important;
}
[data-baseweb="tab-panel"] [data-testid="stTabs"] [data-baseweb="tab"] p::before { display: none !important; }
/* Main tab icon prefixes */
[data-testid="stTabs"] > div > div > div > [data-baseweb="tab"]:nth-child(1) p::before { content: "\f2db"; color: var(--accent) !important; }
[data-testid="stTabs"] > div > div > div > [data-baseweb="tab"]:nth-child(2) p::before { content: "\f11e"; color: var(--accent) !important; }
[data-testid="stTabs"] > div > div > div > [data-baseweb="tab"]:nth-child(3) p::before { content: "\f0ad"; color: var(--accent) !important; }
[data-testid="stTabs"] > div > div > div > [data-baseweb="tab"]:nth-child(4) p::before { content: "\f5fd"; color: var(--accent) !important; }

/* FILE UPLOADER */
[data-testid="stFileUploader"] section {
    background: var(--bg-input) !important; border: 1px dashed var(--border-mid) !important;
    border-radius: var(--radius-md) !important; padding: 20px !important;
    transition: border-color var(--transition), background var(--transition) !important;
}
[data-testid="stFileUploader"] section:hover { border-color: var(--accent) !important; background: rgba(33,197,94,0.03) !important; }
[data-testid="stFileUploader"] section > span { font-family: var(--font-sans) !important; color: var(--text-m) !important; font-size: 0.85rem !important; }
[data-testid="stFileUploader"] button {
    background: var(--bg-raised) !important; border: 1px solid var(--border-mid) !important;
    border-radius: var(--radius-md) !important; color: var(--accent) !important;
    font-family: var(--font-mono) !important; font-size: 0.75rem !important; font-weight: 700 !important;
    letter-spacing: 0.9px !important; transition: all var(--transition) !important;
}
[data-testid="stFileUploader"] button:hover { border-color: var(--accent) !important; background: rgba(33,197,94,0.08) !important; }

/* CONTAINERS WITH BORDER */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: var(--bg-card) !important;
    border: 1px solid rgba(255,255,255,0.07) !important; border-radius: var(--radius-lg) !important;
    padding: 22px !important; transition: border-color var(--transition), box-shadow var(--transition) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 4px 24px rgba(0,0,0,0.8) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div:hover { border-color: rgba(255,255,255,0.12) !important; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 12px 40px rgba(0,0,0,0.9) !important; }

/* CARD CLASS */
.f1-card {
    background: #060608;
    border: 1px solid rgba(255,255,255,0.07); border-radius: var(--radius-lg);
    padding: 26px; margin-bottom: 20px; position: relative; overflow: hidden;
    transition: transform var(--transition-slow), box-shadow var(--transition-slow);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 4px 24px rgba(0,0,0,0.8);
}
.f1-card::before {
    content: ""; position: absolute; inset: -1px; border-radius: inherit; padding: 1px; z-index: 0;
    background: conic-gradient(from var(--liq-angle) at 35% 25%, transparent 0deg, rgba(255,255,255,0.28) 45deg, transparent 90deg, rgba(255,255,255,0.06) 200deg, transparent 260deg, rgba(255,255,255,0.14) 320deg, transparent 360deg);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: destination-out; mask-composite: exclude; pointer-events: none;
    animation: liq-rotate 9s linear infinite;
}
.f1-card:hover { transform: translateY(-4px); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 16px 48px rgba(0,0,0,0.9); }
/* DRIVER CARD — set style="--team-color:R,G,B" on the element */
.driver-card {
    --team-color: 33,197,94;
    background: #010101;
    border: 1px solid rgba(var(--team-color), 0.32); border-radius: var(--radius-lg);
    padding: 20px; position: relative; overflow: hidden;
    transition: transform var(--transition-slow), box-shadow var(--transition-slow);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 4px 28px rgba(0,0,0,0.9), 0 0 0 1px rgba(var(--team-color),0.08);
}
.driver-card::before {
    content: ""; position: absolute; inset: -1px; border-radius: inherit; padding: 1px; z-index: 0;
    background: conic-gradient(from var(--liq-angle) at 50% 0%, rgba(var(--team-color),0.9) 0deg, transparent 50deg, rgba(255,255,255,0.12) 185deg, transparent 235deg, rgba(var(--team-color),0.55) 305deg, transparent 360deg);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: destination-out; mask-composite: exclude; pointer-events: none;
    animation: liq-rotate 6s linear infinite;
}
.driver-card:hover { transform: translateY(-3px); box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 16px 48px rgba(0,0,0,0.95), 0 0 32px rgba(var(--team-color),0.18), 0 0 0 1px rgba(var(--team-color),0.2); }

/* STAT BADGE */
.stat-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(33,197,94,0.07); border: 1px solid rgba(33,197,94,0.22);
    border-radius: 99px; padding: 5px 14px;
    font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700;
    color: var(--accent); letter-spacing: 1px; text-transform: uppercase;
}

/* LIVE DOT */
.live-dot {
    display: inline-block; width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent); animation: blink-dot 1.6s ease-in-out infinite;
    box-shadow: 0 0 6px var(--accent);
}

/* HERO ANIMATIONS */
@keyframes reveal { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.hero-section { animation: reveal 0.9s cubic-bezier(0.19,1,0.22,1); }

/* PAGE ENTRANCE */
@keyframes page-enter {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.main .block-container { animation: page-enter 0.55s cubic-bezier(0.25,0.46,0.45,0.94) both !important; }

/* SHIMMER SWEEP */
@keyframes shimmer-sweep {
    0%   { transform: translateX(-120%) skewX(-20deg); }
    100% { transform: translateX(220%) skewX(-20deg); }
}

/* FLOAT ORB */
@keyframes float-orb {
    0%,100% { transform: translate(0px, 0px) scale(1); }
    33%      { transform: translate(28px, -22px) scale(1.04); }
    66%      { transform: translate(-18px, 14px) scale(0.97); }
}

/* SECTION REVEAL */
@keyframes section-reveal {
    from { opacity: 0; transform: translateY(32px); }
    to   { opacity: 1; transform: translateY(0); }
}
.section-animate { animation: section-reveal 0.75s cubic-bezier(0.19,1,0.22,1) both; }

/* NAVBAR ENTRANCE */
@keyframes nav-drop {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}
div[data-testid="stHorizontalBlock"]:first-of-type {
    animation: nav-drop 0.6s cubic-bezier(0.19,1,0.22,1) both !important;
}

@keyframes pulse-glow-icon {
    0%   { box-shadow: 0 0 0 0 rgba(33,197,94,0.45); transform: scale(1); }
    70%  { box-shadow: 0 0 0 22px rgba(33,197,94,0); transform: scale(1.06); }
    100% { box-shadow: 0 0 0 0 rgba(33,197,94,0); transform: scale(1); }
}
.radar-icon-animated {
    animation: pulse-glow-icon 2.2s infinite cubic-bezier(0.4,0,0.2,1);
    border-radius: 50%; background-color: rgba(33,197,94,0.05); padding: 22px; display: inline-block;
}

/* SIDEBAR SHELL */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080808 0%, #010101 100%) !important;
    border-right: 1px solid var(--border) !important; padding-top: 0 !important;
}
[data-testid="stSidebar"]::before {
    content: ""; display: block; height: 2px;
    background: linear-gradient(90deg, transparent 0%, rgba(33,197,94,0.8) 35%, var(--accent) 50%, rgba(33,197,94,0.8) 65%, transparent 100%);
    animation: breathe 4s ease-in-out infinite; margin-bottom: 0;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.2rem 1rem !important; }

/* SIDEBAR SELECTBOXES */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #020202 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: var(--radius-md) !important; min-height: 36px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), inset 0 2px 6px rgba(0,0,0,0.9) !important; transition: border-color var(--transition), box-shadow var(--transition) !important;
    outline: none !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover, [data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
    border-color: rgba(33,197,94,0.4) !important; box-shadow: 0 0 0 2px rgba(33,197,94,0.07), inset 0 1px 0 rgba(255,255,255,0.03), inset 0 2px 6px rgba(0,0,0,0.9) !important;
    outline: none !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] div { font-family: var(--font-sans) !important; font-size: 0.83rem !important; color: var(--text-s) !important; }
[data-testid="stSidebar"] div[data-baseweb="select"] span[data-baseweb="tag"] {
    background-color: rgba(33,197,94,0.1) !important; color: var(--accent) !important;
    font-family: var(--font-mono) !important; font-size: 0.68rem !important; font-weight: 700 !important;
    border-radius: 4px !important; border: 1px solid rgba(33,197,94,0.28) !important; padding: 2px 7px !important;
}

/* SIDEBAR INPUTS */
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input,
[data-testid="stSidebar"] [data-baseweb="input"] {
    background-color: #040406 !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important; color: var(--text-s) !important;
    font-family: var(--font-sans) !important; font-size: 0.83rem !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), inset 0 2px 6px rgba(0,0,0,0.8) !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus, [data-testid="stSidebar"] [data-testid="stNumberInput"] input:focus {
    border-color: rgba(33,197,94,0.45) !important; box-shadow: 0 0 0 2px rgba(33,197,94,0.08), inset 0 1px 0 rgba(255,255,255,0.04), 0 0 10px rgba(33,197,94,0.05) !important;
}

/* SIDEBAR SLIDER */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] { width: 14px !important; height: 14px !important; }

/* SIDEBAR CHECKBOX AND RADIO */
[data-testid="stSidebar"] [data-baseweb="checkbox"] label span:last-child,
[data-testid="stSidebar"] [data-baseweb="radio"] label span:last-child { font-family: var(--font-sans) !important; font-size: 0.83rem !important; color: var(--text-s) !important; }

/* SIDEBAR PRIMARY BUTTON */
[data-testid="stSidebar"] button[kind="primary"] {
    height: 44px !important; width: 100% !important; border-radius: var(--radius-md) !important;
    box-shadow: 0 4px 18px rgba(33,197,94,0.2), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    animation: none !important;
}
[data-testid="stSidebar"] button[kind="primary"] p { font-size: 0.8rem !important; letter-spacing: 2px !important; }
[data-testid="stSidebar"] button[kind="primary"] p::before { display: none !important; }

/* SIDEBAR SECONDARY BUTTON */
[data-testid="stSidebar"] button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(33,197,94,0.1) 0%, rgba(13,13,16,1) 70%) !important;
    border: 1px solid rgba(33,197,94,0.3) !important; border-radius: var(--radius-md) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: linear-gradient(135deg, rgba(33,197,94,0.18) 0%, rgba(20,20,24,1) 70%) !important;
    border-color: var(--accent) !important; box-shadow: 0 0 16px rgba(33,197,94,0.15) !important; transform: none !important;
}
[data-testid="stSidebar"] button[kind="secondary"] p { font-family: var(--font-mono) !important; font-size: 0.72rem !important; letter-spacing: 1.4px !important; color: var(--text-s) !important; }

/* SIDEBAR WIDGET LABELS — improved contrast for Recognition vs Recall */
[data-testid="stSidebar"] .stWidgetLabel p, [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: 0.70rem !important; color: var(--text-m) !important; letter-spacing: 1.1px !important; }

/* SIDEBAR CUSTOM CLASSES — Hick's Law: clear sections reduce choice complexity */
.sb-section-label {
    display: flex; align-items: center; gap: 9px;
    font-family: var(--font-mono); font-size: 0.64rem; font-weight: 700;
    color: var(--accent); letter-spacing: 2.2px; text-transform: uppercase; margin: 26px 0 11px 0; padding: 0; position: relative;
}
.sb-section-label::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(33,197,94,0.25), transparent); margin-left: 4px; }
.sb-section-label i {
    font-size: 0.7rem; width: 20px; height: 20px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(33,197,94,0.08); border: 1px solid rgba(33,197,94,0.18); border-radius: var(--radius-xs); flex-shrink: 0;
}
.sb-meta-label {
    display: flex; align-items: center; gap: 6px;
    font-family: var(--font-mono); font-size: 0.52rem; font-weight: 700;
    color: var(--text-d); letter-spacing: 1.6px; text-transform: uppercase; margin: 10px 0 5px 0;
}
.sb-meta-label i { font-size: 0.56rem; color: var(--amber); }
.sb-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(58,58,63,0.7) 25%, rgba(58,58,63,0.7) 75%, transparent);
    margin: 24px 0;
}
.sb-session-badge {
    display: flex; align-items: center; gap: 9px;
    background: linear-gradient(135deg, rgba(33,197,94,0.06) 0%, transparent 100%);
    border: 1px solid rgba(33,197,94,0.2); border-radius: var(--radius-md);
    padding: 9px 13px; margin-top: 8px; position: relative; overflow: hidden;
}
.sb-session-badge::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(33,197,94,0.4), transparent);
}
.sb-session-badge i { color: var(--accent); font-size: 0.68rem; flex-shrink: 0; }
.sb-session-badge span { font-family: var(--font-mono); font-size: 0.63rem; color: var(--text-s); line-height: 1.45; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sb-footer { text-align: center; font-family: var(--font-sans); font-size: 0.7rem; color: var(--text-d); margin-top: 18px; margin-bottom: 6px; letter-spacing: 0.3px; }
.sb-footer a { color: var(--accent); text-decoration: none; font-weight: 600; }
.sb-footer a:hover { text-decoration: underline; opacity: 0.8; }

/* SIDEBAR SCROLLBAR */
[data-testid="stSidebar"] ::-webkit-scrollbar { width: 2px; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 99px; }

/* LANGUAGE SELECTOR pill in navbar last column */
div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] > div {
    background: rgba(6,24,13,0.85) !important;
    border: 1px solid rgba(33,197,94,0.28) !important;
    border-radius: 99px !important;
    min-height: 30px !important;
    padding: 0 4px 0 10px !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] > div:hover,
div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] > div:focus-within {
    border-color: rgba(33,197,94,0.6) !important;
    box-shadow: 0 0 14px rgba(33,197,94,0.2) !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] div,
div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] span {
    color: #21C55E !important;
    font-family: 'Geist Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-shadow: 0 0 6px rgba(33,197,94,0.3) !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] svg {
    fill: rgba(33,197,94,0.7) !important;
    width: 13px !important; height: 13px !important;
}

/* ── TAB BANNER — Gestalt: enclosure groups tab context ─────────────── */
.tab-banner {
    display: flex; align-items: center; gap: 16px;
    background: linear-gradient(135deg, rgba(33,197,94,0.055) 0%, rgba(10,10,14,0) 65%);
    border: 1px solid rgba(33,197,94,0.15);
    border-radius: var(--radius-lg); padding: 18px 24px;
    margin-bottom: 32px; position: relative; overflow: hidden;
    animation: tab-content-enter 0.4s cubic-bezier(0.25,0.46,0.45,0.94) both;
}
.tab-banner::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(33,197,94,0.5), transparent);
}
.tab-banner::after {
    content: ""; position: absolute; top: 0; left: -60%;
    width: 35%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(33,197,94,0.04), transparent);
    transform: skewX(-20deg);
    animation: banner-shimmer 6s ease-in-out 0.6s infinite;
    pointer-events: none;
}
.tab-banner-icon {
    width: 46px; height: 46px; border-radius: var(--radius-md);
    background: rgba(33,197,94,0.08); border: 1px solid rgba(33,197,94,0.22);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; font-size: 1.3rem;
    box-shadow: 0 0 14px rgba(33,197,94,0.08);
    animation: icon-bounce 3.5s ease-in-out 1s infinite;
}
.tab-banner-body { flex: 1; min-width: 0; }
.tab-banner-title {
    font-family: var(--font-mono); font-size: 0.88rem; font-weight: 800;
    color: var(--text-w); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 4px;
}
.tab-banner-desc {
    font-family: var(--font-sans); font-size: 0.79rem; color: var(--text-m); line-height: 1.5;
}
.tab-banner-badge {
    display: flex; align-items: center; gap: 6px; flex-shrink: 0;
    background: rgba(33,197,94,0.07); border: 1px solid rgba(33,197,94,0.2);
    border-radius: 99px; padding: 5px 13px;
    font-family: var(--font-mono); font-size: 0.6rem; font-weight: 700;
    color: var(--accent); letter-spacing: 1.2px; text-transform: uppercase;
}

/* ── SECTION SEPARATOR — Gestalt: proximity creates perceived content groups ── */
.section-sep {
    display: flex; align-items: center; gap: 14px;
    margin: var(--section-gap) 0 var(--sp-7);
    animation: tab-content-enter 0.5s cubic-bezier(0.25,0.46,0.45,0.94) both;
}
.section-sep-icon {
    width: 28px; height: 28px; border-radius: var(--radius-sm);
    background: rgba(33,197,94,0.08); border: 1px solid rgba(33,197,94,0.18);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; flex-shrink: 0; color: var(--accent);
}
.section-sep-label {
    font-family: var(--font-mono); font-size: 0.6rem; font-weight: 700;
    color: var(--text-d); text-transform: uppercase; letter-spacing: 2.2px;
}
.section-sep-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(33,197,94,0.18), transparent);
    transform-origin: left center;
    animation: sep-line-grow 0.6s 0.15s cubic-bezier(0.25,0.46,0.45,0.94) both;
}

/* ── STAGGER ANIMATIONS for child cards ────────────────────────────────── */
.stagger-1 { animation: stagger-card 0.48s 0.04s cubic-bezier(0.25,0.46,0.45,0.94) both; }
.stagger-2 { animation: stagger-card 0.48s 0.10s cubic-bezier(0.25,0.46,0.45,0.94) both; }
.stagger-3 { animation: stagger-card 0.48s 0.16s cubic-bezier(0.25,0.46,0.45,0.94) both; }
.stagger-4 { animation: stagger-card 0.48s 0.22s cubic-bezier(0.25,0.46,0.45,0.94) both; }

/* ── INLINE METRIC ROW ─────────────────────────────────────────────────── */
.inline-kpi-row {
    display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px;
}
.inline-kpi {
    flex: 1; min-width: 110px; background: #060608;
    border: 1px solid rgba(255,255,255,0.07); border-radius: var(--radius-md);
    padding: 12px 16px; position: relative; overflow: hidden;
    transition: transform var(--transition), border-color var(--transition), box-shadow var(--transition);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 2px 12px rgba(0,0,0,0.7);
    animation: stagger-card 0.5s cubic-bezier(0.25,0.46,0.45,0.94) both;
}
.inline-kpi:hover {
    transform: translateY(-2px);
    border-color: rgba(33,197,94,0.22);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 8px 28px rgba(0,0,0,0.9), 0 0 14px rgba(33,197,94,0.06);
}
.inline-kpi-label {
    font-family: var(--font-mono); font-size: 0.56rem; font-weight: 700;
    color: var(--text-d); text-transform: uppercase; letter-spacing: 1.4px; margin-bottom: 6px;
}
.inline-kpi-value {
    font-family: var(--font-mono); font-size: 1.15rem; font-weight: 800;
    color: var(--text-w); line-height: 1;
}
.inline-kpi-sub {
    font-family: var(--font-sans); font-size: 0.68rem; color: var(--text-d); margin-top: 3px;
}

/* ── CHART FRAME — wraps Streamlit plotly outputs with a labelled header ── */
.chart-frame {
    background: #030305;
    border: 1px solid rgba(255,255,255,0.06); border-radius: var(--radius-xl);
    overflow: hidden; margin-bottom: 24px; position: relative;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.035), var(--elev-2);
    transition: border-color var(--transition), box-shadow var(--transition-slow);
    will-change: transform;
}
.chart-frame:hover {
    border-color: rgba(255,255,255,0.10);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.055), var(--elev-3);
}
.chart-frame-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 20px 11px;
    border-bottom: 1px solid rgba(255,255,255,0.045);
    background: rgba(255,255,255,0.012);
    gap: 12px;
}
.chart-frame-title {
    display: flex; align-items: center; gap: 10px;
    font-family: var(--font-mono); font-size: 0.63rem; font-weight: 700;
    color: var(--text-d); text-transform: uppercase; letter-spacing: 2px;
}
.chart-frame-title i { color: var(--accent); font-size: 0.72rem; }
.chart-frame-meta {
    display: flex; align-items: center; gap: 8px;
}
.chart-frame-badge {
    display: inline-flex; align-items: center; gap: 5px; flex-shrink: 0;
    font-family: var(--font-mono); font-size: 0.54rem; font-weight: 700;
    padding: 3px 10px; border-radius: 99px;
    background: rgba(33,197,94,0.06); border: 1px solid rgba(33,197,94,0.16);
    color: var(--accent); letter-spacing: 1px; text-transform: uppercase;
    transition: background var(--transition), border-color var(--transition);
}
.chart-frame:hover .chart-frame-badge {
    background: rgba(33,197,94,0.10); border-color: rgba(33,197,94,0.28);
}
.chart-frame-body { padding: 0; }

/* ── REVEAL CARD — scroll-triggered entrance animation ───────────────── */
/* Base state: hidden. JS IntersectionObserver adds .is-visible */
.reveal-card {
    opacity: 0;
    transform: translateY(26px) scale(0.985);
    transition: opacity 0.6s var(--ease-out),
                transform 0.6s var(--ease-out);
    will-change: transform, opacity;
}
.reveal-card.is-visible {
    opacity: 1;
    transform: translateY(0) scale(1);
}
/* Stagger delays — Gestalt: elements that move together feel grouped */
.reveal-card.rd-1 { transition-delay: 0.00s; }
.reveal-card.rd-2 { transition-delay: 0.07s; }
.reveal-card.rd-3 { transition-delay: 0.14s; }
.reveal-card.rd-4 { transition-delay: 0.21s; }
.reveal-card.rd-5 { transition-delay: 0.28s; }
.reveal-card.rd-6 { transition-delay: 0.35s; }
/* Pop variant — spring feel */
.reveal-card.pop {
    transform: scale(0.88) translateY(12px);
    transition: opacity 0.5s var(--ease-spring),
                transform 0.5s var(--ease-spring);
}
.reveal-card.pop.is-visible { transform: scale(1) translateY(0); }
/* From-left / from-right variants */
.reveal-card.from-left  { transform: translateX(-30px); }
.reveal-card.from-right { transform: translateX(30px); }
.reveal-card.from-left.is-visible,
.reveal-card.from-right.is-visible { transform: translateX(0); }

/* ── KPI STRIP — horizontal key metrics bar at top of sections ─────── */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px; margin-bottom: 28px;
}
.kpi-tile {
    background: #040407;
    border: 1px solid rgba(255,255,255,0.065);
    border-radius: var(--radius-lg); padding: 14px 18px;
    position: relative; overflow: hidden;
    transition: transform var(--transition-spring), border-color var(--transition), box-shadow var(--transition-slow);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), var(--elev-1);
    cursor: default;
    animation: number-count 0.45s var(--ease-out) both;
}
.kpi-tile::after {
    content: ""; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: var(--kpi-color, var(--accent));
    opacity: 0.35; transform: scaleX(0); transform-origin: left;
    transition: transform 0.4s var(--ease-spring), opacity var(--transition);
}
.kpi-tile:hover {
    transform: translateY(-3px) scale(1.005);
    border-color: rgba(255,255,255,0.13);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), var(--elev-3);
}
.kpi-tile:hover::after { transform: scaleX(1); opacity: 0.6; }
.kpi-tile-label {
    font-family: var(--font-mono); font-size: 0.54rem; font-weight: 700;
    color: var(--text-d); text-transform: uppercase; letter-spacing: 1.6px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 6px;
}
.kpi-tile-label i { color: var(--kpi-color, var(--accent)); opacity: 0.75; font-size: 0.62rem; }
.kpi-tile-value {
    font-family: var(--font-mono); font-size: 1.28rem; font-weight: 800;
    color: var(--text-w); line-height: 1; letter-spacing: -0.5px;
    animation: number-count 0.4s var(--ease-out) both;
}
.kpi-tile-sub {
    font-family: var(--font-sans); font-size: 0.67rem; color: var(--text-d); margin-top: 4px;
}
.kpi-tile-delta {
    font-family: var(--font-mono); font-size: 0.62rem; font-weight: 700;
    display: inline-flex; align-items: center; gap: 3px; margin-top: 5px;
    padding: 2px 6px; border-radius: 4px;
}
.kpi-tile-delta.up   { color: var(--accent); background: rgba(33,197,94,0.08); }
.kpi-tile-delta.down { color: var(--red);    background: rgba(239,68,68,0.08); }
.kpi-tile-delta.neu  { color: var(--text-d); background: rgba(255,255,255,0.04); }

/* ── DATA PILL — inline contextual tag ────────────────────────────────── */
.data-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px 3px 8px; border-radius: 99px;
    font-family: var(--font-mono); font-size: 0.6rem; font-weight: 700;
    letter-spacing: 0.8px; text-transform: uppercase;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09);
    color: var(--text-m); transition: all var(--transition);
    cursor: default;
}
.data-pill i { font-size: 0.62rem; }
.data-pill.accent { background: rgba(33,197,94,0.07); border-color: rgba(33,197,94,0.22); color: var(--accent); }
.data-pill.amber  { background: rgba(245,158,11,0.07); border-color: rgba(245,158,11,0.22); color: var(--amber); }
.data-pill.red    { background: rgba(239,68,68,0.07);  border-color: rgba(239,68,68,0.22);  color: var(--red); }
.data-pill.blue   { background: rgba(59,130,246,0.07); border-color: rgba(59,130,246,0.22); color: var(--blue); }
.data-pill.purple { background: rgba(168,85,247,0.07); border-color: rgba(168,85,247,0.22); color: var(--purple); }

/* ── SKELETON LOADER — perceived performance ────────────────────────── */
.skeleton {
    background: linear-gradient(90deg,
        rgba(255,255,255,0.04) 0%,
        rgba(255,255,255,0.08) 50%,
        rgba(255,255,255,0.04) 100%);
    background-size: 400px 100%;
    animation: skeleton-wave 1.6s ease-in-out infinite;
    border-radius: var(--radius-sm);
}
.skeleton-line  { height: 12px; border-radius: 6px; margin-bottom: 8px; }
.skeleton-block { height: 160px; border-radius: var(--radius-lg); margin-bottom: 16px; }

/* ── PROGRESS BAR ─────────────────────────────────────────────────────── */
.prog-bar-wrap {
    background: rgba(255,255,255,0.05); border-radius: 99px; height: 5px;
    overflow: hidden; margin: 8px 0;
}
.prog-bar-fill {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, var(--prog-color, var(--accent)) 0%, color-mix(in srgb, var(--prog-color, var(--accent)) 70%, white) 100%);
    transform-origin: left; width: var(--prog-pct, 50%);
    animation: fill-bar 0.8s var(--ease-spring) both;
    box-shadow: 0 0 8px var(--prog-color, var(--accent-glow));
}

/* ── PLOTLY CHART — global improvements ──────────────────────────────── */
[data-testid="stPlotlyChart"] {
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
    transition: box-shadow var(--transition-slow) !important;
}
[data-testid="stPlotlyChart"]:hover {
    box-shadow: var(--elev-3) !important;
}
/* Remove default plotly background bleed */
[data-testid="stPlotlyChart"] .js-plotly-plot .plotly { border-radius: var(--radius-lg) !important; }

/* ── IMPROVED SELECTBOX FOCUS RING (keyboard a11y) ───────────────────── */
[data-baseweb="select"] > div:focus-within {
    outline: none !important;
}

/* ── FOCUS VISIBLE (keyboard navigation) ────────────────────────────── */
:focus-visible {
    outline: 2px solid rgba(33,197,94,0.6) !important;
    outline-offset: 2px !important;
}

/* ── SMOOTH SCROLL ─────────────────────────────────────────────────────── */
html { scroll-behavior: smooth; }

/* ── COLUMN STAGGER — scoped to .main to avoid animating nav ──────── */
.main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) { animation: card-pop 0.5s 0.00s var(--ease-out) both; }
.main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) { animation: card-pop 0.5s 0.07s var(--ease-out) both; }
.main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) { animation: card-pop 0.5s 0.14s var(--ease-out) both; }
.main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(4) { animation: card-pop 0.5s 0.21s var(--ease-out) both; }
.main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(5) { animation: card-pop 0.5s 0.28s var(--ease-out) both; }

/* ── METRIC improved value animation ────────────────────────────────── */
[data-testid="stMetricValue"] {
    animation: number-count 0.5s var(--ease-spring) both !important;
}

/* ── EMPTY STATE ANIMATIONS (orbit, hero-enter, etc.) ───────────────── */
@keyframes orbit {
    from { transform: rotate(0deg) translateX(52px) rotate(0deg); }
    to   { transform: rotate(360deg) translateX(52px) rotate(-360deg); }
}
@keyframes orbit2 {
    from { transform: rotate(180deg) translateX(72px) rotate(-180deg); }
    to   { transform: rotate(540deg) translateX(72px) rotate(-540deg); }
}
@keyframes fade-step {
    0%,100% { opacity: 0.35; } 50% { opacity: 1; }
}
@keyframes hero-enter {
    from { opacity:0; transform:translateY(28px) scale(0.96); }
    to   { opacity:1; transform:translateY(0) scale(1); }
}
@keyframes glyph-glow {
    0%,100% { box-shadow:0 0 0 0 rgba(33,197,94,0.45), 0 0 28px rgba(33,197,94,0.08); }
    50%     { box-shadow:0 0 0 16px rgba(33,197,94,0), 0 0 52px rgba(33,197,94,0.22); }
}

/* ── CONTENT GROUP — Gestalt proximity: visually clusters related blocks ── */
.content-group {
    background: rgba(255,255,255,0.012);
    border: 1px solid rgba(255,255,255,0.046);
    border-radius: var(--radius-xl);
    padding: var(--card-pad) var(--sp-7);
    margin-bottom: var(--block-gap);
    position: relative;
}
.content-group + .content-group { margin-top: var(--sp-2); }

/* ── VON RESTORFF — isolation creates memorability for key data ─────── */
/* Highlight the statistically best/fastest element */
.vr-highlight {
    background: rgba(var(--team-color, 33,197,94), 0.055) !important;
    border-color: rgba(var(--team-color, 33,197,94), 0.30) !important;
    box-shadow: 0 0 0 1px rgba(var(--team-color, 33,197,94), 0.18), var(--elev-2) !important;
    position: relative;
}
.vr-highlight::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(var(--team-color, 33,197,94), 1), transparent);
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    opacity: 0.6;
}
/* Best lap / fastest sector — accent color isolation */
.best-cell {
    color: var(--accent) !important;
    font-weight: 800 !important;
    text-shadow: 0 0 12px rgba(33,197,94,0.45) !important;
}
/* Isolated accent badge pill (larger than data-pill) */
.vr-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 14px 4px 10px; border-radius: 99px;
    font-family: var(--font-mono); font-size: 0.68rem; font-weight: 800;
    letter-spacing: 1px; text-transform: uppercase;
    background: rgba(33,197,94,0.10);
    border: 1px solid rgba(33,197,94,0.35);
    color: var(--accent);
    box-shadow: 0 0 14px rgba(33,197,94,0.15);
    animation: pulse-glow 2.4s ease-in-out infinite;
}
.vr-badge i { font-size: 0.7rem; }

/* ── CURSOR AURA CSS ─────────────────────────────────────────────────── */
#f1-cursor-aura {
    position: fixed; pointer-events: none; z-index: 0;
    width: 340px; height: 340px; border-radius: 50%;
    transform: translate(-50%,-50%);
    background: radial-gradient(circle, rgba(33,197,94,0.038) 0%, transparent 68%);
    transition: left 0.08s linear, top 0.08s linear, opacity 0.4s ease;
    opacity: 0;
}

/* ══════════════════════════════════════════════════════════════════════
   RESPONSIVE — MOBILE FIRST
   All media queries: max-width 768px (phone) and 1024px (tablet)
   ══════════════════════════════════════════════════════════════════════ */

/* ── TABLET (≤1024px) ── */
@media (max-width: 1024px) {
    .block-container {
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }
    .page-hero h1 { font-size: 2.4rem; }
    button[kind="primary"] { width: 340px !important; }
    .hero-orb-1 { width: 280px; height: 280px; }
    .hero-orb-2 { width: 240px; height: 240px; }
    .hero-orb-3 { width: 180px; height: 180px; }
}

/* ── PHONE (≤768px) ── */
@media (max-width: 768px) {

    /* ── Layout container ── */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        max-width: 100% !important;
    }

    /* ── Typography scale ── */
    h1, .stMarkdown h1 { font-size: 1.45rem !important; letter-spacing: 1px !important; }
    h2, .stMarkdown h2 { font-size: 1.15rem !important; }
    h3, .stMarkdown h3 { font-size: 0.92rem !important; }
    p, .stMarkdown p   { font-size: 0.82rem !important; }

    /* ── Page hero ── */
    .page-hero { padding: 24px 12px 20px; }
    .page-hero h1 { font-size: 1.7rem; letter-spacing: 1px; }
    .page-hero p  { font-size: 0.85rem; }

    /* ── Section title ── */
    .section-title { font-size: 0.56rem; margin: 24px 0 10px; }

    /* ── Navbar container ── */
    div[data-testid="stHorizontalBlock"]:first-of-type {
        border-radius: 16px !important;
        padding: 10px 16px !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
    }
    /* Logo column: full width on mobile */
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:first-child {
        flex: 0 0 auto !important;
        min-width: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type img {
        height: 36px !important;
    }
    /* Nav buttons — tighter text */
    html body div.stApp div[data-testid="stHorizontalBlock"]:first-of-type div.stButton > button p {
        font-size: 0.65rem !important;
        letter-spacing: 1px !important;
    }
    /* Language selector pill */
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] > div {
        min-height: 26px !important;
        padding: 0 4px 0 8px !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] div,
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:last-child div[data-baseweb="select"] span {
        font-size: 0.62rem !important;
    }
    .nav-active-item { font-size: 0.65rem; letter-spacing: 1px; }

    /* ── Primary CTA button ── */
    button[kind="primary"] {
        width: 100% !important;
        max-width: 100vw !important;
        height: 60px !important;
        border-radius: var(--radius-lg) !important;
    }
    button[kind="primary"] p { font-size: 0.9rem !important; letter-spacing: 2px !important; }
    div.element-container:has(button[kind="primary"]),
    div[data-testid="stButton"]:has(button[kind="primary"]) {
        padding: 0 12px !important;
        margin-bottom: 32px !important;
    }

    /* ── Tabs — horizontal scroll ── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: none !important;
        padding: 4px !important;
        gap: 1px !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar { display: none !important; }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        padding: 8px 14px !important;
        flex-shrink: 0 !important;
    }
    html body .stApp [data-testid="stTabs"] [data-baseweb="tab"] p {
        font-size: 0.62rem !important;
        letter-spacing: 0.6px !important;
        white-space: nowrap !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] p::before { display: none !important; }

    /* ── Metrics ── */
    [data-testid="stMetric"] { padding: 14px 16px !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }

    /* ── KPI strip — 2 columns on phone ── */
    .kpi-strip { grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; }
    .kpi-tile { padding: 12px 14px !important; }
    .kpi-tile-value { font-size: 1.05rem !important; }

    /* ── Inline KPI row ── */
    .inline-kpi-row { gap: 8px !important; }
    .inline-kpi { min-width: 80px !important; padding: 10px 12px !important; }
    .inline-kpi-value { font-size: 0.95rem !important; }

    /* ── Tab banner — stack vertically ── */
    .tab-banner {
        flex-direction: column !important;
        gap: 8px !important;
        padding: 14px 16px !important;
    }
    .tab-banner-badge { display: none !important; }

    /* ── Chart frame ── */
    .chart-frame-header { padding: 10px 14px 9px !important; }
    .chart-frame-title  { font-size: 0.56rem !important; }

    /* ── Hero background orbs — smaller on mobile ── */
    .hero-orb-1 { width: 200px; height: 200px; top: -60px; left: -60px; }
    .hero-orb-2 { width: 160px; height: 160px; top: 120px; right: -60px; }
    .hero-orb-3 { display: none; }

    /* ── Data pill ── */
    .data-pill { font-size: 0.55rem !important; padding: 3px 8px 3px 6px !important; }

    /* ── Section separator ── */
    .section-sep { margin: 24px 0 14px !important; }

    /* ── Sidebar always-on-top on mobile ── */
    [data-testid="stSidebar"] { z-index: 999 !important; }

    /* ── Show sidebar toggle button on all routes ── */
    [data-testid="collapsedControl"] { display: flex !important; }

    /* ── Expander ── */
    div[data-testid="stExpander"] summary { padding: 12px 16px !important; }
    div[data-testid="stExpanderDetails"] { padding: 14px 12px !important; }

    /* ── Scrollbar hidden on mobile ── */
    ::-webkit-scrollbar { width: 2px; height: 2px; }

    /* ── stWidgetLabel ── */
    .stWidgetLabel p, label p, [data-testid="stWidgetLabel"] p {
        font-size: 0.68rem !important;
        letter-spacing: 0.7px !important;
    }

    /* ── Sidebar footer ── */
    .sb-footer { font-size: 0.64rem !important; }

    /* ── Column stagger animations — reduce delay on mobile ── */
    .main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) { animation-delay: 0s !important; }
    .main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) { animation-delay: 0.04s !important; }
    .main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) { animation-delay: 0.08s !important; }
    .main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(4) { animation-delay: 0.12s !important; }
    .main [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(5) { animation-delay: 0.16s !important; }

    /* ── Plotly chart — ensure full width ── */
    [data-testid="stPlotlyChart"] { border-radius: var(--radius-md) !important; }

    /* ── Select/Multiselect dropdown ── */
    div[data-baseweb="select"] > div { min-height: 36px !important; }
    div[data-baseweb="popover"] ul { max-height: 220px !important; overflow-y: auto !important; }
}
"""
    _links_json = json.dumps(_FONT_LINKS)
    _css_json   = json.dumps(_CSS)
    components.html(f"""
<script>
(function() {{
  var doc = window.parent.document;

  /* ── viewport meta — prevents mobile browsers from zooming out ── */
  if (!doc.querySelector('meta[name="viewport"]')) {{
    var vm = doc.createElement('meta');
    vm.name = 'viewport';
    vm.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0';
    doc.head.appendChild(vm);
  }} else {{
    doc.querySelector('meta[name="viewport"]').content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0';
  }}

  /* ── inject fonts & CSS ── */
  var links = {_links_json};
  links.forEach(function(href) {{
    if (!doc.querySelector('link[href="' + href + '"]')) {{
      var el = doc.createElement('link');
      el.rel = 'stylesheet'; el.href = href; el.crossOrigin = 'anonymous';
      doc.head.appendChild(el);
    }}
  }});
  var prev = doc.getElementById('f1-global-css');
  if (prev) prev.remove();
  var style = doc.createElement('style');
  style.id = 'f1-global-css';
  style.textContent = {_css_json};
  doc.head.appendChild(style);

  /* ── AMBIENT PARTICLE SYSTEM ── */
  if (!doc.getElementById('f1-particles')) {{
    var cv = doc.createElement('canvas');
    cv.id = 'f1-particles';
    cv.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;opacity:0.35;';
    doc.body.insertBefore(cv, doc.body.firstChild);
    var ctx = cv.getContext('2d');
    var W = cv.width  = window.innerWidth;
    var H = cv.height = window.innerHeight;
    var pts = Array.from({{length:55}}, function() {{
      return {{ x:Math.random()*W, y:Math.random()*H,
               sz:Math.random()*1.1+0.2,
               vx:(Math.random()-0.5)*0.18, vy:(Math.random()-0.5)*0.18,
               a:Math.random()*0.3+0.05 }};
    }});
    function drawPts() {{
      ctx.clearRect(0,0,W,H);
      pts.forEach(function(p) {{
        p.x+=p.vx; p.y+=p.vy;
        if(p.x<0) p.x=W; if(p.x>W) p.x=0;
        if(p.y<0) p.y=H; if(p.y>H) p.y=0;
        ctx.beginPath(); ctx.arc(p.x,p.y,p.sz,0,6.283);
        ctx.fillStyle='rgba(33,197,94,'+p.a+')'; ctx.fill();
      }});
      requestAnimationFrame(drawPts);
    }}
    drawPts();
    var rt; window.addEventListener('resize',function(){{
      clearTimeout(rt); rt=setTimeout(function(){{
        W=cv.width=window.innerWidth; H=cv.height=window.innerHeight;
      }},150);
    }});
  }}

  /* ── CURSOR AURA — ambient light that follows mouse ── */
  if (!doc.getElementById('f1-cursor-aura')) {{
    var aura = doc.createElement('div');
    aura.id = 'f1-cursor-aura';
    doc.body.appendChild(aura);
    var mx=0, my=0, ax=0, ay=0;
    doc.addEventListener('mousemove', function(e) {{ mx=e.clientX; my=e.clientY; aura.style.opacity='1'; }});
    doc.addEventListener('mouseleave', function() {{ aura.style.opacity='0'; }});
    (function animAura() {{
      ax += (mx-ax)*0.10; ay += (my-ay)*0.10;
      aura.style.left = ax+'px'; aura.style.top = ay+'px';
      requestAnimationFrame(animAura);
    }})();
  }}

  /* ── BUTTON RIPPLE EFFECT — tactile micro-interaction ── */
  if (!doc.getElementById('f1-ripple-style')) {{
    var rs = doc.createElement('style');
    rs.id = 'f1-ripple-style';
    rs.textContent = '@keyframes f1-ripple{{to{{transform:scale(4);opacity:0}}}}';
    doc.head.appendChild(rs);
    doc.addEventListener('click', function(e) {{
      var btn = e.target.closest('button');
      if (!btn) return;
      var old = btn.querySelector('.f1-rip');
      if (old) old.remove();
      var r = doc.createElement('span');
      r.className = 'f1-rip';
      var rect = btn.getBoundingClientRect();
      var sz = Math.max(rect.width, rect.height);
      r.style.cssText = 'position:absolute;border-radius:50%;pointer-events:none;'+
        'width:'+sz+'px;height:'+sz+'px;'+
        'top:'+(e.clientY-rect.top-sz/2)+'px;'+
        'left:'+(e.clientX-rect.left-sz/2)+'px;'+
        'background:rgba(33,197,94,0.14);transform:scale(0);'+
        'animation:f1-ripple 0.55s ease forwards;';
      var cs = window.getComputedStyle(btn);
      if (cs.position==='static') btn.style.position='relative';
      btn.style.overflow='hidden';
      btn.appendChild(r);
      setTimeout(function(){{ if(r.parentNode) r.parentNode.removeChild(r); }}, 600);
    }});
  }}

  /* ── INTERSECTION OBSERVER — scroll-reveal for .reveal-card elements ── */
  if (!window._f1IO) {{
    window._f1IO = new IntersectionObserver(function(entries) {{
      entries.forEach(function(e) {{
        if (e.isIntersecting) {{
          e.target.classList.add('is-visible');
          window._f1IO.unobserve(e.target);
        }}
      }});
    }}, {{ threshold: 0.06, rootMargin: '0px 0px -30px 0px' }});

    /* MutationObserver watches for new .reveal-card elements added by Streamlit */
    var mo = new MutationObserver(function() {{
      doc.querySelectorAll('.reveal-card:not(.is-visible)').forEach(function(el) {{
        window._f1IO.observe(el);
      }});
    }});
    mo.observe(doc.body, {{ childList:true, subtree:true }});
    /* Initial scan */
    doc.querySelectorAll('.reveal-card:not(.is-visible)').forEach(function(el) {{
      window._f1IO.observe(el);
    }});
  }}

  /* ── SELECT HOVER FIX — prevent focus outline flash ── */
  doc.querySelectorAll('[data-baseweb="select"] > div').forEach(function(el) {{
    el.addEventListener('focus', function() {{ el.style.outline='none'; }});
  }});

}})();
</script>
""", height=0, scrolling=False)
