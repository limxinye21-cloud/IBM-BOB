# AI Packaging Reliability Copilot - Data Schema & Process Intelligence

## Overview

This document defines the complete data schema for semiconductor packaging processes, including parameter definitions, relationships, issue mappings, and the intelligence layer that powers IBM Bob's reasoning capabilities.

---

## 1. Process Stages & Parameters

### 1.1 Die Attach Stage

**Purpose**: Attach semiconductor die to substrate/leadframe

**Critical Parameters**:

| Parameter | Unit | Normal Range | Warning Range | Severe Range | Description |
|-----------|------|--------------|---------------|--------------|-------------|
| `temperature` | °C | 180-190 | 175-180, 190-195 | <175, >195 | Die attach temperature |
| `epoxy_temperature` | °C | 150-160 | 145-150, 160-165 | <145, >165 | Epoxy dispensing temp |
| `void_percentage` | % | 0-3 | 3-5 | >5 | Void area in adhesive |
| `placement_accuracy` | μm | 0-10 | 10-15 | >15 | Die placement precision |
| `bond_line_thickness` | μm | 20-30 | 15-20, 30-35 | <15, >35 | Adhesive thickness |
| `cure_time` | sec | 60-90 | 50-60, 90-120 | <50, >120 | Initial cure duration |
| `pressure` | MPa | 0.5-1.0 | 0.3-0.5, 1.0-1.5 | <0.3, >1.5 | Applied pressure |

**Failure Modes**:
- High void percentage → Poor thermal conductivity → Reliability issues
- Temperature deviation → Incomplete cure → Weak bond
- Poor placement → Electrical connection issues

---

### 1.2 Wire Bonding Stage

**Purpose**: Create electrical connections between die and package

**Critical Parameters**:

| Parameter | Unit | Normal Range | Warning Range | Severe Range | Description |
|-----------|------|--------------|---------------|--------------|-------------|
| `bonding_force` | N | 40-50 | 35-40, 50-55 | <35, >55 | Wire bonding force |
| `ultrasonic_power` | mW | 80-100 | 70-80, 100-110 | <70, >110 | Ultrasonic energy |
| `loop_height` | μm | 200-250 | 180-200, 250-280 | <180, >280 | Wire loop height |
| `pull_strength` | gf | 8-12 | 6-8, 12-15 | <6, >15 | Bond pull test result |
| `bonding_temperature` | °C | 150-180 | 140-150, 180-200 | <140, >200 | Substrate temperature |
| `wire_diameter` | μm | 25 | 24-26 | <24, >26 | Gold wire diameter |
| `bond_time` | ms | 15-25 | 10-15, 25-30 | <10, >30 | Bonding duration |

**Failure Modes**:
- Excessive force → Wire deformation → Short circuits
- Low ultrasonic power → Weak bonds → Open circuits
- Improper loop height → Wire sweep during molding

---

### 1.3 Molding Stage

**Purpose**: Encapsulate die and wires in protective compound

**Critical Parameters**:

| Parameter | Unit | Normal Range | Warning Range | Severe Range | Description |
|-----------|------|--------------|---------------|--------------|-------------|
| `mold_temperature` | °C | 170-180 | 165-170, 180-185 | <165, >185 | Mold cavity temperature |
| `mold_pressure` | MPa | 6-8 | 5-6, 8-9 | <5, >9 | Injection pressure |
| `fill_time` | sec | 3-5 | 2-3, 5-7 | <2, >7 | Cavity fill duration |
| `compound_viscosity` | Pa·s | 100-150 | 80-100, 150-180 | <80, >180 | Compound flow property |
| `transfer_speed` | mm/s | 10-15 | 8-10, 15-18 | <8, >18 | Compound transfer rate |
| `clamp_force` | kN | 50-70 | 40-50, 70-80 | <40, >80 | Mold clamping force |
| `voids_in_mold` | % | 0-1 | 1-2 | >2 | Void percentage in compound |

**Failure Modes**:
- High temperature → Wire sweep → Electrical shorts
- Low pressure → Incomplete fill → Voids
- High viscosity → Poor flow → Delamination

---

### 1.4 Curing Stage

**Purpose**: Complete polymerization of molding compound

**Critical Parameters**:

