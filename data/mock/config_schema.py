"""
AI Packaging Reliability Copilot - Configuration Schema
This file contains all parameter definitions, ranges, and thresholds
based on the comprehensive data schema designed in STEP 2.
"""

from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ProcessStage(Enum):
    """Process stages in semiconductor packaging"""
    DIE_ATTACH = "die_attach"
    WIRE_BONDING = "wire_bonding"
    MOLDING = "molding"
    CURING = "curing"
    INSPECTION = "inspection"


class Status(Enum):
    """System status classification"""
    GOOD = "GOOD"
    WARNING = "WARNING"
    SEVERE = "SEVERE"


@dataclass
class ParameterRange:
    """Parameter range definition"""
    name: str
    unit: str
    normal_min: float
    normal_max: float
    warning_min: float
    warning_max: float
    severe_min: float
    severe_max: float
    description: str


# ============================================================================
# DIE ATTACH PARAMETERS
# ============================================================================

DIE_ATTACH_PARAMS = {
    "temperature": ParameterRange(
        name="temperature",
        unit="°C",
        normal_min=180.0,
        normal_max=190.0,
        warning_min=175.0,
        warning_max=195.0,
        severe_min=170.0,
        severe_max=200.0,
        description="Die attach temperature"
    ),
    "epoxy_temperature": ParameterRange(
        name="epoxy_temperature",
        unit="°C",
        normal_min=150.0,
        normal_max=160.0,
        warning_min=145.0,
        warning_max=165.0,
        severe_min=140.0,
        severe_max=170.0,
        description="Epoxy dispensing temperature"
    ),
    "void_percentage": ParameterRange(
        name="void_percentage",
        unit="%",
        normal_min=0.0,
        normal_max=3.0,
        warning_min=3.0,
        warning_max=5.0,
        severe_min=5.0,
        severe_max=10.0,
        description="Void area in adhesive"
    ),
    "placement_accuracy": ParameterRange(
        name="placement_accuracy",
        unit="μm",
        normal_min=0.0,
        normal_max=10.0,
        warning_min=10.0,
        warning_max=15.0,
        severe_min=15.0,
        severe_max=25.0,
        description="Die placement precision"
    ),
    "bond_line_thickness": ParameterRange(
        name="bond_line_thickness",
        unit="μm",
        normal_min=20.0,
        normal_max=30.0,
        warning_min=15.0,
        warning_max=35.0,
        severe_min=10.0,
        severe_max=40.0,
        description="Adhesive thickness"
    ),
    "cure_time": ParameterRange(
        name="cure_time",
        unit="sec",
        normal_min=60.0,
        normal_max=90.0,
        warning_min=50.0,
        warning_max=120.0,
        severe_min=40.0,
        severe_max=150.0,
        description="Initial cure duration"
    ),
    "pressure": ParameterRange(
        name="pressure",
        unit="MPa",
        normal_min=0.5,
        normal_max=1.0,
        warning_min=0.3,
        warning_max=1.5,
        severe_min=0.1,
        severe_max=2.0,
        description="Applied pressure"
    ),
}

# ============================================================================
# WIRE BONDING PARAMETERS
# ============================================================================

