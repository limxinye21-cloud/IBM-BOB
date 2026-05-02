"""
Alerts Panel Component for AI Packaging Reliability Copilot Dashboard
Display and manage system alerts
"""

import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime


def render_alerts_panel(api_client):
    """
    Render alerts panel with active alerts
    
    Args:
        api_client: API client instance
    """
    st.markdown("### 🚨 Active Alerts")
    
    try:
        # Get active alerts
        result = api_client._get("/alerts/active", params={'limit': 10})
        
        if result.get('success'):
            alerts = result.get('alerts', [])
            
            if not alerts:
                st.success("✓ No active alerts - All systems operating normally")
                return
            
            # Display alert count
            critical_count = sum(1 for a in alerts if a['severity'] == 'CRITICAL')
            warning_count = sum(1 for a in alerts if a['severity'] == 'WARNING')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Alerts", len(alerts))
            with col2:
                st.metric("Critical", critical_count, delta=None if critical_count == 0 else f"+{critical_count}")
            with col3:
                st.metric("Warning", warning_count)
            
            st.markdown("---")
            
            # Display alerts
            for alert in alerts:
                render_alert_card(alert, api_client)
        
        else:
            st.error("Failed to load alerts")
    
    except Exception as e:
        st.error(f"Error loading alerts: {e}")