| Parameter | Unit | Normal Range | Warning Range | Severe Range | Description |
|-----------|------|--------------|---------------|--------------|-------------|
| `cure_temperature` | °C | 175-185 | 170-175, 185-190 | <170, >190 | Oven temperature |
| `cure_time` | min | 120-180 | 100-120, 180-210 | <100, >210 | Total cure duration |
| `humidity` | % | 30-50 | 20-30, 50-60 | <20, >60 | Ambient humidity |
| `thermal_profile` | °C/min | 2-4 | 1-2, 4-5 | <1, >5 | Temperature ramp rate |
| `uniformity` | °C | ±2 | ±3 | >±3 | Temperature variation |
| `oxygen_level` | % | <1 | 1-2 | >2 | Oxygen in oven |

**Failure Modes**:
- Insufficient cure → Weak mechanical properties
- High humidity → Moisture absorption → Popcorn effect
- Non-uniform heating → Internal stress → Cracks

---

### 1.5 Inspection Stage

**Purpose**: Verify package quality and reliability

**Critical Parameters**:

| Parameter | Unit | Normal Range | Warning Range | Severe Range | Description |
|-----------|------|--------------|---------------|--------------|-------------|
| `defect_count` | count | 0 | 1-2 | >2 | Visual defects detected |
| `visual_score` | score | 90-100 | 80-90 | <80 | Overall visual quality |
| `electrical_test` | pass/fail | pass | - | fail | Electrical continuity |
| `reliability_score` | score | 95-100 | 85-95 | <85 | Predicted reliability |
| `dimensional_accuracy` | μm | 0-20 | 20-40 | >40 | Package dimension error |
| `lead_coplanarity` | μm | 0-50 | 50-100 | >100 | Lead flatness |

**Failure Modes**:
- Visual defects → Cosmetic rejection
- Electrical failure → Functional rejection
- Dimensional issues → Assembly problems

---

## 2. Database Schema (SQLite)

### 2.1 Core Tables

#### Table: `process_data`
```sql
CREATE TABLE process_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    machine_id VARCHAR(50),
    process_stage VARCHAR(50) NOT NULL,
    status VARCHAR(20),
    
    -- Die Attach Parameters
    die_temperature REAL,
    die_epoxy_temperature REAL,
    die_void_percentage REAL,
    die_placement_accuracy REAL,
    die_bond_line_thickness REAL,
    die_cure_time REAL,
    die_pressure REAL,
    
    -- Wire Bonding Parameters
    wire_bonding_force REAL,
    wire_ultrasonic_power REAL,
    wire_loop_height REAL,
    wire_pull_strength REAL,
    wire_bonding_temperature REAL,
    wire_diameter REAL,
    wire_bond_time REAL,
    
    -- Molding Parameters
    mold_temperature REAL,
    mold_pressure REAL,
    mold_fill_time REAL,
    mold_compound_viscosity REAL,
    mold_transfer_speed REAL,
    mold_clamp_force REAL,
    mold_voids REAL,
    
    -- Curing Parameters
    cure_temperature REAL,
    cure_time REAL,
    cure_humidity REAL,
    cure_thermal_profile REAL,
    cure_uniformity REAL,
    cure_oxygen_level REAL,
    
    -- Inspection Parameters
    inspect_defect_count INTEGER,
    inspect_visual_score REAL,
    inspect_electrical_test VARCHAR(10),
    inspect_reliability_score REAL,
    inspect_dimensional_accuracy REAL,
    inspect_lead_coplanarity REAL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_batch_id (batch_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (status),
    INDEX idx_stage (process_stage)
);
```

