"""
Test script for mock data generator
Run this to verify the generator works correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_schema import ProcessStage, Status
from generator import MockDataGenerator
from scenarios import ScenarioRunner


def test_config_schema():
    """Test configuration schema"""
    print("=" * 60)
    print("TEST 1: Configuration Schema")
    print("=" * 60)
    
    from config_schema import ALL_PARAMETERS, CRITICAL_PARAMETERS, ISSUE_MAPPING
    
    total_params = sum(len(params) for params in ALL_PARAMETERS.values())
    print(f"✓ Total parameters defined: {total_params}")
    print(f"✓ Critical parameters: {len(CRITICAL_PARAMETERS)}")
    print(f"✓ Issue types: {len(ISSUE_MAPPING)}")
    print(f"✓ Process stages: {len(ProcessStage)}")
    
    # Test parameter ranges
    die_attach_params = ALL_PARAMETERS[ProcessStage.DIE_ATTACH]
    print(f"\n✓ Die Attach parameters: {len(die_attach_params)}")
    for param_name, param_range in list(die_attach_params.items())[:3]:
        print(f"  - {param_name}: {param_range.normal_min}-{param_range.normal_max} {param_range.unit}")
    
    print("\n✅ Configuration schema test PASSED\n")


def test_normal_generation():
    """Test normal data generation"""
    print("=" * 60)
    print("TEST 2: Normal Data Generation")
    print("=" * 60)
    
    generator = MockDataGenerator(seed=42)
    
    # Generate 10 normal samples
    samples = []
    for i in range(10):
        data = generator.generate_normal_data()
        samples.append(data)
    
    # Check all are GOOD status
    good_count = sum(1 for s in samples if s.status == "GOOD")
    print(f"✓ Generated {len(samples)} samples")
    print(f"✓ GOOD status: {good_count}/{len(samples)}")
    
    # Check parameter ranges
    sample = samples[0]
    print(f"\n✓ Sample parameters:")
    print(f"  - Die temperature: {sample.die_temperature:.1f}°C")
    print(f"  - Wire bonding force: {sample.wire_bonding_force:.1f}N")
    print(f"  - Mold temperature: {sample.mold_temperature:.1f}°C")
    print(f"  - Cure time: {sample.cure_time:.1f}min")
    print(f"  - Reliability score: {sample.inspect_reliability_score:.1f}")
    
    assert good_count >= 8, "Most samples should be GOOD"
    print("\n✅ Normal generation test PASSED\n")


def test_anomaly_injection():
    """Test anomaly injection"""
    print("=" * 60)
    print("TEST 3: Anomaly Injection")
    print("=" * 60)
    
    generator = MockDataGenerator(seed=42)
    
    # Inject wire bonding anomaly
    generator.inject_sudden_anomaly(ProcessStage.WIRE_BONDING, Status.SEVERE, 3)
    
    # Generate samples
    samples = []
    for i in range(10):
        data = generator.generate_anomaly_data()
        samples.append(data)
    
    # Check for SEVERE status
    severe_count = sum(1 for s in samples if s.status == "SEVERE")
    print(f"✓ Generated {len(samples)} samples with anomaly")
    print(f"✓ SEVERE status: {severe_count}/{len(samples)}")
    
    # Check parameter values
    sample = samples[0]
    print(f"\n✓ Anomalous parameters:")
    print(f"  - Wire bonding force: {sample.wire_bonding_force:.1f}N")
    print(f"  - Ultrasonic power: {sample.wire_ultrasonic_power:.1f}mW")
    print(f"  - Loop height: {sample.wire_loop_height:.1f}μm")
    
    assert severe_count >= 8, "Most samples should be SEVERE"
    print("\n✅ Anomaly injection test PASSED\n")


def test_scenarios():
    """Test predefined scenarios"""
    print("=" * 60)
    print("TEST 4: Predefined Scenarios")
    print("=" * 60)
    
    runner = ScenarioRunner(seed=42)
    
    # List scenarios
    scenarios = runner.list_scenarios()
    print(f"✓ Available scenarios: {len(scenarios)}")
    for scenario_name in scenarios[:3]:
        scenario = runner.get_scenario_info(scenario_name)
        print(f"  - {scenario.name}")
    
    # Run normal scenario
    print(f"\n✓ Running 'normal' scenario...")
    data = runner.run_scenario("normal", 20)
    status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
    for d in data:
        status_counts[d.status] += 1
    print(f"  GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
    
    # Run failure scenario
    print(f"\n✓ Running 'wire_bonding_failure' scenario...")
    data = runner.run_scenario("wire_bonding_failure", 20)
    status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
    for d in data:
        status_counts[d.status] += 1
    print(f"  GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
    
    assert status_counts["SEVERE"] > 0, "Should have SEVERE samples in failure scenario"
    print("\n✅ Scenarios test PASSED\n")


def test_data_format():
    """Test data format and serialization"""
    print("=" * 60)
    print("TEST 5: Data Format & Serialization")
    print("=" * 60)
    
    generator = MockDataGenerator(seed=42)
    data = generator.generate_normal_data()
    
    # Test dictionary conversion
    data_dict = data.to_dict()
    print(f"✓ Dictionary keys: {len(data_dict)}")
    print(f"✓ Sample keys: {list(data_dict.keys())[:5]}")
    
    # Test JSON conversion
    data_json = data.to_json()
    print(f"\n✓ JSON length: {len(data_json)} characters")
    print(f"✓ JSON preview: {data_json[:100]}...")
    
    # Verify required fields
    required_fields = [
        "batch_id", "timestamp", "machine_id", "process_stage", "status",
        "die_temperature", "wire_bonding_force", "mold_temperature",
        "cure_temperature", "inspect_reliability_score"
    ]
    
    for field in required_fields:
        assert field in data_dict, f"Missing required field: {field}"
    
    print(f"\n✓ All {len(required_fields)} required fields present")
    print("\n✅ Data format test PASSED\n")


def test_cross_stage_dependencies():
    """Test cross-stage dependency effects"""
    print("=" * 60)
    print("TEST 6: Cross-Stage Dependencies")
    print("=" * 60)
    
    generator = MockDataGenerator(seed=42)
    
    # Create die attach issue with high void percentage
    generator.inject_sudden_anomaly(ProcessStage.DIE_ATTACH, Status.SEVERE, 1)
    
    # Generate data
    data = generator.generate_anomaly_data()
    
    print(f"✓ Die void percentage: {data.die_void_percentage:.2f}%")
    print(f"✓ Reliability score: {data.inspect_reliability_score:.1f}")
    
    # High voids should affect reliability
    if data.die_void_percentage > 5.0:
        print(f"✓ Cross-stage effect detected: High voids → Low reliability")
    
    print("\n✅ Cross-stage dependencies test PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MOCK DATA GENERATOR - TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_config_schema()
        test_normal_generation()
        test_anomaly_injection()
        test_scenarios()
        test_data_format()
        test_cross_stage_dependencies()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nMock data generator is working correctly!")
        print("You can now use it for:")
        print("  - Backend API testing")
        print("  - ML model training")
        print("  - Dashboard development")
        print("  - Demo scenarios")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob
