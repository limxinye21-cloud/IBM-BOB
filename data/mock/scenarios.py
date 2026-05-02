"""
Predefined Failure Scenarios for Mock Data Generation

This module defines realistic failure scenarios for testing and demonstration:
- Normal operation
- Gradual drift
- Sudden failures
- Cross-stage propagation
"""

from typing import Dict, List, Callable
from dataclasses import dataclass

from config_schema import ProcessStage, Status
from generator import MockDataGenerator, ProcessData


@dataclass
class Scenario:
    """Scenario definition"""
    name: str
    description: str
    duration: int  # Number of samples
    setup_func: Callable[[MockDataGenerator], None]


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

def setup_normal_operation(generator: MockDataGenerator):
    """Normal operation - all parameters in range"""
    generator.reset()


def setup_die_attach_drift(generator: MockDataGenerator):
    """Gradual temperature drift in die attach"""
    generator.reset()
    generator.inject_gradual_drift(ProcessStage.DIE_ATTACH, "temperature", 0.2)
    generator.inject_gradual_drift(ProcessStage.DIE_ATTACH, "void_percentage", 0.05)


def setup_wire_bonding_failure(generator: MockDataGenerator):
    """Sudden wire bonding failure"""
    generator.reset()
    generator.inject_sudden_anomaly(ProcessStage.WIRE_BONDING, Status.SEVERE, 3)


def setup_molding_issue(generator: MockDataGenerator):
    """Molding compound viscosity issue"""
    generator.reset()
    generator.inject_sudden_anomaly(ProcessStage.MOLDING, Status.SEVERE, 2)


def setup_curing_incomplete(generator: MockDataGenerator):
    """Incomplete curing due to temperature/time issues"""
    generator.reset()
    generator.inject_sudden_anomaly(ProcessStage.CURING, Status.SEVERE, 3)


def setup_inspection_failure(generator: MockDataGenerator):
    """Multiple defects detected at inspection"""
    generator.reset()
    generator.inject_sudden_anomaly(ProcessStage.INSPECTION, Status.SEVERE, 4)


def setup_cascading_failure(generator: MockDataGenerator):
    """
    Cascading failure: die attach issue propagates through stages
    This demonstrates cross-stage dependency
    """
    generator.reset()
    # Start with die attach issue
    generator.inject_sudden_anomaly(ProcessStage.DIE_ATTACH, Status.SEVERE, 2)


def setup_intermittent_warning(generator: MockDataGenerator):
    """Intermittent warnings in multiple stages"""
    generator.reset()
    generator.inject_sudden_anomaly(ProcessStage.WIRE_BONDING, Status.WARNING, 1)


# ============================================================================
# SCENARIO CATALOG
# ============================================================================

SCENARIOS = {
    "normal": Scenario(
        name="Normal Operation",
        description="All parameters within normal range, stable production",
        duration=100,
        setup_func=setup_normal_operation
    ),
    
    "die_attach_drift": Scenario(
        name="Die Attach Temperature Drift",
        description="Gradual temperature increase and void formation in die attach",
        duration=100,
        setup_func=setup_die_attach_drift
    ),
    
    "wire_bonding_failure": Scenario(
        name="Wire Bonding Failure",
        description="Sudden failure in wire bonding - force, ultrasonic power issues",
        duration=100,
        setup_func=setup_wire_bonding_failure
    ),
    
    "molding_issue": Scenario(
        name="Molding Compound Issue",
        description="Molding compound viscosity and void formation problems",
        duration=100,
        setup_func=setup_molding_issue
    ),
    
    "curing_incomplete": Scenario(
        name="Incomplete Curing",
        description="Insufficient cure time and temperature issues",
        duration=100,
        setup_func=setup_curing_incomplete
    ),
    
    "inspection_failure": Scenario(
        name="Inspection Failure",
        description="Multiple defects detected, electrical test failure",
        duration=100,
        setup_func=setup_inspection_failure
    ),
    
    "cascading_failure": Scenario(
        name="Cascading Failure",
        description="Die attach issue propagates through wire bonding to final inspection",
        duration=100,
        setup_func=setup_cascading_failure
    ),
    
    "intermittent_warning": Scenario(
        name="Intermittent Warnings",
        description="Occasional warnings in multiple stages, not severe",
        duration=100,
        setup_func=setup_intermittent_warning
    ),
}