WIRE_BONDING_PARAMS = {
    "bonding_force": ParameterRange(
        name="bonding_force",
        unit="N",
        normal_min=40.0,
        normal_max=50.0,
        warning_min=35.0,
        warning_max=55.0,
        severe_min=30.0,
        severe_max=60.0,
        description="Wire bonding force"
    ),
    "ultrasonic_power": ParameterRange(
        name="ultrasonic_power",
        unit="mW",
        normal_min=80.0,
        normal_max=100.0,
        warning_min=70.0,
        warning_max=110.0,
        severe_min=60.0,
        severe_max=120.0,
        description="Ultrasonic energy"
    ),
    "loop_height": ParameterRange(
        name="loop_height",
        unit="μm",
        normal_min=200.0,
        normal_max=250.0,
        warning_min=180.0,
        warning_max=280.0,
        severe_min=160.0,
        severe_max=300.0,
        description="Wire loop height"
    ),
    "pull_strength": ParameterRange(
        name="pull_strength",
        unit="gf",
        normal_min=8.0,
        normal_max=12.0,
        warning_min=6.0,
        warning_max=15.0,
        severe_min=4.0,
        severe_max=18.0,
        description="Bond pull test result"
    ),
    "bonding_temperature": ParameterRange(
        name="bonding_temperature",
        unit="°C",
        normal_min=150.0,
        normal_max=180.0,
        warning_min=140.0,
        warning_max=200.0,
        severe_min=130.0,
        severe_max=220.0,
        description="Substrate temperature"
    ),
    "wire_diameter": ParameterRange(
        name="wire_diameter",
        unit="μm",
        normal_min=24.5,
        normal_max=25.5,
        warning_min=24.0,
        warning_max=26.0,
        severe_min=23.0,
        severe_max=27.0,
        description="Gold wire diameter"
    ),
    "bond_time": ParameterRange(
        name="bond_time",
        unit="ms",
        normal_min=15.0,
        normal_max=25.0,
        warning_min=10.0,
        warning_max=30.0,
        severe_min=5.0,
        severe_max=35.0,
        description="Bonding duration"
    ),
}

# ============================================================================
# MOLDING PARAMETERS
# ============================================================================

MOLDING_PARAMS = {
    "mold_temperature": ParameterRange(
        name="mold_temperature",
        unit="°C",
        normal_min=170.0,
        normal_max=180.0,
        warning_min=165.0,
        warning_max=185.0,
        severe_min=160.0,
        severe_max=190.0,
        description="Mold cavity temperature"
    ),
    "mold_pressure": ParameterRange(
        name="mold_pressure",
        unit="MPa",
        normal_min=6.0,
        normal_max=8.0,
        warning_min=5.0,
        warning_max=9.0,
        severe_min=4.0,
        severe_max=10.0,
        description="Injection pressure"
    ),
    "fill_time": ParameterRange(
        name="fill_time",
        unit="sec",
        normal_min=3.0,
        normal_max=5.0,
        warning_min=2.0,
        warning_max=7.0,
        severe_min=1.0,
        severe_max=10.0,
        description="Cavity fill duration"
    ),
    "compound_viscosity": ParameterRange(
        name="compound_viscosity",
        unit="Pa·s",
        normal_min=100.0,
        normal_max=150.0,
        warning_min=80.0,
        warning_max=180.0,
        severe_min=60.0,
        severe_max=200.0,
        description="Compound flow property"
    ),
    "transfer_speed": ParameterRange(
        name="transfer_speed",
        unit="mm/s",
        normal_min=10.0,
        normal_max=15.0,
        warning_min=8.0,
        warning_max=18.0,
        severe_min=6.0,
        severe_max=20.0,
        description="Compound transfer rate"
    ),
    "clamp_force": ParameterRange(
        name="clamp_force",
        unit="kN",
        normal_min=50.0,
        normal_max=70.0,
        warning_min=40.0,
        warning_max=80.0,
        severe_min=30.0,
        severe_max=90.0,
        description="Mold clamping force"
    ),
    "voids_in_mold": ParameterRange(
        name="voids_in_mold",
        unit="%",
        normal_min=0.0,
        normal_max=1.0,
        warning_min=1.0,
        warning_max=2.0,
        severe_min=2.0,
        severe_max=5.0,
        description="Void percentage in compound"
    ),
}

# ============================================================================
# CURING PARAMETERS
# ============================================================================

