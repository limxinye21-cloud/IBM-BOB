"""
Pydantic schemas for process data
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProcessDataBase(BaseModel):
    """Base schema for process data"""
    
    batch_id: str = Field(..., description="Batch identifier")
    timestamp: datetime = Field(..., description="Data timestamp")
    machine_id: Optional[str] = Field(None, description="Machine identifier")
    process_stage: str = Field(..., description="Process stage")
    status: str = Field(..., description="Status (GOOD/WARNING/SEVERE)")
    
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
    inspect_electrical_test: int
    inspect_reliability_score: float
    inspect_dimensional_accuracy: float
    inspect_lead_coplanarity: float


class ProcessDataCreate(ProcessDataBase):
    """Schema for creating process data"""
    pass


class ProcessDataResponse(ProcessDataBase):
    """Schema for process data response"""
    
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProcessDataBatch(BaseModel):
    """Schema for batch of process data"""
    
    data: list[ProcessDataCreate]
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "batch_id": "B202601011234",
                        "timestamp": "2026-01-01T10:00:00",
                        "machine_id": "PKG-LINE-01",
                        "process_stage": "all_stages",
                        "status": "GOOD",
                        # ... other parameters
                    }
                ]
            }
        }


class StatusSummary(BaseModel):
    """Summary of system status"""
    
    current_status: str
    batch_id: str
    timestamp: datetime
    total_parameters: int
    abnormal_parameters: int
    critical_issues: list[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_status": "GOOD",
                "batch_id": "B202601011234",
                "timestamp": "2026-01-01T10:00:00",
                "total_parameters": 33,
                "abnormal_parameters": 0,
                "critical_issues": []
            }
        }


class HistoricalQuery(BaseModel):
    """Query parameters for historical data"""
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    batch_id: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_time": "2026-01-01T00:00:00",
                "end_time": "2026-01-01T23:59:59",
                "status": "SEVERE",
                "limit": 100,
                "offset": 0
            }
        }


class HistoricalResponse(BaseModel):
    """Response for historical data query"""
    
    total: int
    data: list[ProcessDataResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "data": []
            }
        }

# Made with Bob
