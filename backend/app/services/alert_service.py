"""
Alert Service for AI Packaging Reliability Copilot
Automated alerting and notification system
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from backend.app.services.copilot_service import get_copilot_service
from backend.app.services.ml_service import get_ml_service


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Alert types"""
    PROCESS_SEVERE = "PROCESS_SEVERE"
    PARAMETER_ABNORMAL = "PARAMETER_ABNORMAL"
    QUALITY_DEGRADATION = "QUALITY_DEGRADATION"
    EQUIPMENT_ISSUE = "EQUIPMENT_ISSUE"
    BATCH_FAILURE = "BATCH_FAILURE"


class AlertService:
    """
    Service for managing alerts and notifications
    """
    
    def __init__(self):
        """Initialize alert service"""
        self.copilot_service = get_copilot_service()
        self.ml_service = get_ml_service()
        self.alert_rules = self._define_alert_rules()
        
    def _define_alert_rules(self) -> Dict:
        """
        Define alert triggering rules
        
        Returns:
            Dictionary of alert rules
        """
        return {
            'severe_status': {
                'condition': lambda data: data.get('predicted_status') == 'SEVERE' or data.get('status') == 'SEVERE',
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.PROCESS_SEVERE,
                'title': 'Critical Process Issue Detected',
                'priority': 1
            },
            'high_defect_count': {
                'condition': lambda data: data.get('inspect_defect_count', 0) > 2,
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.QUALITY_DEGRADATION,
                'title': 'High Defect Count Detected',
                'priority': 2
            },
            'low_reliability': {
                'condition': lambda data: data.get('inspect_reliability_score', 100) < 85,
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.QUALITY_DEGRADATION,
                'title': 'Low Reliability Score',
                'priority': 2
            },
            'electrical_failure': {
                'condition': lambda data: data.get('inspect_electrical_test', 1) == 0,
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.BATCH_FAILURE,
                'title': 'Electrical Test Failure',
                'priority': 1
            },
            'high_voids': {
                'condition': lambda data: data.get('die_void_percentage', 0) > 5 or data.get('mold_voids', 0) > 2,
                'severity': AlertSeverity.WARNING,
                'type': AlertType.PARAMETER_ABNORMAL,
                'title': 'High Void Percentage',
                'priority': 3
            },
            'weak_bonds': {
                'condition': lambda data: data.get('wire_pull_strength', 10) < 6,
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.EQUIPMENT_ISSUE,
                'title': 'Weak Wire Bonds Detected',
                'priority': 1
            },
            'temperature_deviation': {
                'condition': lambda data: (
                    data.get('die_temperature', 185) > 195 or 
                    data.get('die_temperature', 185) < 175 or
                    data.get('mold_temperature', 175) > 183 or
                    data.get('cure_temperature', 180) > 188
                ),
                'severity': AlertSeverity.WARNING,
                'type': AlertType.PARAMETER_ABNORMAL,
                'title': 'Temperature Out of Range',
                'priority': 3
            },
            # ---------------------------------------------------------------- #
            # Scenario-specific rules
            # ---------------------------------------------------------------- #
            'curing_incomplete': {
                'condition': lambda data: (
                    data.get('cure_time', 150) < 120 or
                    data.get('cure_temperature', 181) < 178
                ),
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.PROCESS_SEVERE,
                'title': 'Incomplete Curing Detected',
                'priority': 1
            },
            'cure_uniformity_poor': {
                'condition': lambda data: data.get('cure_uniformity', 1.0) > 2.5,
                'severity': AlertSeverity.WARNING,
                'type': AlertType.PARAMETER_ABNORMAL,
                'title': 'Poor Cure Temperature Uniformity',
                'priority': 2
            },
            'molding_compound_viscosity': {
                'condition': lambda data: (
                    data.get('mold_compound_viscosity', 127) > 155 or
                    data.get('mold_compound_viscosity', 127) < 80
                ),
                'severity': AlertSeverity.WARNING,
                'type': AlertType.PARAMETER_ABNORMAL,
                'title': 'Molding Compound Viscosity Out of Spec',
                'priority': 2
            },
            'mold_void_warning': {
                'condition': lambda data: data.get('mold_voids', 0) > 1.0,
                'severity': AlertSeverity.WARNING,
                'type': AlertType.PARAMETER_ABNORMAL,
                'title': 'Elevated Mold Void Percentage',
                'priority': 3
            },
            'mold_temperature_low': {
                'condition': lambda data: data.get('mold_temperature', 176) < 165,
                'severity': AlertSeverity.WARNING,
                'type': AlertType.PARAMETER_ABNORMAL,
                'title': 'Mold Temperature Below Minimum',
                'priority': 3
            },
            'wire_ultrasonic_low': {
                'condition': lambda data: data.get('wire_ultrasonic_power', 92) < 70,
                'severity': AlertSeverity.WARNING,
                'type': AlertType.EQUIPMENT_ISSUE,
                'title': 'Wire Bonding Ultrasonic Power Low',
                'priority': 2
            },
            'inspection_visual_fail': {
                'condition': lambda data: data.get('inspect_visual_score', 95) < 85,
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.QUALITY_DEGRADATION,
                'title': 'Visual Inspection Score Below Threshold',
                'priority': 2
            },
            'dimensional_accuracy_severe': {
                'condition': lambda data: data.get('inspect_dimensional_accuracy', 10) > 40,
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.QUALITY_DEGRADATION,
                'title': 'Dimensional Accuracy Out of Spec',
                'priority': 2
            },
            'lead_coplanarity_severe': {
                'condition': lambda data: data.get('inspect_lead_coplanarity', 40) > 100,
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.QUALITY_DEGRADATION,
                'title': 'Lead Coplanarity Critical Deviation',
                'priority': 2
            },
            'die_placement_severe': {
                'condition': lambda data: data.get('die_placement_accuracy', 5) > 15,
                'severity': AlertSeverity.WARNING,
                'type': AlertType.PARAMETER_ABNORMAL,
                'title': 'Die Placement Accuracy Degraded',
                'priority': 3
            },
            'cascading_multi_stage': {
                'condition': lambda data: (
                    data.get('die_void_percentage', 0) > 5 and
                    data.get('wire_pull_strength', 10) < 6 and
                    data.get('inspect_reliability_score', 100) < 85
                ),
                'severity': AlertSeverity.CRITICAL,
                'type': AlertType.PROCESS_SEVERE,
                'title': 'CRITICAL: Cascading Multi-Stage Failure',
                'priority': 1
            },
        }
    
    def check_alerts(self, process_data: Dict) -> List[Dict]:
        """
        Check if any alert conditions are met
        
        Args:
            process_data: Current process data
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            if rule['condition'](process_data):
                alert = self._create_alert(
                    rule_name=rule_name,
                    process_data=process_data,
                    severity=rule['severity'],
                    alert_type=rule['type'],
                    title=rule['title'],
                    priority=rule['priority']
                )
                triggered_alerts.append(alert)
        
        # Sort by priority
        triggered_alerts.sort(key=lambda x: x['priority'])
        
        return triggered_alerts
    
    def _create_alert(
        self,
        rule_name: str,
        process_data: Dict,
        severity: AlertSeverity,
        alert_type: AlertType,
        title: str,
        priority: int
    ) -> Dict:
        """
        Create alert with detailed information
        
        Args:
            rule_name: Name of triggered rule
            process_data: Process data
            severity: Alert severity
            alert_type: Alert type
            title: Alert title
            priority: Alert priority
            
        Returns:
            Alert dictionary
        """
        # Get copilot explanation
        context = {'current_data': process_data}
        copilot_response = self.copilot_service.process_query(
            "Why is this batch showing issues?",
            context=context
        )
        
        # Get critical parameters
        critical_params = self.copilot_service._identify_abnormal_parameters(process_data)
        
        # Build alert
        alert = {
            'alert_id': f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{rule_name}",
            'timestamp': datetime.now().isoformat(),
            'batch_id': process_data.get('batch_id', 'UNKNOWN'),
            'machine_id': process_data.get('machine_id', 'UNKNOWN'),
            'rule_name': rule_name,
            'severity': severity.value,
            'type': alert_type.value,
            'title': title,
            'priority': priority,
            'status': process_data.get('predicted_status', process_data.get('status', 'UNKNOWN')),
            'explanation': copilot_response.get('answer', 'No explanation available'),
            'confidence': copilot_response.get('confidence', 0.0),
            'critical_parameters': [
                {
                    'parameter': param,
                    'value': info['value'],
                    'severity': info['severity'],
                    'normal_range': f"{info['normal_min']}-{info['normal_max']} {info['unit']}"
                }
                for param, info in critical_params[:5]
            ],
            'recommended_actions': self._generate_recommended_actions(critical_params),
            'escalation_required': severity == AlertSeverity.CRITICAL and priority == 1
        }
        
        return alert
    
    def _generate_recommended_actions(self, critical_params: List) -> List[str]:
        """
        Generate recommended actions based on critical parameters
        
        Args:
            critical_params: List of critical parameters
            
        Returns:
            List of recommended actions
        """
        actions = []
        
        for param, info in critical_params[:3]:
            if 'temperature' in param.lower():
                if info['value'] > info['normal_max']:
                    actions.append(f"Reduce {param} to {info['normal_min']}-{info['normal_max']} {info['unit']}")
                else:
                    actions.append(f"Increase {param} to {info['normal_min']}-{info['normal_max']} {info['unit']}")
            
            elif 'void' in param.lower():
                actions.append(f"Investigate and reduce {param} (currently {info['value']:.1f}{info['unit']})")
            
            elif 'strength' in param.lower() or 'force' in param.lower():
                if info['value'] < info['normal_min']:
                    actions.append(f"Increase {param} to improve bond quality")
                else:
                    actions.append(f"Reduce {param} to prevent damage")
            
            elif 'defect' in param.lower():
                actions.append(f"Inspect and address defects (count: {int(info['value'])})")
            
            else:
                actions.append(f"Adjust {param} to normal range: {info['normal_min']}-{info['normal_max']} {info['unit']}")
        
        # Add general actions
        if len(critical_params) > 1:
            actions.append("Review complete process parameters")
            actions.append("Consider stopping batch for investigation")
        
        return actions
    
    def generate_alert_message(self, alert: Dict) -> str:
        """
        Generate formatted alert message
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Formatted message string
        """
        message = f"""
