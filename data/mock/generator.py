"""
Real-time Mock Data Generator for AI Packaging Reliability Copilot

This module generates realistic semiconductor packaging process data with:
- Normal operation patterns
- Gradual parameter drift
- Sudden anomalies
- Cross-stage dependencies
- Configurable scenarios (GOOD/WARNING/SEVERE)
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass, asdict

from data.mock.config_schema import (
    ProcessStage,
    Status,
    ALL_PARAMETERS,
    CROSS_STAGE_DEPENDENCIES,
    get_parameter_status,
    classify_overall_status,
)


@dataclass
class ProcessData:
    """Single process data point"""
    batch_id: str
    timestamp: str
    machine_id: str
    process_stage: str
    status: str
    
    # Die Attach
    die_temperature: float
    die_epoxy_temperature: float
    die_void_percentage: float
    die_placement_accuracy: float
    die_bond_line_thickness: float
    die_cure_time: float
    die_pressure: float
    
    # Wire Bonding
    wire_bonding_force: float
    wire_ultrasonic_power: float
    wire_loop_height: float
    wire_pull_strength: float
    wire_bonding_temperature: float
    wire_diameter: float
    wire_bond_time: float
    
    # Molding
    mold_temperature: float
    mold_pressure: float
    mold_fill_time: float
    mold_compound_viscosity: float
    mold_transfer_speed: float
    mold_clamp_force: float
    mold_voids: float
    
    # Curing
    cure_temperature: float
    cure_time: float
    cure_humidity: float
    cure_thermal_profile: float
    cure_uniformity: float
    cure_oxygen_level: float
    
    # Inspection
    inspect_defect_count: int
    inspect_visual_score: float
    inspect_electrical_test: int  # 1=pass, 0=fail
    inspect_reliability_score: float
    inspect_dimensional_accuracy: float
    inspect_lead_coplanarity: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class MockDataGenerator:
    """
    Generate realistic mock data for semiconductor packaging processes
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the generator
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            np.random.seed(seed)
        
        self.current_batch_id = self._generate_batch_id()
        self.current_time = datetime.now()
        self.machine_id = "PKG-LINE-01"
        
        # State tracking for temporal correlation
        self.previous_values: Dict[str, float] = {}
        self.drift_factors: Dict[str, float] = {}
        self.anomaly_active = False
        self.anomaly_stage: Optional[ProcessStage] = None
        self.anomaly_parameters: List[str] = []
        
    def _generate_batch_id(self) -> str:
        """Generate a batch ID in format B{YYYYMMDD}{sequence}"""
        date_str = datetime.now().strftime("%Y%m%d")
        sequence = np.random.randint(1000, 9999)
        return f"B{date_str}{sequence}"
    
    def _get_normal_value(
        self,
        param_name: str,
        stage: ProcessStage,
        add_noise: bool = True
    ) -> float:
        """
        Generate a normal value for a parameter
        
        Args:
            param_name: Parameter name
            stage: Process stage
            add_noise: Whether to add random noise
            
        Returns:
            Generated value within normal range
        """
        param_range = ALL_PARAMETERS[stage][param_name]
        
        # Calculate center of normal range
        center = (param_range.normal_min + param_range.normal_max) / 2
        range_width = param_range.normal_max - param_range.normal_min
        
        # Add temporal correlation (use previous value if exists)
        if param_name in self.previous_values:
            # 80% correlation with previous value
            prev_value = self.previous_values[param_name]
            correlation = 0.8
            value = correlation * prev_value + (1 - correlation) * center
        else:
            value = center
        
        # Add noise
        if add_noise:
            noise_std = range_width * 0.1  # 10% of range as std dev
            noise = np.random.normal(0, noise_std)
            value += noise
        
        # Apply drift if exists
        if param_name in self.drift_factors:
            value += self.drift_factors[param_name]
        
        # Clip to normal range
        value = np.clip(value, param_range.normal_min, param_range.normal_max)
        
        return value
    
    def _get_warning_value(self, param_name: str, stage: ProcessStage) -> float:
        """Generate a value in warning range"""
        param_range = ALL_PARAMETERS[stage][param_name]
        
        # Randomly choose upper or lower warning range
        if np.random.random() < 0.5:
            # Lower warning range
            value = np.random.uniform(
                param_range.warning_min,
                param_range.normal_min
            )
        else:
            # Upper warning range
            value = np.random.uniform(
                param_range.normal_max,
                param_range.warning_max
            )
        
        return value
    
    def _get_severe_value(self, param_name: str, stage: ProcessStage) -> float:
        """Generate a value in severe range"""
        param_range = ALL_PARAMETERS[stage][param_name]
        
        # Randomly choose upper or lower severe range
        if np.random.random() < 0.5:
            # Lower severe range
            value = np.random.uniform(
                param_range.severe_min,
                param_range.warning_min
            )
        else:
            # Upper severe range
            value = np.random.uniform(
                param_range.warning_max,
                param_range.severe_max
            )
        
        return value
    
    def _apply_cross_stage_effects(self, data: Dict[str, float]) -> Dict[str, float]:
        """
        Apply cross-stage dependency effects
        
        Args:
            data: Current parameter values
            
        Returns:
            Modified parameter values
        """
        # Die attach placement affects wire bonding
        if data.get("die_placement_accuracy", 0) > 15.0:
            # Increase bonding force slightly
            data["wire_bonding_force"] = min(
                data.get("wire_bonding_force", 45) * 1.1,
                55.0
            )
        
        # Die attach voids affect reliability
        if data.get("die_void_percentage", 0) > 5.0:
            # Decrease reliability score
            data["inspect_reliability_score"] = max(
                data.get("inspect_reliability_score", 95) - 15,
                70.0
            )
        
        # Wire bonding loop height affects molding
        if data.get("wire_loop_height", 225) < 200.0:
            # Reduce mold temperature to prevent wire sweep
            data["mold_temperature"] = max(
                data.get("mold_temperature", 175) - 5,
                165.0
            )
        
        # Molding voids affect curing
        if data.get("mold_voids", 0) > 2.0:
            # Increase cure uniformity issues
            data["cure_uniformity"] = min(
                data.get("cure_uniformity", 1) + 1.5,
                4.0
            )
        
        # Curing time affects reliability
        if data.get("cure_time", 150) < 120.0:
            # Decrease reliability score
            data["inspect_reliability_score"] = max(
                data.get("inspect_reliability_score", 95) - 10,
                75.0
            )
        
        return data
    
    def generate_normal_data(self) -> ProcessData:
        """Generate data for normal operation (GOOD status)"""
        data = {}
        
        # Generate all parameters in normal range
        for stage in ProcessStage:
            for param_name in ALL_PARAMETERS[stage].keys():
                value = self._get_normal_value(param_name, stage)
                
                # Special handling for integer parameters
                if param_name == "inspect_defect_count":
                    value = 0
                elif param_name == "inspect_electrical_test":
                    value = 1  # pass
                
                data[param_name] = value
                self.previous_values[param_name] = value
        
        # Apply cross-stage effects
        data = self._apply_cross_stage_effects(data)
        
        # Determine status
        statuses = {}
        for stage in ProcessStage:
            for param_name in ALL_PARAMETERS[stage].keys():
                status = get_parameter_status(param_name, data[param_name], stage)
                statuses[param_name] = status
        
        overall_status = classify_overall_status(statuses)
        
        # Create ProcessData object
        process_data = ProcessData(
            batch_id=self.current_batch_id,
            timestamp=self.current_time.isoformat(),
            machine_id=self.machine_id,
            process_stage="all_stages",
            status=overall_status.value,
            die_temperature=data["temperature"],
            die_epoxy_temperature=data["epoxy_temperature"],
            die_void_percentage=data["void_percentage"],
            die_placement_accuracy=data["placement_accuracy"],
            die_bond_line_thickness=data["bond_line_thickness"],
            die_cure_time=data["cure_time"],
            die_pressure=data["pressure"],
            wire_bonding_force=data["bonding_force"],
            wire_ultrasonic_power=data["ultrasonic_power"],
            wire_loop_height=data["loop_height"],
            wire_pull_strength=data["pull_strength"],
            wire_bonding_temperature=data["bonding_temperature"],
            wire_diameter=data["wire_diameter"],
            wire_bond_time=data["bond_time"],
            mold_temperature=data["mold_temperature"],
            mold_pressure=data["mold_pressure"],
            mold_fill_time=data["fill_time"],
            mold_compound_viscosity=data["compound_viscosity"],
            mold_transfer_speed=data["transfer_speed"],
            mold_clamp_force=data["clamp_force"],
            mold_voids=data["voids_in_mold"],
            cure_temperature=data["cure_temperature"],
            cure_time=data["cure_time"],
            cure_humidity=data["humidity"],
            cure_thermal_profile=data["thermal_profile"],
            cure_uniformity=data["uniformity"],
            cure_oxygen_level=data["oxygen_level"],
            inspect_defect_count=int(data["defect_count"]),
            inspect_visual_score=data["visual_score"],
            inspect_electrical_test=int(data["electrical_test"]),
            inspect_reliability_score=data["reliability_score"],
            inspect_dimensional_accuracy=data["dimensional_accuracy"],
            inspect_lead_coplanarity=data["lead_coplanarity"],
        )
        
        # Update time
        self.current_time += timedelta(seconds=30)
        
        return process_data
    
    def inject_gradual_drift(
        self,
        stage: ProcessStage,
        param_name: str,
        drift_rate: float = 0.1
    ):
        """
        Inject gradual parameter drift
        
        Args:
            stage: Process stage
            param_name: Parameter to drift
            drift_rate: Rate of drift per sample
        """
        self.drift_factors[param_name] = drift_rate
    
    def inject_sudden_anomaly(
        self,
        stage: ProcessStage,
        severity: Status = Status.SEVERE,
        num_parameters: int = 2
    ):
        """
        Inject sudden anomaly in specific stage
        
        Args:
            stage: Process stage
            severity: Severity level (WARNING or SEVERE)
            num_parameters: Number of parameters to affect
        """
        self.anomaly_active = True
        self.anomaly_stage = stage
        
        # Select random parameters from the stage
        available_params = list(ALL_PARAMETERS[stage].keys())
        self.anomaly_parameters = np.random.choice(
            available_params,
            size=min(num_parameters, len(available_params)),
            replace=False
        ).tolist()
    
    def generate_anomaly_data(self) -> ProcessData:
        """Generate data with active anomaly"""
        data = {}
        
        # Generate normal data first
        for stage in ProcessStage:
            for param_name in ALL_PARAMETERS[stage].keys():
                # Check if this parameter should be anomalous
                if (self.anomaly_active and 
                    stage == self.anomaly_stage and 
                    param_name in self.anomaly_parameters):
                    # Generate severe value
                    value = self._get_severe_value(param_name, stage)
                else:
                    # Generate normal value
                    value = self._get_normal_value(param_name, stage)
                
                # Special handling for integer parameters
                if param_name == "inspect_defect_count":
                    if self.anomaly_active and stage == self.anomaly_stage:
                        value = np.random.randint(3, 8)
                    else:
                        value = 0
                elif param_name == "inspect_electrical_test":
                    if self.anomaly_active and stage == self.anomaly_stage:
                        value = 0  # fail
                    else:
                        value = 1  # pass
                
                data[param_name] = value
                self.previous_values[param_name] = value
        
        # Apply cross-stage effects
        data = self._apply_cross_stage_effects(data)
        
        # Determine status
        statuses = {}
        for stage in ProcessStage:
            for param_name in ALL_PARAMETERS[stage].keys():
                status = get_parameter_status(param_name, data[param_name], stage)
                statuses[param_name] = status
        
        overall_status = classify_overall_status(statuses)
        
        # Create ProcessData object
        process_data = ProcessData(
            batch_id=self.current_batch_id,
            timestamp=self.current_time.isoformat(),
            machine_id=self.machine_id,
            process_stage=self.anomaly_stage.value if self.anomaly_stage else "all_stages",
            status=overall_status.value,
            die_temperature=data["temperature"],
            die_epoxy_temperature=data["epoxy_temperature"],
            die_void_percentage=data["void_percentage"],
            die_placement_accuracy=data["placement_accuracy"],
            die_bond_line_thickness=data["bond_line_thickness"],
            die_cure_time=data["cure_time"],
            die_pressure=data["pressure"],
            wire_bonding_force=data["bonding_force"],
            wire_ultrasonic_power=data["ultrasonic_power"],
            wire_loop_height=data["loop_height"],
            wire_pull_strength=data["pull_strength"],
            wire_bonding_temperature=data["bonding_temperature"],
            wire_diameter=data["wire_diameter"],
            wire_bond_time=data["bond_time"],
            mold_temperature=data["mold_temperature"],
            mold_pressure=data["mold_pressure"],
            mold_fill_time=data["fill_time"],
            mold_compound_viscosity=data["compound_viscosity"],
            mold_transfer_speed=data["transfer_speed"],
            mold_clamp_force=data["clamp_force"],
            mold_voids=data["voids_in_mold"],
            cure_temperature=data["cure_temperature"],
            cure_time=data["cure_time"],
            cure_humidity=data["humidity"],
            cure_thermal_profile=data["thermal_profile"],
            cure_uniformity=data["uniformity"],
            cure_oxygen_level=data["oxygen_level"],
            inspect_defect_count=int(data["defect_count"]),
            inspect_visual_score=data["visual_score"],
            inspect_electrical_test=int(data["electrical_test"]),
            inspect_reliability_score=data["reliability_score"],
            inspect_dimensional_accuracy=data["dimensional_accuracy"],
            inspect_lead_coplanarity=data["lead_coplanarity"],
        )
        
        # Update time
        self.current_time += timedelta(seconds=30)
        
        return process_data
    
    def clear_anomaly(self):
        """Clear active anomaly"""
        self.anomaly_active = False
        self.anomaly_stage = None
        self.anomaly_parameters = []
    
    def reset(self):
        """Reset generator state"""
        self.current_batch_id = self._generate_batch_id()
        self.current_time = datetime.now()
        self.previous_values = {}
        self.drift_factors = {}
        self.clear_anomaly()
    
    def generate_batch(
        self,
        num_samples: int = 100,
        anomaly_start: Optional[int] = None,
        anomaly_duration: int = 10,
        anomaly_stage: ProcessStage = ProcessStage.WIRE_BONDING
    ) -> List[ProcessData]:
        """
        Generate a batch of data samples
        
        Args:
            num_samples: Number of samples to generate
            anomaly_start: Sample index to start anomaly (None for no anomaly)
            anomaly_duration: Duration of anomaly in samples
            anomaly_stage: Stage where anomaly occurs
            
        Returns:
            List of ProcessData objects
        """
        batch_data = []
        
        for i in range(num_samples):
            # Check if we should inject anomaly
            if anomaly_start is not None:
                if i == anomaly_start:
                    self.inject_sudden_anomaly(anomaly_stage, Status.SEVERE, 3)
                elif i == anomaly_start + anomaly_duration:
                    self.clear_anomaly()
            
            # Generate data
            if self.anomaly_active:
                data = self.generate_anomaly_data()
            else:
                data = self.generate_normal_data()
            
            batch_data.append(data)
        
        return batch_data
    
    def generate_single(self, scenario=None) -> ProcessData:
        """
        Generate a single data sample
        
        Args:
            scenario: Optional scenario configuration (Scenario object or dict with 'status' and 'stage' keys)
            
        Returns:
            Single ProcessData object
        """
        if scenario:
            # Handle Scenario dataclass from scenarios.py
            if hasattr(scenario, 'setup_func'):
                # It's a Scenario object - apply its setup and generate
                scenario.setup_func(self)
                if self.anomaly_active:
                    data = self.generate_anomaly_data()
                else:
                    data = self.generate_normal_data()
                # Clear anomaly after single generation
                self.clear_anomaly()
                return data
            
            # Handle dictionary configuration
            elif isinstance(scenario, dict):
                target_status = scenario.get('status', 'GOOD')
                target_stage = scenario.get('stage')
                
                if target_status in ['WARNING', 'SEVERE'] and target_stage:
                    # Convert stage string to ProcessStage enum
                    stage_map = {
                        'die_attach': ProcessStage.DIE_ATTACH,
                        'wire_bonding': ProcessStage.WIRE_BONDING,
                        'molding': ProcessStage.MOLDING,
                        'curing': ProcessStage.CURING,
                        'inspection': ProcessStage.INSPECTION
                    }
                    
                    stage_enum = stage_map.get(target_stage, ProcessStage.WIRE_BONDING)
                    severity = Status.SEVERE if target_status == 'SEVERE' else Status.WARNING
                    
                    # Inject anomaly and generate
                    self.inject_sudden_anomaly(stage_enum, severity, 2)
                    data = self.generate_anomaly_data()
                    self.clear_anomaly()
                    
                    return data
        
        # Default: generate normal data
        return self.generate_normal_data()


