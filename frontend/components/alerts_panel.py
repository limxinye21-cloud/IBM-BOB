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
                st.markdown("""
                <div style="background:linear-gradient(135deg,#e8f5e9,#f0fdf4);border:1px solid #198038;
                     border-left:4px solid #198038;border-radius:10px;padding:20px 24px;margin:8px 0;">
                    <div style="font-size:1.6rem;">✅</div>
                    <div style="font-weight:700;color:#198038;font-size:1.05rem;margin-top:6px;">All Clear — No Active Alerts</div>
                    <div style="color:#4a5568;font-size:.88rem;margin-top:4px;">All packaging stages are operating within normal parameters.</div>
                </div>
                """, unsafe_allow_html=True)
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
    # Determine colors based on severity — IBM Carbon palette
    if alert['severity'] == 'CRITICAL':
        border_color = "#da1e28"
        bg_color = "#fff1f1"
        icon = "🔴"
        text_color = "#da1e28"
    elif alert['severity'] == 'WARNING':
        border_color = "#b45309"
        bg_color = "#fffbeb"
        icon = "⚠️"
        text_color = "#b45309"
    else:
        border_color = "#0043ce"
        bg_color = "#eef2ff"
        icon = "ℹ️"
        text_color = "#0043ce"
    
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
                    background:{border_color};
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    text-align: center;
                    font-weight: 700;
                    font-size: .85rem;
                    letter-spacing:.5px;
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
                    marker=dict(colors=['#0043ce', '#b45309', '#da1e28']),
                    textfont=dict(color='#1a2238')
                )])
                
                fig.update_layout(
                    height=300,
                    paper_bgcolor='rgba(248,250,255,1)',
                    font=dict(color='#1a2238'),
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
                        padding: 10px 14px;
                        margin: 5px 0;
                        background: white;
                        border-left: 4px solid {'#da1e28' if alert['severity'] == 'CRITICAL' else '#b45309' if alert['severity'] == 'WARNING' else '#0043ce'};
                        border-radius: 6px;
                        box-shadow: 0 1px 4px rgba(0,0,0,.07);
                    ">
                        <div style="font-weight:600;color:#1a2238;">
                            {severity_icon} {alert['title']}
                        </div>
                        <div style="font-size: 12px; color: #697077;margin-top:3px;">
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
