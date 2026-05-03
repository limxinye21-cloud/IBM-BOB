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
    render_process_stage_summary,
    render_stage_health_radar,
    render_parameter_deviation_heatmap,
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

# Custom CSS — IBM BOB Professional Light Theme
st.markdown("""
<style>
/* ── Global Light Background ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg,#f0f4ff 0%,#eef2fb 60%,#f4f7ff 100%);
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#eef3ff 0%,#e8eeff 100%);
    border-right: 1px solid #0f62fe33;
}
[data-testid="stSidebar"] * { color: #1a2238 !important; }

/* ── IBM Header Banner ── */
.ibm-header {
    background: linear-gradient(90deg,#0f62fe 0%,#0043ce 55%,#002d9c 100%);
    padding: 12px 24px; border-radius: 10px; color: white;
    margin-bottom: 12px;
    box-shadow: 0 4px 18px rgba(15,98,254,.25);
    display: flex; align-items: center; gap: 14px;
}
.ibm-header-text h1 { font-size:1.4rem; font-weight:700; margin:0; letter-spacing:-.3px; }
.ibm-header-text p  { margin:2px 0 0 0; opacity:.88; font-size:.8rem; }
.ibm-header-logo { font-size:2rem; }

/* ── KPI Hero Cards ── */
.kpi-row { display:flex; gap:8px; margin-bottom:10px; }
.kpi-card {
    flex:1; background:white;
    border:1px solid #dde6ff; border-radius:10px; padding:10px 8px;
    text-align:center; transition:all .25s;
    box-shadow:0 2px 8px rgba(15,98,254,.08);
}
.kpi-card:hover { border-color:#0f62fe66; transform:translateY(-1px); box-shadow:0 4px 14px rgba(15,98,254,.15); }
.kpi-value { font-size:1.4rem; font-weight:700; color:#0043ce; line-height:1.1; }
.kpi-value.good   { color:#198038; }
.kpi-value.warning{ color:#b45309; }
.kpi-value.severe { color:#da1e28; }
.kpi-value.blue   { color:#0043ce; }
.kpi-label { font-size:.65rem; color:#697077; text-transform:uppercase; letter-spacing:1px; margin-top:3px; }
.kpi-delta { font-size:.75rem; margin-top:2px; }

/* ── Process Flow ── */
.flow-wrap { display:flex; align-items:flex-start; gap:0; margin:6px 0 10px 0; }
.flow-card {
    flex:1; background:white;
    border:1px solid #dde6ff; border-top:3px solid #0f62fe;
    border-radius:8px; padding:8px 6px; text-align:center;
    position:relative; transition:all .2s; min-width:0;
    box-shadow:0 1px 6px rgba(15,98,254,.06);
}
.flow-card.good    { border-top-color:#198038; }
.flow-card.warning { border-top-color:#b45309; }
.flow-card.severe  { border-top-color:#da1e28; }
.flow-stage  { font-size:.6rem; color:#697077; text-transform:uppercase; letter-spacing:.8px; }
.flow-score  { font-size:1.3rem; font-weight:700; margin:2px 0 1px; }
.flow-score.good    { color:#198038; }
.flow-score.warning { color:#b45309; }
.flow-score.severe  { color:#da1e28; }
.flow-score.neutral { color:#0043ce; }
.flow-icon { font-size:1.1rem; }
.flow-arrow {
    display:flex; align-items:center; justify-content:center;
    color:#0f62fe88; font-size:1.2rem; padding:0 2px; padding-top:10px;
    flex-shrink:0;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:#e8eeff; border-radius:8px; padding:4px;
    border:1px solid #dde6ff; gap:2px;
}
.stTabs [data-baseweb="tab"]         { color:#4a5568; border-radius:6px; padding:8px 16px; }
.stTabs [aria-selected="true"]       { background:#0f62fe !important; color:white !important; }

/* ── Buttons ── */
.stButton > button {
    background:linear-gradient(135deg,#0f62fe,#0043ce) !important;
    color:white !important; border:none !important; border-radius:8px !important;
    padding:10px 20px !important; font-weight:600 !important; width:100% !important;
    transition:all .2s !important; box-shadow:0 2px 8px rgba(15,98,254,.25) !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,#0043ce,#002d9c) !important;
    box-shadow:0 4px 16px rgba(15,98,254,.4) !important;
    transform:translateY(-1px) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background:white; border:1px solid #dde6ff; border-radius:10px; padding:12px;
    box-shadow:0 1px 6px rgba(15,98,254,.08);
}
[data-testid="stMetricLabel"]  { color:#697077 !important; }
[data-testid="stMetricValue"]  { color:#1a2238 !important; font-weight:700 !important; }
[data-testid="stMetricDelta"]  { color:#198038 !important; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] { background:white; border-radius:8px; }

/* ── Alerts / info ── */
.stAlert { border-radius:10px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#eef2ff; }
::-webkit-scrollbar-thumb { background:#0f62fe66; border-radius:3px; }
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
    st.markdown("""
    <div class="ibm-header">
        <div class="ibm-header-logo">🔬</div>
        <div class="ibm-header-text">
            <h1>AI Packaging Reliability Copilot</h1>
            <p>Powered by IBM Bob &nbsp;·&nbsp; watsonx.ai &nbsp;·&nbsp; Real-time Semiconductor Packaging Monitoring</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Sidebar
    with st.sidebar:
        # IBM BOB Logo (inline SVG chip icon)
        st.markdown("""
        <div style="text-align:center;padding:10px 0 6px 0;">
          <svg width="188" height="76" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="ibmG" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#0f62fe"/>
                <stop offset="100%" style="stop-color:#002d9c"/>
              </linearGradient>
            </defs>
            <rect width="188" height="76" rx="11" fill="url(#ibmG)"/>
            <!-- chip body -->
            <rect x="10" y="18" width="42" height="40" rx="4" fill="none" stroke="rgba(255,255,255,.65)" stroke-width="2"/>
            <rect x="18" y="26" width="26" height="24" rx="2" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.45)" stroke-width="1.2"/>
            <!-- cross inside chip -->
            <line x1="31" y1="26" x2="31" y2="50" stroke="rgba(255,255,255,.3)" stroke-width="1"/>
            <line x1="18" y1="38" x2="44" y2="38" stroke="rgba(255,255,255,.3)" stroke-width="1"/>
            <!-- pins top -->
            <line x1="23" y1="18" x2="23" y2="11" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="31" y1="18" x2="31" y2="11" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="39" y1="18" x2="39" y2="11" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <!-- pins bottom -->
            <line x1="23" y1="58" x2="23" y2="65" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="31" y1="58" x2="31" y2="65" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="39" y1="58" x2="39" y2="65" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <!-- pins left -->
            <line x1="10" y1="29" x2="4" y2="29" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="10" y1="38" x2="4" y2="38" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="10" y1="47" x2="4" y2="47" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <!-- pins right -->
            <line x1="52" y1="29" x2="58" y2="29" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="52" y1="38" x2="58" y2="38" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <line x1="52" y1="47" x2="58" y2="47" stroke="rgba(255,255,255,.6)" stroke-width="1.8"/>
            <!-- text -->
            <text x="68" y="36" font-family="'IBM Plex Sans',Arial,sans-serif" font-size="21" font-weight="700" fill="white" letter-spacing="1">IBM BOB</text>
            <text x="69" y="54" font-family="'IBM Plex Sans',Arial,sans-serif" font-size="9.5" fill="rgba(255,255,255,.78)" letter-spacing=".5">AI Reliability Copilot</text>
          </svg>
        </div>
        """, unsafe_allow_html=True)

        # Sidebar title
        st.markdown("""
        <div style="text-align:center;color:#8aa3cc;font-size:.72rem;text-transform:uppercase;
             letter-spacing:2px;margin:-4px 0 10px 0;font-weight:600;">Control Panel Settings</div>
        """, unsafe_allow_html=True)
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
        
        if st.button("▶ Start"):
            generate_new_data(data_source, selected_scenario if data_source == "Mock Generator" else None)
        
        if st.button("📈 Get Prediction"):
            if st.session_state.current_data:
                get_prediction()
            else:
                st.warning("Generate data first")
        
        if st.button("🧹 Clear History"):
            st.session_state.prediction_history = []
            st.success("History cleared")
        
        st.markdown("---")
        
        # IBM Bob showcase section
        with st.expander("🤖 Built with IBM Bob", expanded=False):
            st.markdown("""
            <div style="font-size:.82rem;color:#1a2238;line-height:1.7;">
            <b style="color:#0043ce;">IBM Bob</b> was used as the intelligent
            development partner to build every layer of this system:
            <ul style="margin:6px 0 6px 16px;padding:0;">
              <li>🧠 ML ensemble pipeline &amp; feature engineering</li>
              <li>💬 NL Copilot service (8 query handlers)</li>
              <li>🎨 IBM light theme &amp; responsive UI</li>
              <li>🔧 FastAPI backend (20+ endpoints)</li>
              <li>🤖 3 custom Bob agents (debug, ml-trainer, explorer)</li>
              <li>📄 AGENTS.md &amp; project context files</li>
            </ul>
            <b>Sessions:</b> <code>bob_sessions/</code> (10 tasks logged)
            </div>
            """, unsafe_allow_html=True)
    
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
    
    # ── KPI Hero Bar ──
    status = data.get('predicted_status', data.get('status', 'UNKNOWN'))
    confidence = data.get('confidence')
    reliability = data.get('inspect_reliability_score', 0)
    defects = int(data.get('inspect_defect_count', 0))
    void_pct = data.get('die_void_percentage', 0)
    batch_id = data.get('batch_id', 'N/A')

    status_cls = status.lower() if status in ('GOOD','WARNING','SEVERE') else 'blue'
    status_icon = {'GOOD':'✅','WARNING':'⚠️','SEVERE':'🔴'}.get(status,'❓')
    conf_str = f"{confidence:.1%}" if confidence else "—"
    rel_cls = 'good' if reliability >= 95 else ('warning' if reliability >= 85 else 'severe')
    def_cls = 'good' if defects == 0 else ('warning' if defects <= 2 else 'severe')
    void_cls = 'good' if void_pct < 3 else ('warning' if void_pct < 5 else 'severe')

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-value {status_cls}">{status_icon} {status}</div>
            <div class="kpi-label">Process Status</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value blue">{conf_str}</div>
            <div class="kpi-label">ML Confidence</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value {rel_cls}">{reliability:.1f}</div>
            <div class="kpi-label">Reliability Score</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value {def_cls}">{defects}</div>
            <div class="kpi-label">Defect Count</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value {void_cls}">{void_pct:.1f}%</div>
            <div class="kpi-label">Die Void %</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value blue" style="font-size:1.1rem">{batch_id[:12]}</div>
            <div class="kpi-label">Batch ID</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Process Stage Flow ──
    st.markdown("#### 🏭 Process Stage Health")
    render_process_stage_summary(data)
    
    # Tabs for different views (no separator - keep compact)
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


def _compute_stage_scores(data: dict) -> dict:
    """Compute 0-100 health score per stage for radar chart."""
    STAGE_DEF = {
        "Die Attach":   [("die_temperature",175,195),("die_void_percentage",0,3),("die_placement_accuracy",0,10)],
        "Wire Bonding": [("wire_bonding_force",35,55),("wire_pull_strength",7,15),("wire_loop_height",190,250)],
        "Molding":      [("mold_temperature",168,182),("mold_pressure",5,10),("mold_voids",0,1)],
        "Curing":       [("cure_temperature",177,188),("cure_uniformity",1,2),("cure_time",120,180)],
        "Inspection":   [("inspect_reliability_score",90,100),("inspect_defect_count",0,0),("inspect_visual_score",90,100)],
    }
    scores = {}
    for stage, params in STAGE_DEF.items():
        sc = []
        for param, lo, hi in params:
            val = data.get(param)
            if val is None:
                continue
            rng = (hi - lo) if hi != lo else 1.0
            dev = max(0.0, lo - val) + max(0.0, val - hi)
            sc.append(max(0.0, 100.0 - (dev / rng) * 100))
        scores[stage] = round(sum(sc) / len(sc)) if sc else 50
    return scores


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
                color = '#198038' if status == 'GOOD' else ('#b45309' if status == 'WARNING' else '#da1e28')
                st.markdown(
                    f'<div style="margin:6px 0;">'
                    f'<div style="display:flex;justify-content:space-between;color:#1a2238;margin-bottom:2px;">'
                    f'<span style="font-weight:600">{status}</span><span style="color:{color};font-weight:700;">{prob:.1%}</span></div>'
                    f'<div style="background:#dde6ff;border-radius:4px;height:8px;">'
                    f'<div style="background:{color};width:{prob*100:.1f}%;height:8px;border-radius:4px;transition:width .4s"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Get prediction to see probabilities")
    
    with col2:
        st.markdown("#### 📊 Status History")
        if st.session_state.prediction_history:
            render_status_distribution(st.session_state.prediction_history)
        else:
            st.info("No prediction history yet")
    
    st.markdown("---")
    
    # Stage health radar + parameter deviation
    col_r, col_h = st.columns(2)
    with col_r:
        st.markdown("#### 📟 Stage Health Radar")
        stage_scores = _compute_stage_scores(data)
        render_stage_health_radar(stage_scores)
    with col_h:
        st.markdown("#### 🌡️ Parameter Deviations")
        render_parameter_deviation_heatmap(data)
    
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
    
    # Quick Fill buttons
    st.markdown("**Quick Fill Scenarios:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    if qc1.button("Normal", use_container_width=True):
        st.session_state['_qf'] = 'normal'
        st.rerun()
    if qc2.button("Wire Fail", use_container_width=True):
        st.session_state['_qf'] = 'wire_fail'
        st.rerun()
    if qc3.button("Die Void", use_container_width=True):
        st.session_state['_qf'] = 'die_void'
        st.rerun()
    if qc4.button("Mold Issue", use_container_width=True):
        st.session_state['_qf'] = 'mold_issue'
        st.rerun()
    
    # Quick Fill presets
    _QF_PRESETS = {
        'normal':    dict(die_temp=185.0, die_void=1.5, die_placement=5.0, wire_force=46.0, wire_strength=10.0, wire_loop=225.0, mold_temp=175.0, mold_pressure=7.0, mold_voids=0.3, cure_temp=181.0, cure_uniformity=1.2, reliability=97.0, defects=0),
        'wire_fail': dict(die_temp=185.0, die_void=2.0, die_placement=6.0, wire_force=30.0, wire_strength=4.5, wire_loop=270.0, mold_temp=175.0, mold_pressure=7.0, mold_voids=0.3, cure_temp=181.0, cure_uniformity=1.2, reliability=82.0, defects=3),
        'die_void':  dict(die_temp=197.0, die_void=8.5, die_placement=14.0, wire_force=46.0, wire_strength=10.0, wire_loop=225.0, mold_temp=175.0, mold_pressure=7.0, mold_voids=0.3, cure_temp=181.0, cure_uniformity=1.2, reliability=78.0, defects=2),
        'mold_issue':dict(die_temp=185.0, die_void=1.5, die_placement=5.0, wire_force=46.0, wire_strength=10.0, wire_loop=225.0, mold_temp=187.0, mold_pressure=9.5, mold_voids=2.8, cure_temp=181.0, cure_uniformity=1.2, reliability=80.0, defects=4),
    }
    qf = st.session_state.get('_qf', 'normal')
    P = _QF_PRESETS.get(qf, _QF_PRESETS['normal'])
    
    with st.form("manual_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Die Attach**")
            die_temp = st.number_input("Temperature (°C)", 170.0, 200.0, float(P['die_temp']))
            die_void = st.number_input("Void %", 0.0, 10.0, float(P['die_void']))
            die_placement = st.number_input("Placement Accuracy (μm)", 0.0, 20.0, float(P['die_placement']))
            
            st.markdown("**Wire Bonding**")
            wire_force = st.number_input("Bonding Force (gf)", 30.0, 60.0, float(P['wire_force']))
            wire_strength = st.number_input("Pull Strength (gf)", 5.0, 15.0, float(P['wire_strength']))
            wire_loop = st.number_input("Loop Height (μm)", 180.0, 280.0, float(P['wire_loop']))
        
        with col2:
            st.markdown("**Molding**")
            mold_temp = st.number_input("Temperature (°C)", 165.0, 185.0, float(P['mold_temp']))
            mold_pressure = st.number_input("Pressure (MPa)", 5.0, 12.0, float(P['mold_pressure']))
            mold_voids = st.number_input("Voids %", 0.0, 5.0, float(P['mold_voids']))
            
            st.markdown("**Curing**")
            cure_temp = st.number_input("Temperature (°C)", 175.0, 190.0, float(P['cure_temp']))
            cure_uniformity = st.number_input("Uniformity (°C)", 1.0, 3.0, float(P['cure_uniformity']))
            
            st.markdown("**Inspection**")
            reliability = st.number_input("Reliability Score", 80.0, 100.0, float(P['reliability']))
            defects = st.number_input("Defect Count", 0, 5, int(P['defects']))
        
        # Inline validation warnings
        warns = []
        if die_temp > 198: warns.append(f"⚠️ Die temp {die_temp}°C exceeds safe limit (198°C)")
        if wire_strength < 6: warns.append(f"⚠️ Wire pull strength {wire_strength} gf is critically low (<6 gf)")
        if die_void > 5: warns.append(f"⚠️ Die void {die_void}% is very high (>5%)")
        if mold_pressure > 10: warns.append(f"⚠️ Mold pressure {mold_pressure} MPa may cause flash defects")
        for w in warns:
            st.warning(w)
        
        submitted = st.form_submit_button("▶ Submit Data")
        
        if submitted:
            from datetime import datetime as _dt
            manual_data = {
                'batch_id': f"MANUAL_{_dt.now().strftime('%Y%m%d%H%M%S')}",
                'timestamp': _dt.now().isoformat(),
                'machine_id': 'MANUAL_INPUT',
                'die_temperature': die_temp,
                'die_void_percentage': die_void,
                'die_placement_accuracy': die_placement,
                'wire_bonding_force': wire_force,
                'wire_pull_strength': wire_strength,
                'wire_loop_height': wire_loop,
                'mold_temperature': mold_temp,
                'mold_pressure': mold_pressure,
                'mold_voids': mold_voids,
                'cure_temperature': cure_temp,
                'cure_uniformity': cure_uniformity,
                'inspect_reliability_score': reliability,
                'inspect_defect_count': defects,
                'die_epoxy_temperature': die_temp - 30,
                'die_bond_line_thickness': 25.0,
                'die_cure_time': 75.0,
                'die_pressure': 0.8,
                'wire_ultrasonic_power': 90.0,
                'wire_bonding_temperature': 165.0,
                'wire_diameter': 25.0,
                'wire_bond_time': 20.0,
                'mold_fill_time': 4.0,
                'mold_compound_viscosity': 125.0,
                'mold_transfer_speed': 12.5,
                'mold_clamp_force': 60.0,
                'cure_time': 150.0,
                'cure_humidity': 40.0,
                'cure_thermal_profile': 3.0,
                'cure_oxygen_level': 0.5,
                'inspect_visual_score': max(0, reliability - 2),
                'inspect_electrical_test': 1 if defects == 0 else 0,
                'inspect_dimensional_accuracy': 15.0,
                'inspect_lead_coplanarity': 40.0,
                'status': 'UNKNOWN'
            }
            st.session_state.current_data = manual_data
            st.session_state.pop('_qf', None)
            st.success("✓ Manual data submitted")
            st.rerun()


def display_data_details(data: dict):
    """Display detailed data view grouped by stage"""
    
    st.markdown("#### 📋 Complete Process Data by Stage")
    
    STAGE_GROUPS = [
        ("🔩 Die Attach",   "#0043ce", ["die_temperature","die_void_percentage","die_placement_accuracy","die_epoxy_temperature","die_bond_line_thickness","die_cure_time","die_pressure"]),
        ("🔗 Wire Bonding", "#0072c3", ["wire_bonding_force","wire_pull_strength","wire_loop_height","wire_ultrasonic_power","wire_bonding_temperature","wire_diameter","wire_bond_time"]),
        ("🧱 Molding",      "#a2191f", ["mold_temperature","mold_pressure","mold_voids","mold_fill_time","mold_compound_viscosity","mold_transfer_speed","mold_clamp_force"]),
        ("🔥 Curing",       "#b45309", ["cure_temperature","cure_time","cure_uniformity","cure_humidity","cure_thermal_profile","cure_oxygen_level"]),
        ("🔍 Inspection",   "#198038", ["inspect_reliability_score","inspect_defect_count","inspect_visual_score","inspect_electrical_test","inspect_dimensional_accuracy","inspect_lead_coplanarity"]),
        ("📦 Metadata",     "#697077", ["batch_id","timestamp","machine_id","status","predicted_status","confidence"]),
    ]
    
    col_left, col_right = st.columns(2)
    for i, (stage_name, color, params) in enumerate(STAGE_GROUPS):
        col = col_left if i % 2 == 0 else col_right
        with col:
            with st.expander(stage_name, expanded=(i == 0)):
                rows = []
                for p in params:
                    val = data.get(p)
                    if val is not None:
                        rows.append({"Parameter": p.replace('_',' ').title(), "Value": val})
                if rows:
                    import pandas as _pd
                    df = _pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.caption("No data for this stage.")
    
    # Full raw download
    import pandas as _pd2
    df_full = _pd2.DataFrame([data]).T
    df_full.columns = ['Value']
    csv = df_full.to_csv()
    st.download_button(
        label="📥 Download Full Data (CSV)",
        data=csv,
        file_name=f"process_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def display_copilot_chat(data: dict):
    """Display AI copilot chat interface"""
    
    api_client = st.session_state.api_client
    
    # IBM Bob branding banner
    st.markdown("""
    <div style="background:linear-gradient(90deg,#0f62fe 0%,#0043ce 100%);
         border-radius:10px;padding:14px 20px;margin-bottom:16px;
         display:flex;align-items:center;gap:14px;">
        <div style="font-size:2rem;">&#129302;</div>
        <div>
            <div style="color:white;font-weight:700;font-size:1.05rem;">IBM BOB · AI Manufacturing Copilot</div>
            <div style="color:rgba(255,255,255,.8);font-size:.82rem;">
                Powered by IBM Bob IDE &nbsp;·&nbsp; watsonx.ai &nbsp;·&nbsp; Natural Language Process Intelligence
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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