# ============================================================================
# MAIN - Test the generator
# ============================================================================

if __name__ == "__main__":
    print("=== Mock Data Generator Test ===\n")
    
    # Create generator
    generator = MockDataGenerator(seed=42)
    
    # Generate normal data
    print("1. Generating 5 normal samples...")
    for i in range(5):
        data = generator.generate_normal_data()
        print(f"   Sample {i+1}: Status={data.status}, "
              f"Die Temp={data.die_temperature:.1f}°C, "
              f"Wire Force={data.wire_bonding_force:.1f}N")
    
    # Inject anomaly
    print("\n2. Injecting wire bonding anomaly...")
    generator.inject_sudden_anomaly(ProcessStage.WIRE_BONDING, Status.SEVERE, 3)
    
    for i in range(5):
        data = generator.generate_anomaly_data()
        print(f"   Sample {i+1}: Status={data.status}, "
              f"Wire Force={data.wire_bonding_force:.1f}N, "
              f"Ultrasonic={data.wire_ultrasonic_power:.1f}mW")
    
    # Clear anomaly
    print("\n3. Clearing anomaly and returning to normal...")
    generator.clear_anomaly()
    
    for i in range(3):
        data = generator.generate_normal_data()
        print(f"   Sample {i+1}: Status={data.status}")
    
    # Generate batch with anomaly
    print("\n4. Generating batch with anomaly at sample 50...")
    generator.reset()
    batch = generator.generate_batch(
        num_samples=100,
        anomaly_start=50,
        anomaly_duration=10,
        anomaly_stage=ProcessStage.DIE_ATTACH
    )
    
    # Count statuses
    status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
    for data in batch:
        status_counts[data.status] += 1
    
    print(f"   Total samples: {len(batch)}")
    print(f"   GOOD: {status_counts['GOOD']}")
    print(f"   WARNING: {status_counts['WARNING']}")
    print(f"   SEVERE: {status_counts['SEVERE']}")
    
    # Show sample JSON
    print("\n5. Sample JSON output:")
    print(batch[0].to_json())
    
    print("\n=== Test Complete ===")

# Made with Bob
