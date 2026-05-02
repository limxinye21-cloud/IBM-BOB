"""
SQLAlchemy database models for AI Packaging Reliability Copilot
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime

from backend.app.db.database import Base


class ProcessData(Base):
    """Process data table - stores all manufacturing parameters"""
    
    __tablename__ = "process_data"
    
    # Primary key and metadata
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    machine_id = Column(String(50))
    process_stage = Column(String(50), nullable=False, index=True)
    status = Column(String(20), index=True)
    
    # Die Attach Parameters
    die_temperature = Column(Float)
    die_epoxy_temperature = Column(Float)
    die_void_percentage = Column(Float)
    die_placement_accuracy = Column(Float)
    die_bond_line_thickness = Column(Float)
    die_cure_time = Column(Float)
    die_pressure = Column(Float)
    
    # Wire Bonding Parameters
    wire_bonding_force = Column(Float)
    wire_ultrasonic_power = Column(Float)
    wire_loop_height = Column(Float)
    wire_pull_strength = Column(Float)
    wire_bonding_temperature = Column(Float)
    wire_diameter = Column(Float)
    wire_bond_time = Column(Float)
    
    # Molding Parameters
    mold_temperature = Column(Float)
    mold_pressure = Column(Float)
    mold_fill_time = Column(Float)
    mold_compound_viscosity = Column(Float)
    mold_transfer_speed = Column(Float)
    mold_clamp_force = Column(Float)
    mold_voids = Column(Float)
    
    # Curing Parameters
    cure_temperature = Column(Float)
    cure_time = Column(Float)
    cure_humidity = Column(Float)
    cure_thermal_profile = Column(Float)
    cure_uniformity = Column(Float)
    cure_oxygen_level = Column(Float)
    
    # Inspection Parameters
    inspect_defect_count = Column(Integer)
    inspect_visual_score = Column(Float)
    inspect_electrical_test = Column(Integer)  # 1=pass, 0=fail
    inspect_reliability_score = Column(Float)
    inspect_dimensional_accuracy = Column(Float)
    inspect_lead_coplanarity = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ProcessData(batch_id='{self.batch_id}', status='{self.status}', timestamp='{self.timestamp}')>"


class Prediction(Base):
    """ML model predictions table"""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    predicted_status = Column(String(20), nullable=False, index=True)
    confidence = Column(Float)
    feature_importance = Column(Text)  # JSON string
    model_version = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Prediction(batch_id='{self.batch_id}', status='{self.predicted_status}', confidence={self.confidence})>"


class AlertHistory(Base):
    """Alert history table"""
    
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    stage = Column(String(50))
    message = Column(Text)
    explanation = Column(Text)  # Bob-generated explanation
    recommendations = Column(Text)  # Bob-generated recommendations
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<AlertHistory(batch_id='{self.batch_id}', severity='{self.severity}', resolved={self.resolved})>"


class ModelMetadata(Base):
    """ML model metadata table"""
    
    __tablename__ = "model_metadata"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_version = Column(String(20), nullable=False)
    model_type = Column(String(50))
    trained_at = Column(DateTime, nullable=False)
    accuracy = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    training_samples = Column(Integer)
    feature_count = Column(Integer)
    hyperparameters = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ModelMetadata(version='{self.model_version}', accuracy={self.accuracy})>"


class CopilotInteraction(Base):
    """Copilot interaction history table"""
    
    __tablename__ = "copilot_interactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(50), index=True)
    user_query = Column(Text, nullable=False)
    bob_response = Column(Text, nullable=False)
    context = Column(Text)  # JSON string with relevant data
    response_time_ms = Column(Integer)
    feedback_rating = Column(Integer)  # 1-5 stars
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    def __repr__(self):
        return f"<CopilotInteraction(session='{self.session_id}', rating={self.feedback_rating})>"

# Made with Bob