CURING_PARAMS = {
    "cure_temperature": ParameterRange(
        name="cure_temperature",
        unit="°C",
        normal_min=175.0,
        normal_max=185.0,
        warning_min=170.0,
        warning_max=190.0,
        severe_min=165.0,
        severe_max=195.0,
        description="Oven temperature"
    ),
    "cure_time": ParameterRange(
        name="cure_time",
        unit="min",
        normal_min=120.0,
        normal_max=180.0,
        warning_min=100.0,
        warning_max=210.0,
        severe_min=80.0,
        severe_max=240.0,
        description="Total cure duration"
    ),
    "humidity": ParameterRange(
        name="humidity",
        unit="%",
        normal_min=30.0,
        normal_max=50.0,
        warning_min=20.0,
        warning_max=60.0,
        severe_min=10.0,
        severe_max=70.0,
        description="Ambient humidity"
    ),
    "thermal_profile": ParameterRange(
        name="thermal_profile",
        unit="°C/min",
        normal_min=2.0,
        normal_max=4.0,
        warning_min=1.0,
        warning_max=5.0,
        severe_min=0.5,
        severe_max=6.0,
        description="Temperature ramp rate"
    ),
    "uniformity": ParameterRange(
        name="uniformity",
        unit="°C",
        normal_min=0.0,
        normal_max=2.0,
        warning_min=2.0,
        warning_max=3.0,
        severe_min=3.0,
        severe_max=5.0,
        description="Temperature variation"
    ),
    "oxygen_level": ParameterRange(
        name="oxygen_level",
        unit="%",
        normal_min=0.0,
        normal_max=1.0,
        warning_min=1.0,
        warning_max=2.0,
        severe_min=2.0,
        severe_max=5.0,
        description="Oxygen in oven"
    ),
}

# ============================================================================
# INSPECTION PARAMETERS
# ============================================================================

INSPECTION_PARAMS = {
    "defect_count": ParameterRange(
        name="defect_count",
        unit="count",
        normal_min=0.0,
        normal_max=0.0,
        warning_min=1.0,
        warning_max=2.0,
        severe_min=3.0,
        severe_max=10.0,
        description="Visual defects detected"
    ),
    "visual_score": ParameterRange(
        name="visual_score",
        unit="score",
        normal_min=90.0,
        normal_max=100.0,
        warning_min=80.0,
        warning_max=90.0,
        severe_min=0.0,
        severe_max=80.0,
        description="Overall visual quality"
    ),
    "electrical_test": ParameterRange(
        name="electrical_test",
        unit="pass/fail",
        normal_min=1.0,  # 1 = pass
        normal_max=1.0,
        warning_min=1.0,
        warning_max=1.0,
        severe_min=0.0,  # 0 = fail
        severe_max=0.0,
        description="Electrical continuity"
    ),
    "reliability_score": ParameterRange(
        name="reliability_score",
        unit="score",
        normal_min=95.0,
        normal_max=100.0,
        warning_min=85.0,
        warning_max=95.0,
        severe_min=0.0,
        severe_max=85.0,
        description="Predicted reliability"
    ),
    "dimensional_accuracy": ParameterRange(
        name="dimensional_accuracy",
        unit="μm",
        normal_min=0.0,
        normal_max=20.0,
        warning_min=20.0,
        warning_max=40.0,
        severe_min=40.0,
        severe_max=100.0,
        description="Package dimension error"
    ),
    "lead_coplanarity": ParameterRange(
        name="lead_coplanarity",
        unit="μm",
        normal_min=0.0,
        normal_max=50.0,
        warning_min=50.0,
        warning_max=100.0,
        severe_min=100.0,
        severe_max=200.0,
        description="Lead flatness"
    ),
}

# ============================================================================
# ALL PARAMETERS BY STAGE
# ============================================================================

ALL_PARAMETERS = {
    ProcessStage.DIE_ATTACH: DIE_ATTACH_PARAMS,
    ProcessStage.WIRE_BONDING: WIRE_BONDING_PARAMS,
    ProcessStage.MOLDING: MOLDING_PARAMS,
    ProcessStage.CURING: CURING_PARAMS,
    ProcessStage.INSPECTION: INSPECTION_PARAMS,
}

# ============================================================================
# CRITICAL PARAMETERS (Immediate SEVERE)
# ============================================================================

