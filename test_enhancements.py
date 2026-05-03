"""
Test suite for code enhancements from review findings
Tests all improvements made to the AI Packaging Reliability system
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

def test_scenario_display_component():
    """Test scenario display component"""
    print("\n=== Testing Scenario Display Component ===")
    
    try:
        from frontend.components import scenario_display
        
        # Test SCENARIO_CONFIG exists and has all 8 scenarios
        expected_scenarios = [
            'normal', 'die_attach_drift', 'wire_bonding_failure',
            'molding_issue', 'curing_incomplete', 'inspection_failure',
            'cascading_failure', 'intermittent_warning'
        ]
        
        assert hasattr(scenario_display, 'SCENARIO_CONFIG'), "SCENARIO_CONFIG not found"
        
        for scenario in expected_scenarios:
            assert scenario in scenario_display.SCENARIO_CONFIG, f"Scenario {scenario} not found"
            config = scenario_display.SCENARIO_CONFIG[scenario]
            
            # Verify required fields
            assert 'name' in config, f"Missing 'name' in {scenario}"
            assert 'icon' in config, f"Missing 'icon' in {scenario}"
            assert 'color' in config, f"Missing 'color' in {scenario}"
            assert 'expected_status' in config, f"Missing 'expected_status' in {scenario}"
            assert 'description' in config, f"Missing 'description' in {scenario}"
            assert 'key_params' in config, f"Missing 'key_params' in {scenario}"
            assert 'alert_message' in config, f"Missing 'alert_message' in {scenario}"
            
            print(f"  [OK] Scenario '{scenario}' configured correctly")
        
        # Test helper functions exist
        assert hasattr(scenario_display, 'render_scenario_banner'), "render_scenario_banner not found"
        assert hasattr(scenario_display, 'render_scenario_metrics'), "render_scenario_metrics not found"
        assert hasattr(scenario_display, 'get_scenario_color'), "get_scenario_color not found"
        assert hasattr(scenario_display, 'get_scenario_status'), "get_scenario_status not found"
        
        # Test get_scenario_color
        color = scenario_display.get_scenario_color('normal')
        assert color == '#10b981', f"Expected green color for normal, got {color}"
        
        # Test get_scenario_status
        status = scenario_display.get_scenario_status('wire_bonding_failure')
        assert status == 'SEVERE', f"Expected SEVERE status, got {status}"
        
        print("  [OK] All helper functions working correctly")
        print("[PASS] Scenario display component tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Scenario display component test failed: {e}")
        return False


def test_copilot_null_safety():
    """Test null safety improvements in copilot routes"""
    print("\n=== Testing Copilot Null Safety ===")
    
    try:
        from backend.app.api.routes import copilot
        import inspect
        
        # Check get_recent_interactions has null safety
        source = inspect.getsource(copilot.get_recent_interactions)
        assert 'getattr' in source, "getattr not found in get_recent_interactions"
        assert 'if i is not None' in source, "Null check not found in get_recent_interactions"
        print("  [OK] get_recent_interactions has null safety checks")
        
        # Check get_interaction has null safety
        source = inspect.getsource(copilot.get_interaction)
        assert 'getattr' in source, "getattr not found in get_interaction"
        print("  [OK] get_interaction has null safety checks")
        
        print("[PASS] Copilot null safety tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Copilot null safety test failed: {e}")
        return False


def test_ml_service_thresholds():
    """Test threshold refactoring in ml_service"""
    print("\n=== Testing ML Service Thresholds ===")
    
    try:
        from backend.app.services import ml_service
        
        # Test THRESHOLDS constant exists
        assert hasattr(ml_service, 'THRESHOLDS'), "THRESHOLDS constant not found"
        
        thresholds = ml_service.THRESHOLDS
        
        # Verify all expected thresholds
        expected_params = [
            'die_void_percentage', 'die_temperature', 'wire_pull_strength',
            'wire_bonding_force', 'mold_voids', 'cure_uniformity',
            'inspect_reliability_score', 'inspect_defect_count'
        ]
        
        for param in expected_params:
            assert param in thresholds, f"Threshold for {param} not found"
            print(f"  [OK] Threshold defined for {param}")
        
        # Test MLService has _check_parameter_threshold method
        service = ml_service.MLService()
        assert hasattr(service, '_check_parameter_threshold'), "_check_parameter_threshold method not found"
        
        # Test the method works
        result = service._check_parameter_threshold(
            'die_void_percentage',
            6.0,
            thresholds['die_void_percentage']
        )
        assert result == 'severe', f"Expected 'severe' for void 6%, got {result}"
        
        result = service._check_parameter_threshold(
            'die_void_percentage',
            4.0,
            thresholds['die_void_percentage']
        )
        assert result == 'warning', f"Expected 'warning' for void 4%, got {result}"
        
        result = service._check_parameter_threshold(
            'die_void_percentage',
            2.0,
            thresholds['die_void_percentage']
        )
        assert result == 'good', f"Expected 'good' for void 2%, got {result}"
        
        print("  [OK] _check_parameter_threshold method working correctly")
        print("[PASS] ML service threshold tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] ML service threshold test failed: {e}")
        return False


def test_physics_features_documentation():
    """Test physics features documentation improvements"""
    print("\n=== Testing Physics Features Documentation ===")
    
    try:
        from ml.training import physics_features
        
        # Test unit conversion constants
        assert hasattr(physics_features, 'PA_TO_MPA'), "PA_TO_MPA constant not found"
        assert hasattr(physics_features, 'GF_TO_N'), "GF_TO_N constant not found"
        assert hasattr(physics_features, 'UM_TO_M'), "UM_TO_M constant not found"
        print("  [OK] Unit conversion constants defined")
        
        # Test physical constants
        assert hasattr(physics_features, 'BOLTZMANN_CONSTANT'), "BOLTZMANN_CONSTANT not found"
        assert hasattr(physics_features, 'GAS_CONSTANT'), "GAS_CONSTANT not found"
        assert hasattr(physics_features, 'ELECTRON_VOLT_TO_JOULE'), "ELECTRON_VOLT_TO_JOULE not found"
        print("  [OK] Physical constants defined")
        
        # Test material property constants
        assert hasattr(physics_features, 'SILICON_CTE'), "SILICON_CTE not found"
        assert hasattr(physics_features, 'EPOXY_CTE_BELOW_TG'), "EPOXY_CTE_BELOW_TG not found"
        assert hasattr(physics_features, 'GOLD_WIRE_CTE'), "GOLD_WIRE_CTE not found"
        print("  [OK] Material property constants defined")
        
        # Test IMC constants
        assert hasattr(physics_features, 'IMC_ACTIVATION_ENERGY'), "IMC_ACTIVATION_ENERGY not found"
        print("  [OK] IMC constants defined")
        
        # Test moisture constants
        assert hasattr(physics_features, 'WATER_HEAT_OF_VAPORIZATION'), "WATER_HEAT_OF_VAPORIZATION not found"
        assert hasattr(physics_features, 'REFLOW_TEMPERATURE'), "REFLOW_TEMPERATURE not found"
        print("  [OK] Moisture constants defined")
        
        # Verify constants are used in calculations
        calculator = physics_features.PhysicsFeatureCalculator()
        import inspect
        
        # Check thermal stress uses constants
        source = inspect.getsource(calculator.calculate_thermal_stress)
        assert 'PA_TO_MPA' in source, "PA_TO_MPA not used in thermal stress calculation"
        assert 'SILICON_CTE' in source or 'EPOXY_CTE' in source, "Material constants not used"
        print("  [OK] Constants used in thermal stress calculation")
        
        # Check IMC calculation uses constants
        source = inspect.getsource(calculator.calculate_intermetallic_growth)
        assert 'IMC_ACTIVATION_ENERGY' in source, "IMC_ACTIVATION_ENERGY not used"
        assert 'BOLTZMANN_CONSTANT' in source, "BOLTZMANN_CONSTANT not used"
        print("  [OK] Constants used in IMC calculation")
        
        # Check moisture calculation uses constants
        source = inspect.getsource(calculator.calculate_moisture_stress)
        assert 'WATER_HEAT_OF_VAPORIZATION' in source, "WATER_HEAT_OF_VAPORIZATION not used"
        assert 'GAS_CONSTANT' in source, "GAS_CONSTANT not used"
        assert 'REFLOW_TEMPERATURE' in source, "REFLOW_TEMPERATURE not used"
        print("  [OK] Constants used in moisture stress calculation")
        
        print("[PASS] Physics features documentation tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Physics features documentation test failed: {e}")
        return False


def test_integration():
    """Test that all components work together"""
    print("\n=== Testing Integration ===")
    
    try:
        # Test that scenario display can be imported in dashboard context
        from frontend.components import scenario_display
        
        # Test ML service with thresholds
        from backend.app.services.ml_service import get_ml_service
        service = get_ml_service()
        
        # Test physics features calculator
        from ml.training.physics_features import PhysicsFeatureCalculator
        calculator = PhysicsFeatureCalculator()
        
        test_data = {
            'die_attach_temperature': 185.0,
            'die_void_percentage': 2.0,
            'wire_bonding_force': 45.0,
            'wire_pull_strength': 10.0,
            'mold_voids': 0.5,
            'cure_uniformity': 1.5,
            'inspect_reliability_score': 95.0,
            'inspect_defect_count': 0
        }
        
        # Test rule-based classification with new thresholds
        result = service._rule_based_classification(test_data)
        assert 'status' in result, "Status not in result"
        assert 'confidence' in result, "Confidence not in result"
        print(f"  [OK] ML service classification: {result['status']} ({result['confidence']:.2f})")
        
        # Test physics features calculation with new constants
        features = calculator.calculate_all_physics_features(test_data)
        assert len(features) > 0, "No physics features calculated"
        print(f"  [OK] Physics features calculated: {len(features)} features")
        
        # Test scenario display functions
        color = scenario_display.get_scenario_color('normal')
        status = scenario_display.get_scenario_status('normal')
        print(f"  [OK] Scenario display: color={color}, status={status}")
        
        print("[PASS] Integration tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        return False


def main():
    """Run all enhancement tests"""
    print("=" * 70)
    print("AI PACKAGING RELIABILITY - CODE ENHANCEMENTS TEST SUITE")
    print("=" * 70)
    
    results = {
        'Scenario Display Component': test_scenario_display_component(),
        'Copilot Null Safety': test_copilot_null_safety(),
        'ML Service Thresholds': test_ml_service_thresholds(),
        'Physics Features Documentation': test_physics_features_documentation(),
        'Integration': test_integration()
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status:8s} | {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All enhancement tests passed successfully!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

# Made with Bob
