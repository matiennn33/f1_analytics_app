"""
Empty state and loading state UI components for better UX.
Provides styled cards for when data is unavailable or still loading.
"""
from __future__ import annotations

import streamlit as st
from config import COLORS, FONTS


def empty_state(
    icon: str = "fa-inbox",
    title: str = "No Data Available",
    message: str = "Select a session to get started",
    action_text: str = None,
    action_callback = None,
) -> None:
    """
    Display a styled empty state card.

    Args:
        icon: Font Awesome icon class
        title: Main heading
        message: Descriptive message
        action_text: Optional action button text
        action_callback: Callback function for action button
    """
    st.markdown(
        f"""
        <div style="
            background: {COLORS['bg_card']};
            border: 1px dashed {COLORS['border']};
            border-radius: 12px;
            padding: 60px 30px;
            text-align: center;
            margin: 40px auto;
        ">
            <i class="fa-solid {icon}" style="
                font-size: 3rem;
                color: {COLORS['accent_green']};
                opacity: 0.5;
                margin-bottom: 20px;
                display: block;
            "></i>
            <h3 style="
                color: {COLORS['text_white']};
                font-family: {FONTS['mono']};
                margin: 15px 0;
                font-size: 1.3rem;
            ">{title}</h3>
            <p style="
                color: {COLORS['text_muted']};
                font-family: {FONTS['sans']};
                margin: 0;
                max-width: 400px;
                margin-left: auto;
                margin-right: auto;
            ">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if action_text and action_callback:
        if st.button(action_text, use_container_width=True):
            action_callback()


def loading_state(
    message: str = "Processing your request...",
    subtext: str = None,
) -> None:
    """
    Display a styled loading state card.

    Args:
        message: Main loading message
        subtext: Optional additional information
    """
    st.markdown(
        f"""
        <div style="
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 40px 30px;
            text-align: center;
            margin: 40px auto;
        ">
            <div style="
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 3px solid {COLORS['border']};
                border-top-color: {COLORS['accent_green']};
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin-bottom: 20px;
            "></div>
            <h3 style="
                color: {COLORS['text_white']};
                font-family: {FONTS['mono']};
                margin: 15px 0;
            ">{message}</h3>
            {'<p style="color: ' + COLORS['text_muted'] + '; font-family: ' + FONTS['sans'] + '; margin: 0;">' + subtext + '</p>' if subtext else ''}
            <style>
                @keyframes spin {{
                    to {{ transform: rotate(360deg); }}
                }}
            </style>
        </div>
        """,
        unsafe_allow_html=True,
    )


def error_state(
    icon: str = "fa-circle-exclamation",
    title: str = "Something Went Wrong",
    message: str = "An error occurred while processing your request",
    error_details: str = None,
) -> None:
    """
    Display a styled error state card.

    Args:
        icon: Font Awesome icon class
        title: Error title
        message: Error description
        error_details: Optional technical details (expandable)
    """
    st.markdown(
        f"""
        <div style="
            background: {COLORS['bg_card']};
            border: 2px solid #ef4444;
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
        ">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <i class="fa-solid {icon}" style="
                    font-size: 1.5rem;
                    color: #ef4444;
                "></i>
                <h3 style="
                    color: {COLORS['text_white']};
                    font-family: {FONTS['mono']};
                    margin: 0;
                ">{title}</h3>
            </div>
            <p style="
                color: {COLORS['text_muted']};
                font-family: {FONTS['sans']};
                margin: 0;
            ">{message}</p>
            {'<p style="color: #a1a1aa; font-family: monospace; font-size: 0.85rem; margin-top: 10px; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px;">' + str(error_details) + '</p>' if error_details else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def no_data_chart(reason: str = "No data available for this selection") -> None:
    """
    Display styled message for charts with no data.

    Args:
        reason: Explanation of why no data is available
    """
    st.markdown(
        f"""
        <div style="
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        ">
            <i class="fa-solid fa-chart-line" style="
                font-size: 2rem;
                color: {COLORS['text_muted']};
                opacity: 0.4;
                margin-bottom: 15px;
            "></i>
            <p style="
                color: {COLORS['text_muted']};
                font-family: {FONTS['sans']};
                margin: 0;
            ">{reason}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
