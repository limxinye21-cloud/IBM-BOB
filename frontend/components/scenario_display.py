"""
Scenario Display Component
Provides scenario-specific UI elements for the AI Packaging Reliability system.
"""

import streamlit as st
from typing import Dict, List, Any, Optional

# Scenario configuration with all 8 scenarios
SCENARIO_CONFIG = {
    "normal": {
        "name": "Normal Operation",
        "icon": "✅",
        "color": "#10b981",
        "expected_status": "GOOD",
        "description": "All parameters within normal operating ranges",
        "key_params": ["temperature", "pressure", "humidity"],
        "alert_message": "System operating normally"
    },
    "die_attach_drift": {
        "name": "Die Attach Drift",
        "icon": "⚠️",
        "color": "#f59e0b",
        "expected_status": "WARNING",
        "description": "Die attach temperature or pressure drifting from optimal values",
        "key_params": ["die_attach_temp", "die_attach_pressure", "die_attach_time"],
        "alert_message": "Die attach parameters showing drift - monitor closely"
    },
    "wire_bonding_failure": {
        "name": "Wire Bonding Failure",
        "icon": "🔴",
        "color": "#ef4444",
        "expected_status": "SEVERE",
        "description": "Wire bonding force or temperature outside acceptable limits",
        "key_params": ["wire_bond_force", "wire_bond_temp", "wire_bond_power"],
        "alert_message": "Critical wire bonding issue detected - immediate action required"
    },
    "molding_issue": {
        "name": "Molding Issue",
        "icon": "⚠️",
        "color": "#f59e0b",
        "expected_status": "WARNING",
        "description": "Molding compound pressure or temperature anomalies",
        "key_params": ["mold_pressure", "mold_temp", "mold_time"],
        "alert_message": "Molding process showing anomalies"
    },
    "curing_incomplete": {
        "name": "Incomplete Curing",
        "icon": "🔴",
        "color": "#ef4444",
        "expected_status": "SEVERE",
        "description": "Curing temperature or time insufficient for proper bonding",
        "key_params": ["cure_temp", "cure_time", "cure_humidity"],
        "alert_message": "Curing process incomplete - quality at risk"
    },
    "inspection_failure": {
        "name": "Inspection Failure",
        "icon": "🔴",
        "color": "#ef4444",
        "expected_status": "SEVERE",
        "description": "Visual or electrical inspection detecting defects",
        "key_params": ["visual_defects", "electrical_test_pass_rate", "dimensional_accuracy"],
        "alert_message": "Multiple inspection failures detected"
    },
    "cascading_failure": {
        "name": "Cascading Failure",
        "icon": "🚨",
        "color": "#dc2626",
        "expected_status": "SEVERE",
        "description": "Multiple process stages showing failures simultaneously",
        "key_params": ["temperature", "pressure", "humidity", "die_attach_temp", "wire_bond_force"],
        "alert_message": "CRITICAL: Multiple process failures - system shutdown recommended"
    },
    "intermittent_warning": {
        "name": "Intermittent Warning",
        "icon": "⚡",
        "color": "#f59e0b",
        "expected_status": "WARNING",
        "description": "Sporadic parameter fluctuations requiring monitoring",
        "key_params": ["temperature", "pressure", "vibration"],
        "alert_message": "Intermittent fluctuations detected - continue monitoring"
    }
}


def render_scenario_banner(scenario_type: str) -> None:
    """
    Render a banner displaying current scenario information.
    
    Args:
        scenario_type: The type of scenario (e.g., 'normal', 'die_attach_drift')
    """
    config = SCENARIO_CONFIG.get(scenario_type, SCENARIO_CONFIG["normal"])
    
    # Create banner HTML
    banner_html = f"""
    <div style="
        background: linear-gradient(135deg, {config['color']}15 0%, {config['color']}05 100%);
        border-left: 4px solid {config['color']};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="font-size: 2.5em;">{config['icon']}</div>
            <div style="flex: 1;">
                <h2 style="margin: 0; color: {config['color']}; font-size: 1.5em;">
                    {config['name']}
                </h2>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.95em;">
                    {config['description']}
                </p>
            </div>
            <div style="
                background-color: {config['color']};
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9em;
            ">
                {config['expected_status']}
            </div>
        </div>
        <div style="
            margin-top: 15px;
            padding: 10px;
            background-color: rgba(255,255,255,0.7);
            border-radius: 5px;
            font-size: 0.9em;
            color: #333;
        ">
            <strong>Alert:</strong> {config['alert_message']}
        </div>
    </div>
    """
    
    st.markdown(banner_html, unsafe_allow_html=True)


def render_scenario_metrics(scenario_type: str, metrics: Dict[str, Any]) -> None:
    """
    Render scenario-specific metrics with highlighting for key parameters.
    
    Args:
        scenario_type: The type of scenario
        metrics: Dictionary of all available metrics
    """
    config = SCENARIO_CONFIG.get(scenario_type, SCENARIO_CONFIG["normal"])
    key_params = config["key_params"]
    
    st.markdown("### 🎯 Key Parameters for This Scenario")
    
    # Create columns for key metrics
    cols = st.columns(min(len(key_params), 4))
    
    for idx, param in enumerate(key_params):
        col_idx = idx % len(cols)
        with cols[col_idx]:
            # Get metric value
            value = metrics.get(param, "N/A")
            
            # Determine status color based on scenario
            if config["expected_status"] == "GOOD":
                status_color = "#10b981"
                status_icon = "✅"
            elif config["expected_status"] == "WARNING":
                status_color = "#f59e0b"
                status_icon = "⚠️"
            else:  # SEVERE
                status_color = "#ef4444"
                status_icon = "🔴"
            
            # Format parameter name for display
            display_name = param.replace("_", " ").title()
            
            # Render metric card
            metric_html = f"""
            <div style="
                background: linear-gradient(135deg, {status_color}15 0%, {status_color}05 100%);
                border: 2px solid {status_color};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                text-align: center;
            ">
                <div style="font-size: 1.5em; margin-bottom: 5px;">{status_icon}</div>
                <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">
                    {display_name}
                </div>
                <div style="font-size: 1.3em; font-weight: bold; color: {status_color};">
                    {value}
                </div>
            </div>
            """
            st.markdown(metric_html, unsafe_allow_html=True)


def get_scenario_color(scenario_type: str) -> str:
    """
    Get the color associated with a scenario type.
    
    Args:
        scenario_type: The type of scenario
        
    Returns:
        Hex color code
    """
    config = SCENARIO_CONFIG.get(scenario_type, SCENARIO_CONFIG["normal"])
    return config["color"]


def get_scenario_status(scenario_type: str) -> str:
    """
    Get the expected status for a scenario type.
    
    Args:
        scenario_type: The type of scenario
        
    Returns:
        Expected status string (GOOD, WARNING, or SEVERE)
    """
    config = SCENARIO_CONFIG.get(scenario_type, SCENARIO_CONFIG["normal"])
    return config["expected_status"]


def render_scenario_selector() -> Optional[str]:
    """
    Render a scenario selector dropdown.
    
    Returns:
        Selected scenario type or None
    """
    scenario_options = {
        config["name"]: scenario_type 
        for scenario_type, config in SCENARIO_CONFIG.items()
    }
    
    selected_name = st.selectbox(
        "Select Scenario to Simulate",
        options=list(scenario_options.keys()),
        help="Choose a scenario to see how the system responds"
    )
    
    return scenario_options.get(selected_name)

# Made with Bob