CRITICAL_PARAMETERS = {
    "void_percentage": 5.0,  # > 5% is critical
    "pull_strength": 6.0,  # < 6gf is critical
    "electrical_test": 0.0,  # 0 (fail) is critical
    "reliability_score": 85.0,  # < 85 is critical
    "voids_in_mold": 2.0,  # > 2% is critical
}

# ============================================================================
# CROSS-STAGE DEPENDENCIES
# ============================================================================

CROSS_STAGE_DEPENDENCIES = {
    "die_attach_to_wire_bonding": {
        "cause_param": "placement_accuracy",
        "effect_param": "bonding_force",
        "threshold": 15.0,
        "description": "Die placement accuracy affects wire bonding alignment",
        "impact": "If placement_accuracy > 15μm, bonding force may need adjustment"
    },
    "die_attach_to_reliability": {
        "cause_param": "void_percentage",
        "effect_param": "reliability_score",
        "threshold": 5.0,
        "description": "Void percentage affects thermal performance",
        "impact": "If void_percentage > 5%, reliability score typically drops below 85"
    },
    "wire_bonding_to_molding": {
        "cause_param": "loop_height",
        "effect_param": "mold_temperature",
        "threshold": 200.0,
        "description": "Loop height affects wire sweep during molding",
        "impact": "If loop_height < 200μm, reduce mold_temperature to prevent wire sweep"
    },
    "molding_to_curing": {
        "cause_param": "voids_in_mold",
        "effect_param": "uniformity",
        "threshold": 2.0,
        "description": "Mold voids affect cure uniformity",
        "impact": "If voids_in_mold > 2%, expect cure uniformity issues"
    },
    "curing_to_reliability": {
        "cause_param": "cure_time",
        "effect_param": "reliability_score",
        "threshold": 120.0,
        "description": "Incomplete cure affects mechanical strength",
        "impact": "If cure_time < 120min, reliability score may be compromised"
    },
}

# ============================================================================
# ISSUE-TO-PARAMETER MAPPING (Bob's Knowledge Base)
# ============================================================================