#### Table: `predictions`
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    predicted_status VARCHAR(20) NOT NULL,
    confidence REAL,
    feature_importance TEXT, -- JSON string
    model_version VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (batch_id) REFERENCES process_data(batch_id),
    INDEX idx_batch_prediction (batch_id),
    INDEX idx_status_prediction (predicted_status)
);
```

#### Table: `alert_history`
```sql
CREATE TABLE alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    severity VARCHAR(20) NOT NULL,
    stage VARCHAR(50),
    message TEXT,
    explanation TEXT, -- Bob-generated explanation
    recommendations TEXT, -- Bob-generated recommendations
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    resolved_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (batch_id) REFERENCES process_data(batch_id),
    INDEX idx_batch_alert (batch_id),
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved)
);
```

#### Table: `model_metadata`
```sql
CREATE TABLE model_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50),
    trained_at DATETIME NOT NULL,
    accuracy REAL,
    precision_score REAL,
    recall_score REAL,
    f1_score REAL,
    training_samples INTEGER,
    feature_count INTEGER,
    hyperparameters TEXT, -- JSON string
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `copilot_interactions`
```sql
CREATE TABLE copilot_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(50),
    user_query TEXT NOT NULL,
    bob_response TEXT NOT NULL,
    context TEXT, -- JSON string with relevant data
    response_time_ms INTEGER,
    feedback_rating INTEGER, -- 1-5 stars
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_session (session_id),
    INDEX idx_timestamp_interaction (timestamp)
);
```

---

## 3. Issue-to-Parameter Mapping (Bob's Knowledge Base)

### 3.1 Issue Mapping Dictionary

```python
ISSUE_PARAMETER_MAPPING = {
    "die_attach_issue": {
        "primary_parameters": [
            "die_temperature",
            "die_epoxy_temperature",
            "die_void_percentage"
        ],
        "secondary_parameters": [
            "die_placement_accuracy",
            "die_bond_line_thickness",
            "die_pressure"
        ],
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
        "primary_parameters": [
            "wire_bonding_force",
            "wire_ultrasonic_power",
            "wire_loop_height"
        ],
        "secondary_parameters": [
            "wire_pull_strength",
            "wire_bonding_temperature",
            "wire_bond_time"
        ],
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
        "primary_parameters": [
            "mold_temperature",
            "mold_pressure",
            "mold_compound_viscosity"
        ],
        "secondary_parameters": [
            "mold_fill_time",
            "mold_transfer_speed",
            "mold_voids"
        ],
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
        "primary_parameters": [
            "cure_temperature",
            "cure_time",
            "cure_humidity"
        ],
        "secondary_parameters": [
            "cure_thermal_profile",
            "cure_uniformity",
            "cure_oxygen_level"
        ],
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
        "primary_parameters": [
            "inspect_defect_count",
            "inspect_electrical_test",
            "inspect_reliability_score"
        ],
        "secondary_parameters": [
            "inspect_visual_score",
            "inspect_dimensional_accuracy"
        ],
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
    }
}
```

### 3.2 Cross-Stage Dependencies

```python
CROSS_STAGE_DEPENDENCIES = {
    "die_attach → wire_bonding": {
        "dependency": "Die placement accuracy affects wire bonding alignment",
        "parameters": {
            "cause": "die_placement_accuracy",
            "effect": "wire_bonding_force"
        },
        "threshold": "If die_placement_accuracy > 15μm, wire bonding may require force adjustment"
    },
    
    "die_attach → reliability": {
        "dependency": "Void percentage affects thermal performance",
        "parameters": {
            "cause": "die_void_percentage",
            "effect": "inspect_reliability_score"
        },
        "threshold": "If die_void_percentage > 5%, reliability score typically drops below 85"
    },
    
    "wire_bonding → molding": {
        "dependency": "Loop height affects wire sweep during molding",
        "parameters": {
            "cause": "wire_loop_height",
            "effect": "mold_temperature"
        },
        "threshold": "If wire_loop_height < 200μm, reduce mold_temperature to prevent wire sweep"
    },
    
    "molding → curing": {
        "dependency": "Mold voids affect cure uniformity",
        "parameters": {
            "cause": "mold_voids",
            "effect": "cure_uniformity"
        },
        "threshold": "If mold_voids > 2%, expect cure_uniformity issues"
    },
    
    "curing → reliability": {
        "dependency": "Incomplete cure affects mechanical strength",
        "parameters": {
            "cause": "cure_time",
            "effect": "inspect_reliability_score"
        },
        "threshold": "If cure_time < 120min, reliability score may be compromised"
    }
}
```

---

## 4. Classification Rules

### 4.1 Status Classification Logic

