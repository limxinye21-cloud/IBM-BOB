"""
Integration Tests for AI Packaging Reliability Copilot
Tests end-to-end workflows across all system components
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, List
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.app.services.alert_service import AlertService
from backend.app.services.copilot_service import CopilotService
from backend.app.services.ml_service import MLService
from data.mock.generator import MockDataGenerator
from data.mock.scenarios import SCENARIOS


class TestEndToEndWorkflow:
    """Test complete system workflow from data generation to alert resolution"""
    
    @pytest.fixture
    def mock_generator(self):
        """Create mock data generator"""
        return MockDataGenerator()
    
    @pytest.fixture
    def alert_service(self):
        """Create alert service"""
        return AlertService()
    
    @pytest.fixture
    def copilot_service(self):
        """Create copilot service"""
        return CopilotService()
    
    @pytest.fixture
    def ml_service(self):
        """Create ML service"""
        return MLService()
    
    @pytest.mark.asyncio
    async def test_normal_operation_workflow(self, mock_generator, ml_service, alert_service):
        """Test workflow with normal operating conditions"""
        
        # Step 1: Generate normal data
        data = mock_generator.generate_single()
        assert data is not None
        assert 'batch_id' in data
        
        # Step 2: ML prediction
        prediction = await ml_service.predict(data)
        assert prediction is not None
        assert prediction['status'] in ['GOOD', 'WARNING', 'SEVERE']
        
        # Step 3: Check alerts (should be none for normal operation)
        alerts = await alert_service.check_alerts(data)
        
        # For normal data, expect no critical alerts
        critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
        assert len(critical_alerts) == 0
        
        print(f"✓ Normal operation workflow: {prediction['status']} status, {len(alerts)} alerts")
    
    @pytest.mark.asyncio
    async def test_severe_condition_workflow(self, mock_generator, ml_service, alert_service, copilot_service):
        """Test complete workflow when severe condition is detected"""
        
        # Step 1: Generate severe scenario data
        scenario = SCENARIOS['die_attach_issue']
        data = mock_generator.generate_single(scenario=scenario)
        assert data is not None
        
        # Step 2: ML prediction (should predict SEVERE)
        prediction = await ml_service.predict(data)
        assert prediction is not None
        data['predicted_status'] = prediction['status']
        data['confidence'] = prediction['confidence']
        
        # Step 3: Alert detection
        alerts = await alert_service.check_alerts(data)
        assert len(alerts) > 0
        
        # Should have at least one critical alert
        critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
        assert len(critical_alerts) > 0
        
        # Step 4: AI Copilot analysis
        alert = alerts[0]
        analysis = await copilot_service.analyze_issue(
            issue_type='die_attach',
            data=data
        )
        assert analysis is not None
        assert 'root_cause' in analysis
        assert 'recommendations' in analysis
        
        # Step 5: Workflow creation
        workflow = await alert_service.create_workflow(alert)
        assert workflow is not None
        assert 'workflow_id' in workflow
        assert len(workflow['steps']) > 0
        
        print(f"✓ Severe condition workflow: {len(alerts)} alerts, workflow {workflow['workflow_id']} created")
    
    @pytest.mark.asyncio
    async def test_multi_stage_issue_detection(self, mock_generator, alert_service, copilot_service):
        """Test detection of issues across multiple process stages"""
        
        # Generate data with wire bonding issue
        scenario = SCENARIOS['wire_bond_issue']
        data = mock_generator.generate_single(scenario=scenario)
        
        # Check alerts
        alerts = await alert_service.check_alerts(data)
        
        # Should detect wire bonding related alerts
        wire_alerts = [a for a in alerts if 'wire' in a['type'].lower() or 'bond' in a['type'].lower()]
        assert len(wire_alerts) > 0
        
        # Copilot should identify wire bonding parameters
        analysis = await copilot_service.analyze_issue(
            issue_type='wire_bonding',
            data=data
        )
        
        assert 'wire_bonding_force' in str(analysis) or 'wire_pull_strength' in str(analysis)
        
        print(f"✓ Multi-stage detection: {len(wire_alerts)} wire bonding alerts")
    
    @pytest.mark.asyncio
    async def test_alert_lifecycle(self, mock_generator, alert_service):
        """Test complete alert lifecycle: create → acknowledge → resolve"""
        
        # Generate severe data
        scenario = SCENARIOS['electrical_failure']
        data = mock_generator.generate_single(scenario=scenario)
        
        # Create alert
        alerts = await alert_service.check_alerts(data)
        assert len(alerts) > 0
        
        alert = alerts[0]
        alert_id = alert['alert_id']
        
        # Verify initial state
        assert alert['status'] == 'ACTIVE'
        assert alert['acknowledged'] == False
        assert alert['resolved'] == False
        
        # Acknowledge alert
        acknowledged = await alert_service.acknowledge_alert(
            alert_id=alert_id,
            acknowledged_by='test_engineer'
        )
        assert acknowledged['acknowledged'] == True
        
        # Resolve alert
        resolved = await alert_service.resolve_alert(
            alert_id=alert_id,
            resolved_by='test_engineer',
            resolution_notes='Issue resolved by parameter adjustment'
        )
        assert resolved['resolved'] == True
        assert resolved['status'] == 'RESOLVED'
        
        print(f"✓ Alert lifecycle: {alert_id} created → acknowledged → resolved")
    
    @pytest.mark.asyncio
    async def test_copilot_query_processing(self, copilot_service, mock_generator):
        """Test AI Copilot natural language query processing"""
        
        data = mock_generator.generate_single()
        
        # Test different query types
        queries = [
            "Why is this batch severe?",
            "Analyze die attach issue",
            "What parameters are abnormal?",
            "Suggest optimization",
            "Explain the current status"
        ]
        
        for query in queries:
            response = await copilot_service.process_query(
                query=query,
                context={'data': data}
            )
            
            assert response is not None
            assert 'response' in response
            assert len(response['response']) > 0
            
            print(f"✓ Query processed: '{query}' → {len(response['response'])} chars")
    
    @pytest.mark.asyncio
    async def test_notification_system(self, alert_service, mock_generator):
        """Test multi-channel notification system"""
        
        # Generate critical alert
        scenario = SCENARIOS['electrical_failure']
        data = mock_generator.generate_single(scenario=scenario)
        
        alerts = await alert_service.check_alerts(data)
        critical_alert = [a for a in alerts if a['severity'] == 'CRITICAL'][0]
        
        # Test notification sending
        channels = ['email', 'sms', 'slack']
        notifications = await alert_service.send_notification(
            alert=critical_alert,
            channels=channels
        )
        
        assert notifications is not None
        assert len(notifications) == len(channels)
        
        for channel, status in notifications.items():
            assert status['sent'] == True
            print(f"✓ Notification sent via {channel}")
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, mock_generator, ml_service, alert_service):
        """Test batch processing of multiple data points"""
        
        # Generate batch of data
        batch_size = 10
        batch_data = [mock_generator.generate_single() for _ in range(batch_size)]
        
        # Process batch predictions
        predictions = []
        for data in batch_data:
            pred = await ml_service.predict(data)
            predictions.append(pred)
        
        assert len(predictions) == batch_size
        
        # Check alerts for batch
        all_alerts = []
        for data in batch_data:
            alerts = await alert_service.check_alerts(data)
            all_alerts.extend(alerts)
        
        print(f"✓ Batch processing: {batch_size} samples, {len(all_alerts)} total alerts")
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, mock_generator, ml_service, alert_service):
        """Test system performance and response times"""
        
        import time
        
        # Test data generation speed
        start = time.time()
        for _ in range(100):
            data = mock_generator.generate_single()
        gen_time = time.time() - start
        
        # Test ML prediction speed
        data = mock_generator.generate_single()
        start = time.time()
        for _ in range(10):
            pred = await ml_service.predict(data)
        pred_time = (time.time() - start) / 10
        
        # Test alert checking speed
        start = time.time()
        for _ in range(10):
            alerts = await alert_service.check_alerts(data)
        alert_time = (time.time() - start) / 10
        
        print(f"✓ Performance metrics:")
        print(f"  - Data generation: {gen_time/100*1000:.2f}ms per sample")
        print(f"  - ML prediction: {pred_time*1000:.2f}ms per prediction")
        print(f"  - Alert checking: {alert_time*1000:.2f}ms per check")
        
        # Assert reasonable performance
        assert gen_time / 100 < 0.1  # < 100ms per sample
        assert pred_time < 1.0  # < 1s per prediction
        assert alert_time < 0.5  # < 500ms per check


class TestComponentIntegration:
    """Test integration between specific components"""
    
    @pytest.mark.asyncio
    async def test_ml_copilot_integration(self, ml_service, copilot_service, mock_generator):
        """Test ML model and Copilot working together"""
        
        data = mock_generator.generate_single()
        
        # Get ML prediction
        prediction = await ml_service.predict(data)
        
        # Get feature importance
        importance = await ml_service.get_feature_importance()
        
        # Copilot uses ML results for analysis
        data['predicted_status'] = prediction['status']
        analysis = await copilot_service.analyze_issue(
            issue_type='general',
            data=data
        )
        
        assert analysis is not None
        print(f"✓ ML-Copilot integration: {prediction['status']} → analysis generated")
    
    @pytest.mark.asyncio
    async def test_copilot_alert_integration(self, copilot_service, alert_service, mock_generator):
        """Test Copilot generating explanations for alerts"""
        
        scenario = SCENARIOS['molding_issue']
        data = mock_generator.generate_single(scenario=scenario)
        
        # Generate alerts
        alerts = await alert_service.check_alerts(data)
        
        if len(alerts) > 0:
            alert = alerts[0]
            
            # Copilot generates explanation
            message = await alert_service.generate_alert_message(alert, data)
            
            assert message is not None
            assert len(message) > 0
            assert 'molding' in message.lower() or 'temperature' in message.lower()
            
            print(f"✓ Copilot-Alert integration: Explanation generated for {alert['type']}")
    
    @pytest.mark.asyncio
    async def test_database_persistence(self, alert_service, mock_generator):
        """Test data persistence and retrieval"""
        
        # Generate and store alerts
        data = mock_generator.generate_single()
        alerts = await alert_service.check_alerts(data)
        
        if len(alerts) > 0:
            alert_id = alerts[0]['alert_id']
            
            # Retrieve alert
            retrieved = await alert_service.get_alert(alert_id)
            
            assert retrieved is not None
            assert retrieved['alert_id'] == alert_id
            
            print(f"✓ Database persistence: Alert {alert_id} stored and retrieved")


class TestScenarios:
    """Test specific manufacturing scenarios"""
    
    @pytest.mark.asyncio
    async def test_all_scenarios(self, mock_generator, ml_service, alert_service):
        """Test all predefined scenarios"""
        
        results = {}
        
        for scenario_name, scenario_config in SCENARIOS.items():
            # Generate data
            data = mock_generator.generate_single(scenario=scenario_config)
            
            # Get prediction
            prediction = await ml_service.predict(data)
            
            # Check alerts
            alerts = await alert_service.check_alerts(data)
            
            results[scenario_name] = {
                'status': prediction['status'],
                'confidence': prediction['confidence'],
                'alert_count': len(alerts),
                'critical_alerts': len([a for a in alerts if a['severity'] == 'CRITICAL'])
            }
            
            print(f"✓ Scenario '{scenario_name}': {prediction['status']} ({prediction['confidence']:.1%}), {len(alerts)} alerts")
        
        # Verify all scenarios processed
        assert len(results) == len(SCENARIOS)
        
        return results


def run_integration_tests():
    """Run all integration tests"""
    
    print("\n" + "="*80)
    print("AI PACKAGING RELIABILITY COPILOT - INTEGRATION TESTS")
    print("="*80 + "\n")
    
    # Run pytest
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto'
    ])


if __name__ == "__main__":
    run_integration_tests()

# Made with Bob