ISSUE_MAPPING = {
    "die_attach_issue": {
        "primary_parameters": ["temperature", "epoxy_temperature", "void_percentage"],
        "secondary_parameters": ["placement_accuracy", "bond_line_thickness", "pressure"],
        "downstream_impact": ["wire_bonding", "reliability"],
        "typical_causes": [
            "Temperature controller malfunction",
            "Epoxy dispenser clogging",
            "Substrate contamination"
        ],
        "recommendations": [
            "Verify temperature calibration",
            "Check epoxy viscosity and expiration",
            "Inspect substrate cleanliness"
        ]
    },
    "wire_bonding_issue": {
        "primary_parameters": ["bonding_force", "ultrasonic_power", "loop_height"],
        "secondary_parameters": ["pull_strength", "bonding_temperature", "bond_time"],
        "downstream_impact": ["molding", "electrical_test"],
        "typical_causes": [
            "Capillary wear",
            "Ultrasonic generator drift",
            "Bond pad contamination"
        ],
        "recommendations": [
            "Replace capillary if worn",
            "Calibrate ultrasonic power",
            "Verify bond pad cleanliness"
        ]
    },
    "molding_issue": {
        "primary_parameters": ["mold_temperature", "mold_pressure", "compound_viscosity"],
        "secondary_parameters": ["fill_time", "transfer_speed", "voids_in_mold"],
        "downstream_impact": ["curing", "reliability", "visual_quality"],
        "typical_causes": [
            "Compound degradation",
            "Mold contamination",
            "Pressure system leak"
        ],
        "recommendations": [
            "Check compound storage conditions",
            "Clean mold cavity",
            "Inspect pressure system"
        ]
    },
    "curing_issue": {
        "primary_parameters": ["cure_temperature", "cure_time", "humidity"],
        "secondary_parameters": ["thermal_profile", "uniformity", "oxygen_level"],
        "downstream_impact": ["reliability", "mechanical_strength"],
        "typical_causes": [
            "Oven temperature drift",
            "Humidity control failure",
            "Insufficient cure time"
        ],
        "recommendations": [
            "Calibrate oven temperature",
            "Check humidity control system",
            "Extend cure time if needed"
        ]
    },
    "inspection_failure": {
        "primary_parameters": ["defect_count", "electrical_test", "reliability_score"],
        "secondary_parameters": ["visual_score", "dimensional_accuracy"],
        "upstream_causes": ["die_attach", "wire_bonding", "molding", "curing"],
        "typical_causes": [
            "Accumulated defects from earlier stages",
            "Process parameter drift",
            "Material quality issues"
        ],
        "recommendations": [
            "Trace back to root cause stage",
            "Review process control charts",
            "Verify material certifications"
        ]
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_parameter_status(param_name: str, value: float, stage: ProcessStage) -> Status:
    """
    Determine the status of a parameter based on its value
    
    Args:
        param_name: Name of the parameter
        value: Current value
        stage: Process stage
        
    Returns:
        Status enum (GOOD, WARNING, or SEVERE)
    """
    params = ALL_PARAMETERS.get(stage, {})
    param_range = params.get(param_name)
    
    if not param_range:
        return Status.GOOD
    
    # Check if it's a critical parameter
    if param_name in CRITICAL_PARAMETERS:
        threshold = CRITICAL_PARAMETERS[param_name]
        if param_name in ["void_percentage", "voids_in_mold"]:
            if value > threshold:
                return Status.SEVERE
        elif param_name in ["pull_strength", "reliability_score"]:
            if value < threshold:
                return Status.SEVERE
        elif param_name == "electrical_test":
            if value == 0.0:
                return Status.SEVERE
    
    # Check normal range
    if param_range.normal_min <= value <= param_range.normal_max:
        return Status.GOOD
    
    # Check warning range
    if param_range.warning_min <= value <= param_range.warning_max:
        return Status.WARNING
    
    # Otherwise it's severe
    return Status.SEVERE


def classify_overall_status(parameter_statuses: Dict[str, Status]) -> Status:
    """
    Classify overall system status based on individual parameter statuses
    
    Args:
        parameter_statuses: Dictionary of parameter names to their statuses
        
    Returns:
        Overall Status enum
    """
    severe_count = sum(1 for s in parameter_statuses.values() if s == Status.SEVERE)
    warning_count = sum(1 for s in parameter_statuses.values() if s == Status.WARNING)
    
    # Any critical parameter in severe = overall severe
    if severe_count >= 1:
        return Status.SEVERE
    
    # 3+ warnings = overall warning
    if warning_count >= 3:
        return Status.WARNING
    
    # 1-2 warnings = still warning
    if warning_count >= 1:
        return Status.WARNING
    
    return Status.GOOD


def get_all_parameter_names(stage: ProcessStage) -> List[str]:
    """Get all parameter names for a given stage"""
    return list(ALL_PARAMETERS.get(stage, {}).keys())


def get_parameter_range(param_name: str, stage: ProcessStage) -> ParameterRange | None:
    """Get the parameter range definition"""
    return ALL_PARAMETERS.get(stage, {}).get(param_name)


if __name__ == "__main__":
    # Test the configuration
    print("=== AI Packaging Reliability Copilot - Configuration Schema ===\n")
    
    for stage in ProcessStage:
        params = ALL_PARAMETERS.get(stage, {})
        print(f"\n{stage.value.upper()} ({len(params)} parameters):")
        for param_name, param_range in params.items():
            print(f"  - {param_name}: {param_range.normal_min}-{param_range.normal_max} {param_range.unit}")
    
    print(f"\n\nTotal parameters: {sum(len(p) for p in ALL_PARAMETERS.values())}")
    print(f"Critical parameters: {len(CRITICAL_PARAMETERS)}")
    print(f"Cross-stage dependencies: {len(CROSS_STAGE_DEPENDENCIES)}")
    print(f"Issue types: {len(ISSUE_MAPPING)}")

# Made with Bob
