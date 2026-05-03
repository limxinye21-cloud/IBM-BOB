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
    # Status colors and icons
    status_config = {
        "GOOD": {
            "color": "#28a745",
            "bg_color": "#d4edda",
            "icon": "✓",
            "text": "GOOD",
            "description": "All systems operating normally"
        },
        "WARNING": {
            "color": "#ffc107",
            "bg_color": "#fff3cd",
            "icon": "⚠",
            "text": "WARNING",
            "description": "Attention required - parameters outside normal range"
        },
        "SEVERE": {
            "color": "#dc3545",
            "bg_color": "#f8d7da",
            "icon": "✗",
            "text": "SEVERE",
            "description": "Critical issue detected - immediate action required"
        },
        "UNKNOWN": {
            "color": "#6c757d",
            "bg_color": "#e2e3e5",
            "icon": "?",
            "text": "UNKNOWN",
            "description": "Status unavailable"
        }
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
    
    # Get configuration
    config = status_config.get(status.upper(), status_config["UNKNOWN"])
    sizes = size_config.get(size, size_config["large"])
    
    # Render status light
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 20px;
            background-color: {config['bg_color']};
            border-radius: 15px;
            border: 3px solid {config['color']};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            gap: 20px;
        ">
            <!-- Status Light Circle -->
            <div style="
                width: {sizes['light_size']};
                height: {sizes['light_size']};
                background-color: {config['color']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: {sizes['icon_size']};
                color: white;
                font-weight: bold;
                box-shadow: 0 0 20px {config['color']};
                animation: pulse 2s infinite;
                flex-shrink: 0;
            ">
                {config['icon']}
            </div>
            
            <!-- Status Information in Columns -->
            <div style="
                display: flex;
                flex-direction: column;
                gap: 8px;
                flex: 1;
            ">
                <!-- Status Text -->
                <div style="
                    font-size: {sizes['font_size']};
                    font-weight: bold;
                    color: {config['color']};
                ">
                    {config['text']}
                </div>
                
                <!-- Confidence Score -->
                {f'''
                <div style="
                    font-size: 14px;
                    color: #666;
                    font-weight: 500;
                ">
                    <span style="color: #333;">Confidence:</span> {confidence:.1%}
                </div>
                ''' if confidence is not None else ''}
                
                <!-- Description -->
                <div style="
                    font-size: 12px;
                    color: #666;
                    line-height: 1.4;
                ">
                    {config['description']}
                </div>
            </div>
        </div>
        
        <style>
            @keyframes pulse {{
                0% {{
                    box-shadow: 0 0 20px {config['color']};
                }}
                50% {{
                    box-shadow: 0 0 40px {config['color']};
                }}
                100% {{
                    box-shadow: 0 0 20px {config['color']};
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_status_badge(status: str, confidence: Optional[float] = None) -> None:
    """
    Render compact status badge
    
    Args:
        status: Status (GOOD, WARNING, SEVERE)
        confidence: Confidence score (0-1)
    """
    status_config = {
        "GOOD": {"color": "#28a745", "icon": "✓"},
        "WARNING": {"color": "#ffc107", "icon": "⚠"},
        "SEVERE": {"color": "#dc3545", "icon": "✗"},
        "UNKNOWN": {"color": "#6c757d", "icon": "?"}
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
            "GOOD": {"color": "#28a745", "icon": "✓"},
            "WARNING": {"color": "#ffc107", "icon": "⚠"},
            "SEVERE": {"color": "#dc3545", "icon": "✗"}
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