def render_alert_card(alert: Dict, api_client):
    """
    Render individual alert card
    
    Args:
        alert: Alert dictionary
        api_client: API client instance
    """
    # Determine colors based on severity
    if alert['severity'] == 'CRITICAL':
        border_color = "#dc3545"
        bg_color = "#f8d7da"
        icon = "🔴"
    elif alert['severity'] == 'WARNING':
        border_color = "#ffc107"
        bg_color = "#fff3cd"
        icon = "🟡"
    else:
        border_color = "#17a2b8"
        bg_color = "#d1ecf1"
        icon = "🔵"
    
    # Create expander for alert details
    with st.expander(f"{icon} {alert['title']} - {alert['batch_id']}", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Alert ID**: {alert['alert_id']}")
            st.markdown(f"**Batch**: {alert['batch_id']} | **Machine**: {alert['machine_id']}")
            st.markdown(f"**Time**: {alert['timestamp'][:19]}")
            st.markdown(f"**Type**: {alert['type']}")
        
        with col2:
            st.markdown(f"**Severity**")
            st.markdown(
                f"""
                <div style="
                    background-color: {border_color};
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                ">
                    {alert['severity']}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 View Details", key=f"details_{alert['alert_id']}"):
                show_alert_details(alert['alert_id'], api_client)
        
        with col2:
            if not alert.get('acknowledged'):
                if st.button("✓ Acknowledge", key=f"ack_{alert['alert_id']}"):
                    acknowledge_alert(alert['alert_id'], api_client)
        
        with col3:
            if st.button("🔧 Create Workflow", key=f"workflow_{alert['alert_id']}"):
                create_workflow(alert['alert_id'], api_client)


def show_alert_details(alert_id: str, api_client):
    """
    Show detailed alert information
    
    Args:
        alert_id: Alert identifier
        api_client: API client instance
    """
    try:
        result = api_client._get(f"/alerts/{alert_id}")
        
        if result.get('success'):
            alert = result['alert']
            
            st.markdown("#### Alert Details")
            st.markdown(f"**Alert ID**: {alert['alert_id']}")
            st.markdown(f"**Batch**: {alert['batch_id']}")
            st.markdown(f"**Machine**: {alert['machine_id']}")
            st.markdown(f"**Severity**: {alert['severity']}")
            st.markdown(f"**Type**: {alert['type']}")
            st.markdown(f"**Status**: {alert['status']}")
            
            st.markdown("---")
            st.markdown("**Message**:")
            st.text(alert['message'])
            
            if alert.get('acknowledged'):
                st.info(f"✓ Acknowledged by {alert['acknowledged_by']} at {alert['acknowledged_at'][:19]}")
            
            if alert.get('resolved'):
                st.success(f"✓ Resolved by {alert['resolved_by']} at {alert['resolved_at'][:19]}")
                if alert.get('resolution_notes'):
                    st.markdown(f"**Resolution Notes**: {alert['resolution_notes']}")
        
        else:
            st.error("Failed to load alert details")
    
    except Exception as e:
        st.error(f"Error: {e}")


def acknowledge_alert(alert_id: str, api_client):
    """
    Acknowledge an alert
    
    Args:
        alert_id: Alert identifier
        api_client: API client instance
    """
    try:
        result = api_client._post(f"/alerts/{alert_id}/acknowledge", {
            'acknowledged_by': 'dashboard_user'
        })
        
        if result.get('success'):
            st.success(f"✓ Alert {alert_id} acknowledged")
            st.rerun()
        else:
            st.error("Failed to acknowledge alert")
    
    except Exception as e:
        st.error(f"Error: {e}")


def create_workflow(alert_id: str, api_client):
    """
    Create workflow for alert
    
    Args:
        alert_id: Alert identifier
        api_client: API client instance
    """
    try:
        result = api_client._post("/alerts/workflow/create", {
            'alert_id': alert_id
        })
        
        if result.get('success'):
            workflow = result['workflow']
            
            st.success(f"✓ Workflow created: {workflow['workflow_id']}")
            
            st.markdown("**Workflow Steps**:")
            for step in workflow['steps']:
                st.markdown(f"{step['step']}. {step['description']} (Assignee: {step['assignee']})")
        
        else:
            st.error("Failed to create workflow")
    
    except Exception as e:
        st.error(f"Error: {e}")


def render_alert_statistics(api_client, hours: int = 24):
    """
    Render alert statistics
    
    Args:
        api_client: API client instance
        hours: Time range in hours
    """
    st.markdown(f"### 📊 Alert Statistics (Last {hours} hours)")
    
    try:
        result = api_client._get("/alerts/statistics/summary", params={'hours': hours})
        
        if result.get('success'):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Alerts", result.get('total_alerts', 0))
            
            with col2:
                st.metric("Active", result.get('active_alerts', 0))
            
            with col3:
                st.metric("Ack Rate", f"{result.get('acknowledgment_rate', 0)}%")
            
            with col4:
                st.metric("Resolution Rate", f"{result.get('resolution_rate', 0)}%")
            
            # Severity distribution
            st.markdown("#### Severity Distribution")
            severity_dist = result.get('severity_distribution', {})
            
            if severity_dist:
                import plotly.graph_objects as go
                
                fig = go.Figure(data=[go.Pie(
                    labels=list(severity_dist.keys()),
                    values=list(severity_dist.values()),
                    hole=0.4,
                    marker=dict(colors=['#17a2b8', '#ffc107', '#dc3545'])
                )])
                
                fig.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No alerts in selected time range")
        
        else:
            st.error("Failed to load statistics")
    
    except Exception as e:
        st.error(f"Error: {e}")


def render_alert_history(api_client, hours: int = 24):
    """
    Render alert history
    
    Args:
        api_client: API client instance
        hours: Time range in hours
    """
    st.markdown(f"### 📜 Alert History (Last {hours} hours)")
    
    try:
        result = api_client._get("/alerts/history", params={'hours': hours})
        
        if result.get('success'):
            alerts = result.get('alerts', [])
            
            if not alerts:
                st.info("No alerts in selected time range")
                return
            
            # Create timeline
            for alert in alerts[:20]:  # Show last 20
                severity_icon = {
                    'CRITICAL': '🔴',
                    'WARNING': '🟡',
                    'INFO': '🔵'
                }.get(alert['severity'], '⚪')
                
                st.markdown(
                    f"""
                    <div style="
                        padding: 10px;
                        margin: 5px 0;
                        background-color: #f8f9fa;
                        border-left: 4px solid {'#dc3545' if alert['severity'] == 'CRITICAL' else '#ffc107' if alert['severity'] == 'WARNING' else '#17a2b8'};
                        border-radius: 5px;
                    ">
                        <div style="font-weight: bold;">
                            {severity_icon} {alert['title']}
                        </div>
                        <div style="font-size: 12px; color: #666;">
                            {alert['timestamp'][:19]} | Batch: {alert['batch_id']} | Status: {alert['status']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        else:
            st.error("Failed to load history")
    
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    # Test alerts panel
    st.set_page_config(page_title="Alerts Panel Test", layout="wide")
    
    st.title("Alerts Panel Component Test")
    
    # Mock API client
    class MockAPIClient:
        def _get(self, endpoint, params=None):
            if 'active' in endpoint:
                return {
                    'success': True,
                    'alerts': [
                        {
                            'alert_id': 'ALERT_001',
                            'batch_id': 'BATCH_001',
                            'machine_id': 'MACHINE_01',
                            'timestamp': '2024-01-15T10:30:00',
                            'severity': 'CRITICAL',
                            'type': 'PROCESS_SEVERE',
                            'title': 'Critical Process Issue Detected',
                            'acknowledged': False
                        }
                    ]
                }
            elif 'statistics' in endpoint:
                return {
                    'success': True,
                    'total_alerts': 10,
                    'active_alerts': 2,
                    'acknowledgment_rate': 80.0,
                    'resolution_rate': 60.0,
                    'severity_distribution': {
                        'CRITICAL': 3,
                        'WARNING': 5,
                        'INFO': 2
                    }
                }
            return {'success': True, 'alerts': []}
        
        def _post(self, endpoint, data):
            return {'success': True}
    
    mock_client = MockAPIClient()
    
    # Render components
    render_alerts_panel(mock_client)
    
    st.markdown("---")
    render_alert_statistics(mock_client, hours=24)
    
    st.markdown("---")
    render_alert_history(mock_client, hours=24)

# Made with Bob
