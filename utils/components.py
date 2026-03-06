import base64
import os
import streamlit as st
from utils.i18n import t


def _get_logo_src() -> str:
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"


def plot_chart(fig, filename: str = "f1_chart", key: str = None, extra_config: dict = None) -> None:
    """
    Drop-in replacement for st.plotly_chart that:
    - enables the modebar with a PNG download button (camera icon)
    - stores the figure in session_state for bulk export
    - merges any caller-supplied config overrides via extra_config
    """
    config = {
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {
            "format": "png",
            "filename": filename,
            "height": 750,
            "width": 1400,
            "scale": 2,
        },
    }
    if extra_config:
        # Deep-merge: extra_config keys win over defaults
        for k, v in extra_config.items():
            if k == "toImageButtonOptions" and isinstance(v, dict):
                config["toImageButtonOptions"].update(v)
            else:
                config[k] = v

    kwargs = {"config": config, "width": "stretch"}
    if key is not None:
        kwargs["key"] = key

    st.plotly_chart(fig, **kwargs)

    # Store for bulk export (PDF / ZIP)
    if "_f1_charts" not in st.session_state:
        st.session_state["_f1_charts"] = {}
    st.session_state["_f1_charts"][filename] = fig



    return ""


def render_navbar(active_page: str = "landing") -> None:
    """Render the consistent top navigation bar for all non-dashboard pages."""
    # Ensure language state exists
    if "lang" not in st.session_state:
        st.session_state["lang"] = "EN"

    logo_src = _get_logo_src()

    # Inject navbar-specific CSS (only on pages that call this)
    st.markdown(
        """
    <style>
        /* NAVBAR CONTAINER */
        div[data-testid="stHorizontalBlock"]:first-of-type {
            background: rgba(17,17,19,0.75) !important;
            border: 1px solid #232326 !important;
            border-radius: 32px !important;
            padding: 18px 40px !important;
            width: 100% !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04) !important;
            backdrop-filter: blur(20px) !important;
        }
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:first-child,
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:first-child > div {
            display: flex !important; align-items: center !important;
            justify-content: flex-start !important; height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"] > div {
            display: flex !important; align-items: center !important; height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:first-of-type img {
            height: 52px !important; display: block !important;
            position: relative !important; top: -7.5px !important;
        }

        /* NAVBAR BUTTONS */
        html body div.stApp div[data-testid="stHorizontalBlock"]:first-of-type div.stButton > button {
            background: none !important; border: none !important; box-shadow: none !important;
            transform: none !important; padding: 0 !important; width: auto !important; min-height: 0 !important;
        }
        html body div.stApp div[data-testid="stHorizontalBlock"]:first-of-type div.stButton > button p {
            color: #71717a !important; font-family: 'Geist Mono', monospace !important;
            font-size: 0.78rem !important; text-transform: uppercase !important; letter-spacing: 1.8px !important;
            transition: color 0.3s ease, text-shadow 0.3s ease !important;
        }
        html body div.stApp div[data-testid="stHorizontalBlock"]:first-of-type div.stButton > button:hover p {
            color: #f4f4f5 !important;
            text-shadow: 0 0 14px rgba(255,255,255,0.35) !important;
        }

        /* NAVBAR ACTIVE ITEM */
        .nav-active-item {
            font-family: 'Geist Mono', monospace;
            font-size: 0.78rem;
            font-weight: 700;
            color: #21C55E;
            text-transform: uppercase;
            letter-spacing: 1.8px;
            position: relative;
            display: inline-block;
        }
        .nav-active-item::after {
            content: "";
            position: absolute;
            bottom: -5px;
            left: 0;
            right: 0;
            height: 1px;
            background: #21C55E;
            border-radius: 99px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    nav_items = [
        ("features",      t("nav_features")),
        ("architecture",  t("nav_architecture")),
        ("documentation", t("nav_documentation")),
    ]

    current_lang = st.session_state.get("lang", "EN")

    def _lang_selector(key: str) -> None:
        new = st.selectbox(
            "lang",
            options=["EN", "IT"],
            index=0 if current_lang == "EN" else 1,
            key=f"lang_sel_{key}",
            label_visibility="collapsed",
        )
        if new != current_lang:
            st.session_state["lang"] = new
            st.rerun()

    if active_page == "landing":
        cols = st.columns([6.8, 1.05, 1.35, 1.45, 1.15], vertical_alignment="center")
        with cols[0]:
            if logo_src:
                st.markdown(f'<img src="{logo_src}">', unsafe_allow_html=True)
        for i, (page_key, page_label) in enumerate(nav_items):
            with cols[i + 1]:
                if st.button(page_label, key=f"nav_landing_{page_key}"):
                    st.session_state["current_route"] = page_key
                    st.rerun()
        with cols[4]:
            _lang_selector("landing")
    else:
        cols = st.columns([5.1, 1.35, 1.05, 1.35, 1.45, 1.15], vertical_alignment="center")
        with cols[0]:
            if logo_src:
                st.markdown(f'<img src="{logo_src}">', unsafe_allow_html=True)
        with cols[1]:
            if st.button(t("nav_home"), key=f"nav_{active_page}_home"):
                st.session_state["current_route"] = "landing"
                st.rerun()
        for i, (page_key, page_label) in enumerate(nav_items):
            with cols[i + 2]:
                if page_key == active_page:
                    st.markdown(
                        f'<span class="nav-active-item">{page_label.upper()}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(page_label, key=f"nav_{active_page}_{page_key}"):
                        st.session_state["current_route"] = page_key
                        st.rerun()
        with cols[5]:
            _lang_selector(active_page)
