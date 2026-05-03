"""
AI Packaging Reliability Copilot - Main Dashboard
Real-time semiconductor packaging monitoring and AI copilot system
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from frontend.utils.api_client import get_api_client
from frontend.components.status_light import render_status_light, render_status_badge, render_status_timeline
from frontend.components.charts import (
    render_parameter_gauge,
    render_time_series,
    render_status_distribution,
    render_confidence_histogram,
    render_feature_importance,
    render_multi_parameter_chart,
    render_process_stage_summary
)
from frontend.components.chat_copilot import (
    render_chat_interface,
    render_quick_actions,
    render_copilot_stats
)
from frontend.components.alerts_panel import (
    render_alerts_panel,
    render_alert_statistics,
    render_alert_history
)
from data.mock.generator import MockDataGenerator
from data.mock.scenarios import SCENARIOS


# Page configuration
st.set_page_config(
    page_title="AI Packaging Reliability Copilot",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'api_client' not in st.session_state:
    st.session_state.api_client = get_api_client()

if 'mock_generator' not in st.session_state:
    st.session_state.mock_generator = MockDataGenerator()

if 'current_data' not in st.session_state:
    st.session_state.current_data = None

if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<div class="main-header">🔬 AI Packaging Reliability Copilot</div>', unsafe_allow_html=True)
    st.markdown("**Powered by IBM Bob** | Real-time Semiconductor Packaging Monitoring & AI Analysis")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=IBM+Bob", width=200)
        st.markdown("---")
        
        # API Status
        st.subheader("🔌 System Status")
        api_client = st.session_state.api_client
        
        if api_client.is_connected():
            st.success("✓ Backend Connected")
            
            # ML Status
            ml_status = api_client.get_ml_status()
            if ml_status.get('status') == 'loaded':
                st.success("✓ ML Model Loaded")
                model_info = ml_status.get('model_info', {})
                if model_info:
                    st.caption(f"Accuracy: {model_info.get('test_accuracy', 0):.2%}")
            else:
                st.warning("⚠ ML Model Not Available")
                st.caption("Using rule-based classification")
        else:
            st.error("✗ Backend Disconnected")
            st.caption("Start backend: `python backend/app/main.py`")
        
        st.markdown("---")
        
        # Data Source Selection
        st.subheader("📊 Data Source")
        data_source = st.radio(
            "Select source:",
            ["Mock Generator", "Manual Input", "Live API"],
            help="Choose how to generate process data"
        )
        
        # Scenario Selection (for mock generator)
        if data_source == "Mock Generator":
            st.subheader("🎭 Scenario")
            scenario_names = ["Normal"] + list(SCENARIOS.keys())
            selected_scenario = st.selectbox(
                "Select scenario:",
                scenario_names,
                help="Choose a predefined scenario"
            )
        
        st.markdown("---")
        
        # Auto-refresh
        st.subheader("🔄 Auto-Refresh")
        auto_refresh = st.checkbox("Enable auto-refresh", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
        
        if auto_refresh:
            refresh_interval = st.slider("Interval (seconds)", 1, 10, 3)
        
        st.markdown("---")
        
        # Actions
        st.subheader("⚡ Actions")
        
        if st.button("🔄 Generate New Data"):
            generate_new_data(data_source, selected_scenario if data_source == "Mock Generator" else None)
        
        if st.button("📈 Get Prediction"):
            if st.session_state.current_data:
                get_prediction()
            else:
                st.warning("Generate data first")
        
        if st.button("🧹 Clear History"):
            st.session_state.prediction_history = []
            st.success("History cleared")
    
    # Main content
    if st.session_state.current_data is None:
        st.info("👈 Generate data from the sidebar to begin monitoring")
        
        # Show welcome message
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🎯 Real-Time Monitoring")
            st.write("Track 33 process parameters across 5 packaging stages")
        with col2:
            st.markdown("### 🤖 AI Classification")
            st.write("ML-powered status prediction with explainability")
        with col3:
            st.markdown("### 💡 Intelligent Insights")
            st.write("Feature importance and critical parameter analysis")
        
        return
    
    # Display current data and prediction
    display_dashboard()
    
    # Auto-refresh
    if st.session_state.auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


def generate_new_data(source: str, scenario: str = None):
    """Generate new process data"""
    
    if source == "Mock Generator":
        generator = st.session_state.mock_generator
        
        if scenario and scenario != "Normal":
            scenario_config = SCENARIOS.get(scenario)
            data = generator.generate_single(scenario=scenario_config)
        else:
            data = generator.generate_single()
        
        # Convert ProcessData object to dictionary
        st.session_state.current_data = data.to_dict()
        st.success(f"✓ Generated data with scenario: {scenario}")
    
    elif source == "Manual Input":
        st.info("Manual input mode - use the input panel below")
    
    elif source == "Live API":
        api_client = st.session_state.api_client
        result = api_client.get_latest_data(limit=1)
        
        if result.get('success') and result.get('data'):
            st.session_state.current_data = result['data'][0]
            st.success("✓ Fetched latest data from API")
        else:
            st.error("Failed to fetch data from API")


def get_prediction():
    """Get ML prediction for current data"""
    
    if not st.session_state.current_data:
        st.warning("No data available")
        return
    
    api_client = st.session_state.api_client
    data = st.session_state.current_data
    
    # Get prediction
    result = api_client.predict(data)
    
    if result.get('success'):
        prediction = result['prediction']
        
        # Store in history
        st.session_state.prediction_history.append({
            'timestamp': prediction['timestamp'],
            'predicted_status': prediction['status'],
            'confidence': prediction['confidence'],
            'probabilities': prediction['probabilities']
        })
        
        # Update current data with prediction
        st.session_state.current_data['predicted_status'] = prediction['status']
        st.session_state.current_data['confidence'] = prediction['confidence']
        
        st.success(f"✓ Prediction: {prediction['status']} ({prediction['confidence']:.1%} confidence)")
    else:
        st.error("Prediction failed")


def display_dashboard():
    """Display main dashboard content"""
    
    data = st.session_state.current_data
    api_client = st.session_state.api_client
    
    # Top section: Status and Key Metrics with Alerts
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("### 🚦 Current Status")
        status = data.get('predicted_status', data.get('status', 'UNKNOWN'))
        confidence = data.get('confidence')
        render_status_light(status, confidence, size="large")
    
    with col2:
        st.markdown("### 📊 Key Metrics")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric(
                "Batch ID",
                data.get('batch_id', 'N/A')[:8] + "..."
            )
        
        with metric_col2:
            st.metric(
                "Reliability Score",
                f"{data.get('inspect_reliability_score', 0):.1f}",
                delta=None
            )
        
        with metric_col3:
            st.metric(
                "Defect Count",
                int(data.get('inspect_defect_count', 0))
            )
        
        with metric_col4:
            st.metric(
                "Void %",
                f"{data.get('die_void_percentage', 0):.1f}%"
            )
    
    st.markdown("---")
    
    # Process Stage Summary
    st.markdown("### 🏭 Process Stage Overview")
    render_process_stage_summary(data)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Real-Time Parameters",
        "🤖 ML Analysis",
        "💬 AI Copilot",
        "🚨 Alerts",
        "📊 Historical Trends",
        "⚙️ Manual Input",
        "📋 Data Details"
    ])
    
    with tab1:
        display_realtime_parameters(data)
    
    with tab2:
        display_ml_analysis(data)
    
    with tab3:
        display_copilot_chat(data)
    
    with tab4:
        display_alerts_tab()
    
    with tab5:
        display_historical_trends()
    
    with tab6:
        display_manual_input()
    
    with tab7:
        display_data_details(data)


def display_realtime_parameters(data: dict):
    """Display real-time parameter gauges"""
    
    st.markdown("#### Die Attach Stage")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_parameter_gauge(
            "Temperature",
            data.get('die_temperature', 0),
            170, 200, 190, 195, "°C"
        )
    
    with col2:
        render_parameter_gauge(
            "Void %",
            data.get('die_void_percentage', 0),
            0, 10, 3, 5, "%"
        )
    
    with col3:
        render_parameter_gauge(
            "Placement Accuracy",
            data.get('die_placement_accuracy', 0),
            0, 20, 10, 15, "μm"
        )
    
    st.markdown("#### Wire Bonding Stage")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_parameter_gauge(
            "Bonding Force",
            data.get('wire_bonding_force', 0),
            30, 60, 50, 55, "gf"
        )
    
    with col2:
        render_parameter_gauge(
            "Pull Strength",
            data.get('wire_pull_strength', 0),
            5, 15, 8, 6, "gf"
        )
    
    with col3:
        render_parameter_gauge(
            "Loop Height",
            data.get('wire_loop_height', 0),
            180, 280, 240, 260, "μm"
        )
    
    st.markdown("#### Molding & Curing")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_parameter_gauge(
            "Mold Temperature",
            data.get('mold_temperature', 0),
            165, 185, 180, 183, "°C"
        )
    
    with col2:
        render_parameter_gauge(
            "Cure Uniformity",
            data.get('cure_uniformity', 0),
            1, 3, 2, 2.5, "°C"
        )
    
    with col3:
        render_parameter_gauge(
            "Mold Voids",
            data.get('mold_voids', 0),
            0, 5, 1, 2, "%"
        )


def display_ml_analysis(data: dict):
    """Display ML analysis and explainability"""
    
    api_client = st.session_state.api_client
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Prediction Probabilities")
        
        if 'predicted_status' in data:
            probabilities = data.get('probabilities', {
                'GOOD': 0.33,
                'WARNING': 0.33,
                'SEVERE': 0.34
            })
            
            for status, prob in probabilities.items():
                st.progress(prob, text=f"{status}: {prob:.1%}")
        else:
            st.info("Get prediction to see probabilities")
    
    with col2:
        st.markdown("#### 📊 Status History")
        if st.session_state.prediction_history:
            render_status_distribution(st.session_state.prediction_history)
        else:
            st.info("No prediction history yet")
    
    st.markdown("---")
    
    # Feature Importance
    st.markdown("#### 🔍 Feature Importance Analysis")
    
    if st.button("🧠 Explain Prediction"):
        with st.spinner("Analyzing..."):
            result = api_client.explain_prediction(data, top_n=10)
            
            if result.get('success'):
                explanation = result['explanation']
                contributors = explanation.get('top_contributors', [])
                
                if contributors:
                    render_feature_importance(contributors, top_n=10)
                    
                    st.markdown("#### ⚠️ Critical Parameters")
                    critical_result = api_client.get_critical_parameters(data, threshold=0.05)
                    
                    if critical_result.get('success'):
                        critical_params = critical_result['critical_parameters']
                        
                        if critical_params:
                            for param in critical_params[:5]:
                                importance_pct = param['importance'] * 100
                                st.markdown(
                                    f"- **{param['parameter']}**: {param['value']:.2f} "
                                    f"(Importance: {importance_pct:.1f}%)"
                                )
                        else:
                            st.info("No critical parameters identified")
                else:
                    st.warning("No feature importance data available")
            else:
                st.error("Failed to get explanation")


def display_historical_trends():
    """Display historical trends"""
    
    st.markdown("#### 📈 Prediction Timeline")
    
    if st.session_state.prediction_history:
        render_status_timeline(st.session_state.prediction_history)
        
        st.markdown("---")
        
        # Confidence histogram
        st.markdown("#### 📊 Confidence Distribution")
        render_confidence_histogram(st.session_state.prediction_history)
    else:
        st.info("No historical data available. Generate predictions to see trends.")


def display_manual_input():
    """Display manual input form"""
    
    st.markdown("#### ✏️ Manual Data Entry")
    st.info("Enter process parameters manually for testing")
    
    with st.form("manual_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Die Attach**")
            die_temp = st.number_input("Temperature (°C)", 170.0, 200.0, 185.0)
            die_void = st.number_input("Void %", 0.0, 10.0, 2.0)
            die_placement = st.number_input("Placement Accuracy (μm)", 0.0, 20.0, 8.0)
            
            st.markdown("**Wire Bonding**")
            wire_force = st.number_input("Bonding Force (gf)", 30.0, 60.0, 45.0)
            wire_strength = st.number_input("Pull Strength (gf)", 5.0, 15.0, 10.0)
            wire_loop = st.number_input("Loop Height (μm)", 180.0, 280.0, 225.0)
        
        with col2:
            st.markdown("**Molding**")
            mold_temp = st.number_input("Temperature (°C)", 165.0, 185.0, 175.0)
            mold_voids = st.number_input("Voids %", 0.0, 5.0, 0.5)
            
            st.markdown("**Curing**")
            cure_temp = st.number_input("Temperature (°C)", 175.0, 190.0, 180.0)
            cure_uniformity = st.number_input("Uniformity (°C)", 1.0, 3.0, 1.5)
            
            st.markdown("**Inspection**")
            reliability = st.number_input("Reliability Score", 80.0, 100.0, 97.0)
            defects = st.number_input("Defect Count", 0, 5, 0)
        
        submitted = st.form_submit_button("Submit Data")
        
        if submitted:
            # Create data dictionary with all required parameters
            manual_data = {
                'batch_id': f"MANUAL_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'machine_id': 'MANUAL_INPUT',
                'die_temperature': die_temp,
                'die_void_percentage': die_void,
                'die_placement_accuracy': die_placement,
                'wire_bonding_force': wire_force,
                'wire_pull_strength': wire_strength,
                'wire_loop_height': wire_loop,
                'mold_temperature': mold_temp,
                'mold_voids': mold_voids,
                'cure_temperature': cure_temp,
                'cure_uniformity': cure_uniformity,
                'inspect_reliability_score': reliability,
                'inspect_defect_count': defects,
                # Add default values for other required parameters
                'die_epoxy_temperature': die_temp - 30,
                'die_bond_line_thickness': 25.0,
                'die_cure_time': 75.0,
                'die_pressure': 0.8,
                'wire_ultrasonic_power': 90.0,
                'wire_bonding_temperature': 165.0,
                'wire_diameter': 25.0,
                'wire_bond_time': 20.0,
                'mold_pressure': 7.0,
                'mold_fill_time': 4.0,
                'mold_compound_viscosity': 125.0,
                'mold_transfer_speed': 12.5,
                'mold_clamp_force': 60.0,
                'cure_time': 150.0,
                'cure_humidity': 40.0,
                'cure_thermal_profile': 3.0,
                'cure_oxygen_level': 0.5,
                'inspect_visual_score': reliability - 2,
                'inspect_electrical_test': 1 if defects == 0 else 0,
                'inspect_dimensional_accuracy': 15.0,
                'inspect_lead_coplanarity': 40.0,
                'status': 'UNKNOWN'
            }
            
            st.session_state.current_data = manual_data
            st.success("✓ Manual data submitted")
            st.rerun()


def display_data_details(data: dict):
    """Display detailed data view"""
    
    st.markdown("#### 📋 Complete Process Data")
    
    # Convert to DataFrame for better display
    df = pd.DataFrame([data]).T
    df.columns = ['Value']
    
    st.dataframe(df, use_container_width=True, height=600)
    
    # Download button
    csv = df.to_csv()
    st.download_button(
        label="📥 Download Data (CSV)",
        data=csv,
        file_name=f"process_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def display_copilot_chat(data: dict):
    """Display AI copilot chat interface"""
    
    api_client = st.session_state.api_client
    
    # Chat interface
    render_chat_interface(api_client, data)
    
    st.markdown("---")
    
    # Quick actions
    render_quick_actions(api_client, data)
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📊 Copilot Statistics")
    render_copilot_stats(api_client)


def display_alerts_tab():
    """Display alerts management tab"""
    
    api_client = st.session_state.api_client
    
    # Alert panel
    render_alerts_panel(api_client)
    
    st.markdown("---")
    
    # Alert statistics
    col1, col2 = st.columns(2)
    
    with col1:
        render_alert_statistics(api_client, hours=24)
    
    with col2:
        render_alert_history(api_client, hours=24)
    
    st.markdown("---")
    
    # Manual alert check
    st.markdown("### 🔍 Manual Alert Check")
    
    if st.button("Check for Alerts Now"):
        data = st.session_state.current_data
        if data:
            result = api_client._post("/alerts/check", data)
            
            if result.get('success'):
                alerts_triggered = result.get('alerts_triggered', [])
                
                if alerts_triggered:
                    st.warning(f"⚠️ {len(alerts_triggered)} alert(s) triggered!")
                    for alert in alerts_triggered:
                        st.error(f"🔴 {alert['title']}")
                else:
                    st.success("✓ No alerts triggered - System operating normally")
            else:
                st.error("Failed to check alerts")
        else:
            st.warning("No data available - Generate data first")


if __name__ == "__main__":
    main()

# Made with Bob