```python
def classify_status(parameters: dict) -> str:
    """
    Classify system status based on parameter values
    
    Returns: "GOOD", "WARNING", or "SEVERE"
    """
    severe_count = 0
    warning_count = 0
    
    # Check each parameter against thresholds
    for param, value in parameters.items():
        if is_severe(param, value):
            severe_count += 1
        elif is_warning(param, value):
            warning_count += 1
    
    # Classification logic
    if severe_count >= 3:
        return "SEVERE"
    elif severe_count >= 1:
        return "SEVERE"  # Any critical parameter in severe range
    elif warning_count >= 3:
        return "WARNING"
    elif warning_count >= 1:
        return "WARNING"
    else:
        return "GOOD"
```

### 4.2 Critical Parameters (Immediate SEVERE)

Parameters that trigger immediate SEVERE status:
- `die_void_percentage > 5%`
- `wire_pull_strength < 6gf`
- `inspect_electrical_test = "fail"`
- `inspect_reliability_score < 85`
- `mold_voids > 2%`

---

## 5. Feature Engineering for ML

### 5.1 Engineered Features

```python
ENGINEERED_FEATURES = {
    # Statistical features
    "temperature_variance": "Variance across all temperature parameters",
    "pressure_ratio": "mold_pressure / die_pressure",
    "time_efficiency": "actual_time / expected_time",
    
    # Cross-stage features
    "thermal_consistency": "Consistency of temperature across stages",
    "process_stability": "Standard deviation of key parameters",
    
    # Rolling features (time-series)
    "temp_rolling_mean_5": "5-sample rolling mean of temperatures",
    "pressure_rolling_std_5": "5-sample rolling std of pressures",
    
    # Interaction features
    "temp_pressure_interaction": "temperature * pressure",
    "void_reliability_score": "void_percentage * (100 - reliability_score)"
}
```

### 5.2 Feature Importance Tracking

Track which features contribute most to predictions for Bob's explanations.

---

## 6. Bob's Reasoning Templates

### 6.1 Root Cause Analysis Template

```python
ROOT_CAUSE_TEMPLATE = """
Based on analysis of batch {batch_id}:

**Status**: {status}
**Primary Issue**: {primary_issue}

**Abnormal Parameters**:
{abnormal_parameters_list}

**Root Cause**:
{root_cause_explanation}

**Impact**:
{downstream_impact}

**Recommended Actions**:
{recommendations_list}

**Confidence**: {confidence_level}%
"""
```

### 6.2 Optimization Template

```python
OPTIMIZATION_TEMPLATE = """
**Current Performance**: {current_status}

**Optimization Opportunities**:

1. **{stage_1}**:
   - Current: {current_value_1}
   - Recommended: {recommended_value_1}
   - Expected Improvement: {improvement_1}

2. **{stage_2}**:
   - Current: {current_value_2}
   - Recommended: {recommended_value_2}
   - Expected Improvement: {improvement_2}

**Priority**: {priority_level}
**Estimated Impact**: {estimated_impact}
"""
```

---

## 7. Data Validation Rules

### 7.1 Parameter Validation

```python
VALIDATION_RULES = {
    "die_temperature": {
        "type": "float",
        "min": 150,
        "max": 200,
        "required": True
    },
    "wire_bonding_force": {
        "type": "float",
        "min": 20,
        "max": 70,
        "required": True
    },
    # ... (all parameters)
}
```

### 7.2 Batch Validation

- Batch ID format: `B{YYYYMMDD}{sequence}`
- Timestamp must be sequential
- All required parameters must be present
- Values must be within physical limits

---

## 8. Summary

### Key Components Defined

✅ **5 Process Stages** with 35+ parameters
✅ **Database Schema** with 5 core tables
✅ **Issue Mapping** for Bob's knowledge base
✅ **Cross-Stage Dependencies** for reasoning
✅ **Classification Rules** for status determination
✅ **Feature Engineering** for ML model
✅ **Reasoning Templates** for Bob's responses
✅ **Validation Rules** for data quality

### Next Steps

This schema will be used to:
1. Generate mock data (STEP 3)
2. Build database models (STEP 4)
3. Train ML classifier (STEP 5)
4. Power Bob's reasoning (STEP 7)

---

**STEP 2 STATUS**: ✅ COMPLETE
**Ready for**: STEP 3 - Mock Data Generator Implementation