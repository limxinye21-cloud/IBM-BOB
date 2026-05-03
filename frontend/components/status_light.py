"""
Status Light Component for AI Packaging Reliability Copilot Dashboard
"""

import streamlit as st
from typing import Optional


def render_status_light(
    status: str,
    confidence: Optional[float] = None,
    size: str = "large"
) -> None:
    """
    Render status indicator light
    
    Args:
        status: Status (GOOD, WARNING, SEVERE)
        confidence: Confidence score (0-1)
        size: Size (small, medium, large)
    """
    status_config = {
        "GOOD": {
            "color": "#42be65",
            "bg_color": "rgba(66,190,101,0.08)",
            "glow": "rgba(66,190,101,0.5)",
            "icon": "✓",
            "text": "GOOD",
            "description": "All systems operating normally",
            "anim": "pulse-good",
        },
        "WARNING": {
            "color": "#f1c21b",
            "bg_color": "rgba(241,194,27,0.08)",
            "glow": "rgba(241,194,27,0.5)",
            "icon": "⚠",
            "text": "WARNING",
            "description": "Attention required — parameters outside normal range",
            "anim": "pulse-warning",
        },
        "SEVERE": {
            "color": "#fa4d56",
            "bg_color": "rgba(250,77,86,0.08)",
            "glow": "rgba(250,77,86,0.5)",
            "icon": "✗",
            "text": "SEVERE",
            "description": "Critical issue detected — immediate action required",
            "anim": "pulse-severe",
        },
        "UNKNOWN": {
            "color": "#8aa3cc",
            "bg_color": "rgba(138,163,204,0.08)",
            "glow": "rgba(138,163,204,0.3)",
            "icon": "?",
            "text": "UNKNOWN",
            "description": "Status unavailable",
            "anim": "pulse-good",
        },
    }
    
    # Size configurations
    size_config = {
        "small": {
            "light_size": "40px",
            "font_size": "14px",
            "icon_size": "20px"
        },
        "medium": {
            "light_size": "60px",
            "font_size": "18px",
            "icon_size": "30px"
        },
        "large": {
            "light_size": "100px",
            "font_size": "24px",
            "icon_size": "50px"
        }
    }
    
    config = status_config.get(status.upper(), status_config["UNKNOWN"])
    sizes = size_config.get(size, size_config["large"])
    anim = config["anim"]
    conf_html = (
        f'<div style="font-size:13px;color:{config["color"]};font-weight:600;margin-top:3px;">'
        f'Confidence: {confidence:.1%}</div>'
    ) if confidence is not None else ""

    st.markdown(f"""
        <style>
        @keyframes pulse-good    {{ 0%,100%{{box-shadow:0 0 16px #42be6580;}} 50%{{box-shadow:0 0 36px #42be65;}} }}
        @keyframes pulse-warning {{ 0%,100%{{box-shadow:0 0 16px #f1c21b80;}} 50%{{box-shadow:0 0 36px #f1c21b;}} }}
        @keyframes pulse-severe  {{
            0%,100%{{box-shadow:0 0 16px #fa4d5680;transform:scale(1);}}
            50%{{box-shadow:0 0 40px #fa4d56;transform:scale(1.04);}}
        }}
        </style>
        <div style="
            display:flex; align-items:center; padding:18px 22px;
            background:{config['bg_color']}; border-radius:14px;
            border:2px solid {config['color']}44; gap:18px;
            backdrop-filter:blur(6px);
        ">
            <div style="
                width:{sizes['light_size']}; height:{sizes['light_size']};
                background:radial-gradient(circle,{config['color']} 0%,{config['color']}bb 100%);
                border-radius:50%; display:flex; align-items:center; justify-content:center;
                font-size:{sizes['icon_size']}; color:white; font-weight:bold; flex-shrink:0;
                animation:{anim} {'1.2s' if status=='SEVERE' else '2s'} infinite;
            ">{config['icon']}</div>
            <div>
                <div style="font-size:{sizes['font_size']};font-weight:700;color:{config['color']};
                            letter-spacing:1px;">{config['text']}</div>
                {conf_html}
                <div style="font-size:11px;color:#697077;margin-top:5px;line-height:1.4;">
                    {config['description']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str, confidence: Optional[float] = None) -> None:
    """
    Render compact status badge
    
    Args:
        status: Status (GOOD, WARNING, SEVERE)
        confidence: Confidence score (0-1)
    """
    status_config = {
        "GOOD":    {"color": "#42be65", "icon": "✓"},
        "WARNING": {"color": "#f1c21b", "icon": "⚠"},
        "SEVERE":  {"color": "#fa4d56", "icon": "✗"},
        "UNKNOWN": {"color": "#8aa3cc", "icon": "?"},
    }
    
    config = status_config.get(status.upper(), status_config["UNKNOWN"])
    
    confidence_text = f" ({confidence:.1%})" if confidence is not None else ""
    
    st.markdown(
        f"""
        <span style="
            display: inline-block;
            padding: 5px 15px;
            background-color: {config['color']};
            color: white;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin: 5px;
        ">
            {config['icon']} {status.upper()}{confidence_text}
        </span>
        """,
        unsafe_allow_html=True
    )


def render_status_timeline(predictions: list) -> None:
    """
    Render status timeline
    
    Args:
        predictions: List of predictions with timestamp and status
    """
    if not predictions:
        st.info("No prediction history available")
        return
    
    st.markdown("### Status Timeline")
    
    for pred in predictions[-10:]:  # Show last 10
        timestamp = pred.get('timestamp', 'Unknown')
        status = pred.get('predicted_status', 'UNKNOWN')
        confidence = pred.get('confidence')
        
        status_config = {
            "GOOD":    {"color": "#42be65", "icon": "✓"},
            "WARNING": {"color": "#f1c21b", "icon": "⚠"},
            "SEVERE":  {"color": "#fa4d56", "icon": "✗"},
        }
        
        config = status_config.get(status, {"color": "#6c757d", "icon": "?"})
        
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                padding: 10px;
                margin: 5px 0;
                background-color: #f8f9fa;
                border-left: 4px solid {config['color']};
                border-radius: 5px;
            ">
                <span style="
                    font-size: 20px;
                    margin-right: 10px;
                    color: {config['color']};
                ">
                    {config['icon']}
                </span>
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: {config['color']};">
                        {status}
                    </div>
                    <div style="font-size: 12px; color: #666;">
                        {timestamp[:19] if len(timestamp) > 19 else timestamp}
                        {f" • Confidence: {confidence:.1%}" if confidence else ""}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    # Test status light
    st.set_page_config(page_title="Status Light Test", layout="wide")
    
    st.title("Status Light Component Test")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("GOOD Status")
        render_status_light("GOOD", confidence=0.95, size="large")
    
    with col2:
        st.subheader("WARNING Status")
        render_status_light("WARNING", confidence=0.78, size="large")
    
    with col3:
        st.subheader("SEVERE Status")
        render_status_light("SEVERE", confidence=0.92, size="large")
    
    st.markdown("---")
    
    st.subheader("Status Badges")
    render_status_badge("GOOD", 0.95)
    render_status_badge("WARNING", 0.78)
    render_status_badge("SEVERE", 0.92)
    
    st.markdown("---")
    
    st.subheader("Status Timeline")
    sample_predictions = [
        {"timestamp": "2024-01-15T10:00:00", "predicted_status": "GOOD", "confidence": 0.95},
        {"timestamp": "2024-01-15T10:05:00", "predicted_status": "GOOD", "confidence": 0.93},
        {"timestamp": "2024-01-15T10:10:00", "predicted_status": "WARNING", "confidence": 0.78},
        {"timestamp": "2024-01-15T10:15:00", "predicted_status": "SEVERE", "confidence": 0.92},
    ]
    render_status_timeline(sample_predictions)

# Made with Bob
