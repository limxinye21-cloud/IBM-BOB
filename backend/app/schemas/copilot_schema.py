"""
Pydantic schemas for AI Copilot interactions
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CopilotQuery(BaseModel):
    """Schema for copilot query"""
    
    query: str = Field(..., description="User's natural language query")
    session_id: Optional[str] = Field(None, description="Session identifier for context")
    batch_id: Optional[str] = Field(None, description="Specific batch to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Why is this batch severe?",
                "session_id": "session_123",
                "batch_id": "B202601011234"
            }
        }


class CopilotResponse(BaseModel):
    """Schema for copilot response"""
    
    response: str = Field(..., description="Bob's response")
    context: Optional[dict] = Field(None, description="Relevant context data")
    confidence: Optional[float] = Field(None, description="Confidence score")
    recommendations: Optional[list[str]] = Field(None, description="Action recommendations")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "This batch is severe due to high void percentage (6.2%) in die attach stage...",
                "context": {
                    "abnormal_parameters": ["die_void_percentage", "wire_bonding_force"],
                    "affected_stages": ["die_attach", "wire_bonding"]
                },
                "confidence": 0.92,
                "recommendations": [
                    "Check epoxy dispenser for clogging",
                    "Verify substrate cleanliness",
                    "Calibrate temperature controller"
                ],
                "response_time_ms": 245
            }
        }


class RootCauseRequest(BaseModel):
    """Request for root cause analysis"""
    
    batch_id: str = Field(..., description="Batch to analyze")
    stage: Optional[str] = Field(None, description="Specific stage to focus on")
    
    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "B202601011234",
                "stage": "wire_bonding"
            }
        }


class RootCauseResponse(BaseModel):
    """Response for root cause analysis"""
    
    batch_id: str
    status: str
    primary_issue: str
    abnormal_parameters: list[dict]
    root_cause: str
    downstream_impact: list[str]
    recommendations: list[str]
    confidence: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "B202601011234",
                "status": "SEVERE",
                "primary_issue": "Die attach void formation",
                "abnormal_parameters": [
                    {"name": "die_void_percentage", "value": 6.2, "expected": "0-3%"},
                    {"name": "die_temperature", "value": 195.5, "expected": "180-190°C"}
                ],
                "root_cause": "Temperature controller malfunction causing excessive heating and void formation",
                "downstream_impact": ["Reduced thermal conductivity", "Lower reliability score"],
                "recommendations": [
                    "Verify temperature calibration",
                    "Check epoxy viscosity",
                    "Inspect substrate cleanliness"
                ],
                "confidence": 0.89
            }
        }


class OptimizationRequest(BaseModel):
    """Request for optimization suggestions"""
    
    batch_id: Optional[str] = Field(None, description="Specific batch to optimize")
    stage: Optional[str] = Field(None, description="Specific stage to optimize")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stage": "wire_bonding"
            }
        }


class OptimizationResponse(BaseModel):
    """Response for optimization suggestions"""
    
    current_performance: str
    opportunities: list[dict]
    priority: str
    estimated_impact: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_performance": "WARNING - Intermittent bonding force variations",
                "opportunities": [
                    {
                        "stage": "wire_bonding",
                        "parameter": "bonding_force",
                        "current": 52.3,
                        "recommended": 45.0,
                        "improvement": "Reduce force to prevent wire deformation"
                    }
                ],
                "priority": "MEDIUM",
                "estimated_impact": "15% reduction in bonding defects"
            }
        }


class CopilotInteractionHistory(BaseModel):
    """Schema for copilot interaction history"""
    
    id: int
    session_id: Optional[str]
    user_query: str
    bob_response: str
    response_time_ms: Optional[int]
    feedback_rating: Optional[int]
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Made with Bob