# ============================================================================
# SCENARIO RUNNER
# ============================================================================

class ScenarioRunner:
    """Run predefined scenarios"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize scenario runner
        
        Args:
            seed: Random seed for reproducibility
        """
        self.generator = MockDataGenerator(seed=seed)
        self.current_scenario: str | None = None
    
    def list_scenarios(self) -> List[str]:
        """List available scenarios"""
        return list(SCENARIOS.keys())
    
    def get_scenario_info(self, scenario_name: str) -> Scenario:
        """Get scenario information"""
        if scenario_name not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        return SCENARIOS[scenario_name]
    
    def run_scenario(
        self,
        scenario_name: str,
        num_samples: int | None = None
    ) -> List[ProcessData]:
        """
        Run a specific scenario
        
        Args:
            scenario_name: Name of the scenario to run
            num_samples: Number of samples (None = use scenario default)
            
        Returns:
            List of generated ProcessData
        """
        if scenario_name not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = SCENARIOS[scenario_name]
        self.current_scenario = scenario_name
        
        # Setup scenario
        scenario.setup_func(self.generator)
        
        # Generate data
        duration = num_samples if num_samples is not None else scenario.duration
        batch_data = []
        
        for i in range(duration):
            if self.generator.anomaly_active:
                data = self.generator.generate_anomaly_data()
            else:
                data = self.generator.generate_normal_data()
            batch_data.append(data)
        
        return batch_data
    
    def run_demo_sequence(self) -> Dict[str, List[ProcessData]]:
        """
        Run a sequence of scenarios for demo purposes
        
        Returns:
            Dictionary mapping scenario names to data
        """
        demo_scenarios = [
            ("normal", 50),
            ("wire_bonding_failure", 30),
            ("normal", 20),
            ("die_attach_drift", 40),
            ("molding_issue", 30),
        ]
        
        results = {}
        for scenario_name, num_samples in demo_scenarios:
            print(f"Running scenario: {scenario_name} ({num_samples} samples)")
            data = self.run_scenario(scenario_name, num_samples)
            results[scenario_name] = data
        
        return results


# ============================================================================
# MAIN - Test scenarios
# ============================================================================

if __name__ == "__main__":
    print("=== Scenario Runner Test ===\n")
    
    runner = ScenarioRunner(seed=42)
    
    # List scenarios
    print("Available scenarios:")
    for i, scenario_name in enumerate(runner.list_scenarios(), 1):
        scenario = runner.get_scenario_info(scenario_name)
        print(f"{i}. {scenario.name}")
        print(f"   {scenario.description}")
        print()
    
    # Run normal scenario
    print("\n1. Running 'normal' scenario (10 samples)...")
    data = runner.run_scenario("normal", 10)
    status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
    for d in data:
        status_counts[d.status] += 1
    print(f"   GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
    
    # Run wire bonding failure
    print("\n2. Running 'wire_bonding_failure' scenario (10 samples)...")
    data = runner.run_scenario("wire_bonding_failure", 10)
    status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
    for d in data:
        status_counts[d.status] += 1
    print(f"   GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
    
    # Run die attach drift
    print("\n3. Running 'die_attach_drift' scenario (20 samples)...")
    data = runner.run_scenario("die_attach_drift", 20)
    status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
    for d in data:
        status_counts[d.status] += 1
    print(f"   GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
    
    # Show parameter evolution
    print("\n4. Parameter evolution in die_attach_drift:")
    for i, d in enumerate(data[::5]):  # Every 5th sample
        print(f"   Sample {i*5}: Temp={d.die_temperature:.1f}°C, Voids={d.die_void_percentage:.2f}%")
    
    print("\n=== Test Complete ===")

# Made with Bob
