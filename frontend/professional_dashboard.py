"""
Professional AI Packaging Reliability Risk Prediction Dashboard
Based on Micron Research Implementation
Real-time semiconductor packaging monitoring with ML-powered risk assessment
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from frontend.utils.api_client import get_api_client
from data.mock.generator import MockDataGenerator
from data.mock.scenarios import SCENARIOS

# Page configuration
st.set_page_config(
    page_title="Packaging Reliability Risk Prediction",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS Styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .header-container {
        background: white;
        padding: 20px 40px;
        border-bottom: 3px solid #667eea;
        margin-bottom: 20px;
    }
    
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
    }
    
    .subtitle {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .risk-indicator {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .risk-good { background: #10b981; color: white; }
    .risk-warning { background: #f59e0b; color: white; }
    .risk-severe { background: #ef4444; color: white; }
    
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    
    .status-idle { background: #e5e7eb; color: #6b7280; }
    .status-running {
        background: #10b981;
        color: white;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .stButton>button {
        border-radius: 8px;
        height: 50px;
        font-weight: 600;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None
if 'data_history' not in st.session_state:
    st.session_state.data_history = []
if 'mock_generator' not in st.session_state:
    st.session_state.mock_generator = MockDataGenerator()
if 'api_client' not in st.session_state:
    st.session_state.api_client = get_api_client()
if 'show_data_panel' not in st.session_state:
    st.session_state.show_data_panel = True
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = "normal"


def main():
    """Main application"""
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="main-title">🔬 Packaging Reliability Risk Prediction System</div>
        <div class="subtitle">Real-time AI-powered semiconductor packaging quality monitoring | Micron Technology</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Control Panel
    render_control_panel()
    
    st.markdown("---")
    
    # Data Loading Panel (Collapsible)
    render_data_loading_panel()
    
    st.markdown("---")
    
    # Auto-generate data if monitoring is active
    if st.session_state.monitoring_active:
        generate_and_predict()
        time.sleep(2)  # Sampling rate
        st.rerun()
    
    # Main Dashboard
    render_risk_dashboard()
    
    # Process Parameters
    if st.session_state.current_data:
        st.markdown("---")
        render_process_parameters()
        
        st.markdown("---")
        render_trend_charts()


def render_control_panel():
    """Render main control panel"""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("### 🎛️ Monitoring Controls")
        status = "RUNNING" if st.session_state.monitoring_active else "IDLE"
        status_class = "status-running" if st.session_state.monitoring_active else "status-idle"
        st.markdown(f'<span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
    
    with col2:
        if not st.session_state.monitoring_active:
            if st.button("▶️ START PREDICTION", type="primary", use_container_width=True):
                st.session_state.monitoring_active = True
                st.rerun()
    
    with col3:
        if st.session_state.monitoring_active:
            if st.button("⏸️ STOP", use_container_width=True):
                st.session_state.monitoring_active = False
                st.rerun()
    
    with col4:
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.monitoring_active = False
            st.session_state.current_data = None
            st.session_state.prediction_result = None
            st.session_state.data_history = []
            st.rerun()


def render_data_loading_panel():
    """Render collapsible data loading panel"""
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### 📊 Data Configuration")
    with col2:
        if st.button("▼" if st.session_state.show_data_panel else "▶", key="toggle_panel"):
            st.session_state.show_data_panel = not st.session_state.show_data_panel
            st.rerun()
    
    if st.session_state.show_data_panel:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Data Source**")
            data_source = st.selectbox(
                "source",
                ["Mock Generator", "Live Sensor Feed", "Historical Data"],
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**Scenario**")
            scenario_options = ["normal"] + list(SCENARIOS.keys())
            st.session_state.selected_scenario = st.selectbox(
                "scenario",
                scenario_options,
                label_visibility="collapsed"
            )
        
        with col3:
            st.markdown("**Sampling Rate**")
            st.select_slider(
                "rate",
                options=[0.5, 1, 2, 3, 5],
                value=2,
                label_visibility="collapsed"
            )


def generate_and_predict():
    """Generate data and get prediction"""
    generator = st.session_state.mock_generator
    api_client = st.session_state.api_client
    
    # Generate data
    if st.session_state.selected_scenario != "normal":
        scenario_config = SCENARIOS.get(st.session_state.selected_scenario)
        data = generator.generate_single(scenario=scenario_config)
    else:
        data = generator.generate_single()
    
    data_dict = data.to_dict()
    st.session_state.current_data = data_dict
    
    # Get prediction
    result = api_client.predict(data_dict)
    
    if result.get('success'):
        st.session_state.prediction_result = result['prediction']
        st.session_state.data_history.append({
            'timestamp': datetime.now(),
            'status': result['prediction']['status'],
            'confidence': result['prediction']['confidence'],
            'data': data_dict
        })
        if len(st.session_state.data_history) > 50:
            st.session_state.data_history = st.session_state.data_history[-50:]


def render_risk_dashboard():
    """Render risk dashboard"""
    if st.session_state.prediction_result is None:
        st.info("👆 Click START PREDICTION to begin monitoring")
        return
    
    pred = st.session_state.prediction_result
    data = st.session_state.current_data
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = pred['status']
        confidence = pred['confidence']
        risk_class = {'GOOD': 'risk-good', 'WARNING': 'risk-warning', 'SEVERE': 'risk-severe'}.get(status, 'risk-good')
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">RISK STATUS</div>
            <div class="risk-indicator {risk_class}">{status}</div>
            <div style="font-size: 24px; font-weight: 700; margin-top: 12px;">{confidence*100:.1f}%</div>
            <div style="font-size: 12px; color: #6b7280;">Confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">BATCH ID</div>
            <div style="font-size: 20px; font-weight: 600;">{data.get('batch_id', 'N/A')}</div>
            <div style="font-size: 12px; color: #6b7280; margin-top: 12px;">Machine: {data.get('machine_id', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        defect_count = data.get('inspect_defect_count', 0)
        reliability = data.get('inspect_reliability_score', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">QUALITY METRICS</div>
            <div style="font-size: 24px; font-weight: 700;">{defect_count}</div>
            <div style="font-size: 12px; color: #6b7280;">Defects | Reliability: {reliability:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        history_count = len(st.session_state.data_history)
        severe_rate = 0
        if history_count > 0:
            severe_count = sum(1 for h in st.session_state.data_history if h['status'] == 'SEVERE')
            severe_rate = (severe_count / history_count) * 100
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">BATCH STATISTICS</div>
            <div style="font-size: 24px; font-weight: 700;">{history_count}</div>
            <div style="font-size: 12px; color: #6b7280;">Samples | Severe: {severe_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)


def render_process_parameters():
    """Render process parameters"""
    data = st.session_state.current_data
    st.markdown("### 🔧 Critical Process Parameters")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Die Attach", "Wire Bonding", "Molding", "Curing", "Inspection"])
    
    with tab1:
        cols = st.columns(4)
        cols[0].metric("Temperature", f"{data.get('die_temperature', 0):.1f}°C", "±2°C")
        cols[1].metric("Void %", f"{data.get('die_void_percentage', 0):.2f}%", "Target <3%")
        cols[2].metric("Placement", f"{data.get('die_placement_accuracy', 0):.1f}μm", "Target <10μm")
        cols[3].metric("Bond Line", f"{data.get('die_bond_line_thickness', 0):.1f}μm", "20-30μm")
    
    with tab2:
        cols = st.columns(4)
        cols[0].metric("Bond Force", f"{data.get('wire_bonding_force', 0):.1f}N", "35-55N")
        cols[1].metric("Ultrasonic", f"{data.get('wire_ultrasonic_power', 0):.1f}mW", "70-110mW")
        cols[2].metric("Loop Height", f"{data.get('wire_loop_height', 0):.1f}μm", "200-250μm")
        cols[3].metric("Pull Strength", f"{data.get('wire_pull_strength', 0):.1f}gf", ">8gf")
    
    with tab3:
        cols = st.columns(4)
        cols[0].metric("Mold Temp", f"{data.get('mold_temperature', 0):.1f}°C", "165-185°C")
        cols[1].metric("Pressure", f"{data.get('mold_pressure', 0):.1f}MPa", "5-9MPa")
        cols[2].metric("Fill Time", f"{data.get('mold_fill_time', 0):.1f}s", "3-5s")
        cols[3].metric("Voids", f"{data.get('mold_voids', 0):.2f}%", "Target <1%")
    
    with tab4:
        cols = st.columns(4)
        cols[0].metric("Cure Temp", f"{data.get('cure_temperature', 0):.1f}°C", "170-190°C")
        cols[1].metric("Cure Time", f"{data.get('cure_time', 0):.0f}min", "120-180min")
        cols[2].metric("Humidity", f"{data.get('cure_humidity', 0):.1f}%", "30-50%")
        cols[3].metric("Uniformity", f"{data.get('cure_uniformity', 0):.2f}°C", "Target <2°C")
    
    with tab5:
        cols = st.columns(4)
        cols[0].metric("Defects", f"{data.get('inspect_defect_count', 0)}", "Target 0")
        cols[1].metric("Visual Score", f"{data.get('inspect_visual_score', 0):.1f}", ">90")
        cols[2].metric("Electrical", "PASS" if data.get('inspect_electrical_test', 1) == 1 else "FAIL")
        cols[3].metric("Reliability", f"{data.get('inspect_reliability_score', 0):.1f}%", ">95%")


def render_trend_charts():
    """Render trend charts"""
    if len(st.session_state.data_history) < 2:
        return
    
    st.markdown("### 📈 Real-Time Trends")
    
    # Prepare data
    df = pd.DataFrame([
        {
            'timestamp': h['timestamp'],
            'status': h['status'],
            'confidence': h['confidence']
        }
        for h in st.session_state.data_history
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Confidence trend
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['confidence'] * 100,
            mode='lines+markers',
            name='Confidence',
            line=dict(color='#667eea', width=2)
        ))
        fig.update_layout(
            title="Prediction Confidence Over Time",
            xaxis_title="Time",
            yaxis_title="Confidence (%)",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Status distribution
        status_counts = df['status'].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            marker=dict(colors=['#10b981', '#f59e0b', '#ef4444'])
        )])
        fig.update_layout(title="Status Distribution", height=300)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

# Made with Bob
