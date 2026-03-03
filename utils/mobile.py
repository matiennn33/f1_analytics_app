"""
Mobile responsive CSS for F1 Telemetry Analytics app.
Ensures proper display on tablets (≥768px) and phones (<768px).
"""
from __future__ import annotations


def get_mobile_responsive_css() -> str:
    """Return mobile-responsive CSS for the app."""
    return """
    <style>
        /* ============================================
           MOBILE RESPONSIVE BREAKPOINTS
           ============================================ */

        /* Tablets and up (≥768px) */
        @media (max-width: 1024px) {
            /* Sidebar adjustments */
            [data-testid="stSidebar"] {
                width: 250px !important;
            }

            /* Main content padding */
            .main {
                padding-right: 1rem !important;
                padding-left: 1rem !important;
            }

            /* Card styling */
            .f1-card {
                padding: 15px !important;
                margin-bottom: 15px !important;
            }

            /* Chart height adjustments */
            .plotly-graph-div {
                height: 400px !important;
            }
        }

        /* Smartphones (≤768px) */
        @media (max-width: 768px) {
            /* Hide sidebar by default, show on mobile */
            [data-testid="stSidebar"] {
                width: 100% !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                z-index: 999 !important;
                opacity: 0 !important;
                transition: opacity 0.3s !important;
                pointer-events: none !important;
            }

            /* Mobile-friendly spacing */
            .main {
                padding: 1rem 0.5rem !important;
            }

            /* Header styling */
            h1 {
                font-size: 2rem !important;
                line-height: 1.2 !important;
            }

            h2, h3 {
                font-size: 1.3rem !important;
            }

            /* Button sizing */
            .stButton > button {
                width: 100% !important;
                padding: 0.5rem !important;
                font-size: 0.9rem !important;
            }

            /* Tab text sizing */
            .stTabs [role="tablist"] button {
                font-size: 0.85rem !important;
                padding: 0.5rem !important;
            }

            /* Multiselect dropdown */
            .stMultiSelect [role="listbox"] {
                max-height: 200px !important;
            }

            /* Charts should be taller on mobile for better readability */
            .plotly-graph-div {
                height: 350px !important;
                margin: 10px 0 !important;
            }

            /* Card adjustments */
            .f1-card {
                border-radius: 8px !important;
                padding: 12px !important;
                margin-bottom: 12px !important;
                border: 1px solid #27272a !important;
            }

            /* Expander styling */
            .streamlit-expanderHeader {
                font-size: 0.95rem !important;
            }

            /* Column layout: stacked on mobile */
            [data-testid="column"] {
                min-width: 100% !important;
            }

            /* Logo sizing */
            [data-testid="stImage"] img {
                max-width: 100% !important;
                height: auto !important;
            }

            /* Info/Error boxes */
            [role="alert"] {
                font-size: 0.9rem !important;
                padding: 0.75rem !important;
            }

            /* Sidebar text sizing */
            [data-testid="stSidebar"] button {
                font-size: 0.85rem !important;
            }

            [data-testid="stSidebar"] label {
                font-size: 0.85rem !important;
            }

            /* Monospace font sizes for mobile */
            .stCode, code, pre {
                font-size: 0.75rem !important;
            }

            /* Container max-width for readability */
            .main .block-container {
                max-width: 100% !important;
                padding: 0 !important;
            }
        }

        /* Very small phones (≤480px) */
        @media (max-width: 480px) {
            h1 { font-size: 1.5rem !important; }
            h2 { font-size: 1.2rem !important; }
            h3 { font-size: 1rem !important; }

            .plotly-graph-div { height: 300px !important; }

            .stButton > button {
                font-size: 0.8rem !important;
                padding: 0.4rem !important;
            }

            /* Tight spacing on small phones */
            .main { padding: 0.5rem !important; }

            .f1-card { padding: 8px !important; margin-bottom: 8px !important; }

            /* Reduce font sizes further */
            body, input, select, textarea, button {
                font-size: 13px !important;
            }
        }

        /* ============================================
           TOUCH-FRIENDLY ADJUSTMENTS
           ============================================ */

        @media (hover: none) and (pointer: coarse) {
            /* Touch devices - larger tap targets */
            button, a, .stButton > button {
                min-height: 44px !important;
                min-width: 44px !important;
            }

            /* Hover effects disabled on touch devices */
            button:hover {
                transform: none !important;
            }

            /* Improve label selectability */
            label {
                cursor: pointer !important;
                padding: 0.5rem !important;
            }
        }

        /* ============================================
           ORIENTATION FIXES
           ============================================ */

        @media (orientation: landscape) and (max-height: 500px) {
            /* Landscape mode adjustments */
            .plotly-graph-div { height: 250px !important; }

            [data-testid="stSidebar"] {
                width: 200px !important;
            }

            h1 { font-size: 1.5rem !important; }
        }
    </style>
    """