🚨 **{alert['title']}**

**Alert ID**: {alert['alert_id']}
**Severity**: {alert['severity']}
**Priority**: P{alert['priority']}
**Timestamp**: {alert['timestamp']}

**Batch Information**:
- Batch ID: {alert['batch_id']}
- Machine ID: {alert['machine_id']}
- Status: {alert['status']}

**Issue Analysis**:
{alert['explanation']}

**Critical Parameters**:
"""
        
        for param in alert['critical_parameters']:
            message += f"- {param['parameter']}: {param['value']:.2f} (Normal: {param['normal_range']}) - {param['severity']}\n"
        
        message += "\n**Recommended Actions**:\n"
        for i, action in enumerate(alert['recommended_actions'], 1):
            message += f"{i}. {action}\n"
        
        if alert['escalation_required']:
            message += "\n⚠️ **ESCALATION REQUIRED** - Immediate attention needed\n"
        
        return message
    
    def send_notification(
        self,
        alert: Dict,
        recipients: List[str],
        channels: List[str] = ['dashboard']
    ) -> Dict:
        """
        Send alert notification
        
        Args:
            alert: Alert dictionary
            recipients: List of recipient identifiers
            channels: Notification channels (dashboard, email, sms)
            
        Returns:
            Notification result
        """
        message = self.generate_alert_message(alert)
        
        results = {
            'alert_id': alert['alert_id'],
            'timestamp': datetime.now().isoformat(),
            'channels': {},
            'success': True
        }
        
        for channel in channels:
            if channel == 'dashboard':
                # Dashboard notification (always succeeds)
                results['channels']['dashboard'] = {
                    'status': 'sent',
                    'message': 'Alert displayed on dashboard'
                }
            
            elif channel == 'email':
                # Email notification (simulated)
                results['channels']['email'] = self._send_email(
                    recipients=recipients,
                    subject=alert['title'],
                    body=message
                )
            
            elif channel == 'sms':
                # SMS notification (simulated)
                results['channels']['sms'] = self._send_sms(
                    recipients=recipients,
                    message=f"{alert['title']} - Batch {alert['batch_id']} - {alert['severity']}"
                )
            
            elif channel == 'slack':
                # Slack notification (simulated)
                results['channels']['slack'] = self._send_slack(
                    message=message
                )
        
        return results
    
    def _send_email(self, recipients: List[str], subject: str, body: str) -> Dict:
        """Simulate email sending"""
        # In production, integrate with email service (SendGrid, AWS SES, etc.)
        return {
            'status': 'simulated',
            'recipients': recipients,
            'message': f'Email would be sent to {len(recipients)} recipients'
        }
    
    def _send_sms(self, recipients: List[str], message: str) -> Dict:
        """Simulate SMS sending"""
        # In production, integrate with SMS service (Twilio, AWS SNS, etc.)
        return {
            'status': 'simulated',
            'recipients': recipients,
            'message': f'SMS would be sent to {len(recipients)} recipients'
        }
    
    def _send_slack(self, message: str) -> Dict:
        """Simulate Slack notification"""
        # In production, integrate with Slack API
        return {
            'status': 'simulated',
            'message': 'Slack notification would be sent'
        }
    
    def create_workflow(self, alert: Dict) -> Dict:
        """
        Create automated workflow for alert handling
        (Integration point for watsonx Orchestrate)
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Workflow definition
        """
        workflow = {
            'workflow_id': f"WF_{alert['alert_id']}",
            'alert_id': alert['alert_id'],
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'steps': []
        }
        
        # Step 1: Notify stakeholders
        workflow['steps'].append({
            'step': 1,
            'action': 'notify',
            'description': 'Send notifications to relevant stakeholders',
            'status': 'pending',
            'assignee': 'system'
        })
        
        # Step 2: Create investigation ticket
        workflow['steps'].append({
            'step': 2,
            'action': 'create_ticket',
            'description': 'Create investigation ticket in tracking system',
            'status': 'pending',
            'assignee': 'system'
        })
        
        # Step 3: Assign to engineer
        workflow['steps'].append({
            'step': 3,
            'action': 'assign',
            'description': 'Assign to process engineer for investigation',
            'status': 'pending',
            'assignee': 'process_engineer'
        })
        
        # Step 4: Implement corrective actions
        workflow['steps'].append({
            'step': 4,
            'action': 'implement',
            'description': 'Implement recommended corrective actions',
            'status': 'pending',
            'assignee': 'process_engineer'
        })
        
        # Step 5: Verify resolution
        workflow['steps'].append({
            'step': 5,
            'action': 'verify',
            'description': 'Verify issue resolution and close ticket',
            'status': 'pending',
            'assignee': 'quality_engineer'
        })
        
        # Add escalation step if critical
        if alert['escalation_required']:
            workflow['steps'].insert(1, {
                'step': 1.5,
                'action': 'escalate',
                'description': 'Escalate to production manager',
                'status': 'pending',
                'assignee': 'production_manager'
            })
        
        return workflow


# Global alert service instance
_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    """
    Get or create alert service singleton
    
    Returns:
        Alert service instance
    """
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service


if __name__ == "__main__":
    print("=== Alert Service Test ===\n")
    
    alert_service = get_alert_service()
    
    # Test data (SEVERE condition)
    test_data = {
        'batch_id': 'BATCH_TEST_001',
        'machine_id': 'MACHINE_01',
        'timestamp': datetime.now().isoformat(),
        'die_temperature': 195.0,
        'die_void_percentage': 6.0,
        'wire_pull_strength': 5.0,
        'wire_bonding_force': 35.0,
        'mold_voids': 2.5,
        'cure_uniformity': 2.8,
        'inspect_reliability_score': 82.0,
        'inspect_defect_count': 3,
        'inspect_electrical_test': 0,
        'predicted_status': 'SEVERE'
    }
    
    # Check alerts
    print("Checking for alert conditions...")
    alerts = alert_service.check_alerts(test_data)
    
    print(f"\n✓ Found {len(alerts)} triggered alerts\n")
    
    for alert in alerts:
        print(f"Alert: {alert['title']}")
        print(f"  Severity: {alert['severity']}")
        print(f"  Priority: P{alert['priority']}")
        print(f"  Type: {alert['type']}")
        print(f"  Escalation Required: {alert['escalation_required']}")
        print()
    
    if alerts:
        # Generate message for first alert
        print("=" * 60)
        print("Alert Message:")
        print("=" * 60)
        message = alert_service.generate_alert_message(alerts[0])
        print(message)
        
        # Send notification
        print("\n" + "=" * 60)
        print("Sending Notification:")
        print("=" * 60)
        result = alert_service.send_notification(
            alert=alerts[0],
            recipients=['engineer@example.com', 'manager@example.com'],
            channels=['dashboard', 'email', 'sms']
        )
        print(f"Notification sent: {result['success']}")
        for channel, status in result['channels'].items():
            print(f"  {channel}: {status['status']}")
        
        # Create workflow
        print("\n" + "=" * 60)
        print("Creating Workflow:")
        print("=" * 60)
        workflow = alert_service.create_workflow(alerts[0])
        print(f"Workflow ID: {workflow['workflow_id']}")
        print(f"Steps: {len(workflow['steps'])}")
        for step in workflow['steps']:
            print(f"  Step {step['step']}: {step['action']} - {step['description']}")
    
    print("\n✓ Alert service test complete")

# Made with Bob
