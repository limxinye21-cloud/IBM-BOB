"""
ML API routes for AI Packaging Reliability Copilot
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
import json

from backend.app.db.database import get_db
from backend.app.db import models
from backend.app.schemas.data_schema import ProcessDataCreate
from backend.app.services.ml_service import get_ml_service, MLService
from datetime import datetime

router = APIRouter(prefix="/ml", tags=["ml"])


@router.get("/status")
async def get_ml_status():
    """
    Get ML model status
    
    Returns:
        Model status and information
    """
    ml_service = get_ml_service()
    
    if not ml_service.is_loaded():
        return {
            "status": "not_loaded",
            "message": "ML model not available. Using rule-based classification.",
            "model_info": None
        }
    
    model_info = ml_service.get_model_info()
    return {
        "status": "loaded",
        "message": "ML model loaded and ready",
        "model_info": model_info
    }


@router.post("/predict")
async def predict_status(
    data: ProcessDataCreate,
    db: Session = Depends(get_db)
):
    """
    Predict process status using ML model
    
    Args:
        data: Process data
        db: Database session
        
    Returns:
        Prediction result with status and confidence
    """
    ml_service = get_ml_service()
    
    # Convert Pydantic model to dict
    process_data = data.model_dump()
    
    try:
        # Get prediction
        result = ml_service.predict_status(process_data)
        
        # Store prediction in database
        prediction = models.Prediction(
            batch_id=data.batch_id,
            timestamp=datetime.fromisoformat(data.timestamp) if isinstance(data.timestamp, str) else data.timestamp,
            predicted_status=result['status'],
            confidence=result['confidence'],
            probabilities=json.dumps(result['probabilities'])  # Convert dict to JSON string
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        return {
            "success": True,
            "prediction": result,
            "prediction_id": prediction.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predict/batch")
async def predict_batch(
    data_list: List[ProcessDataCreate],
    db: Session = Depends(get_db)
):
    """
    Predict status for multiple data points
    
    Args:
        data_list: List of process data
        db: Database session
        
    Returns:
        List of prediction results
    """
    ml_service = get_ml_service()
    
    # Convert to list of dicts
    process_data_list = [d.model_dump() for d in data_list]
    
    try:
        # Get predictions
        results = ml_service.predict_batch(process_data_list)
        
        # Store predictions
        predictions = []
        for data, result in zip(data_list, results):
            prediction = models.Prediction(
                batch_id=data.batch_id,
                timestamp=datetime.fromisoformat(data.timestamp) if isinstance(data.timestamp, str) else data.timestamp,
                predicted_status=result['status'],
                confidence=result['confidence'],
                probabilities=json.dumps(result['probabilities'])  # Convert dict to JSON string
            )
            db.add(prediction)
            predictions.append(prediction)
        
        db.commit()
        
        return {
            "success": True,
            "count": len(results),
            "predictions": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.post("/explain")
async def explain_prediction(
    data: ProcessDataCreate,
    top_n: int = 10
):
    """
    Explain prediction with feature contributions
    
    Args:
        data: Process data
        top_n: Number of top features to return
        
    Returns:
        Explanation with top contributing features
    """
    ml_service = get_ml_service()
    
    # Convert to dict
    process_data = data.model_dump()
    
    try:
        explanation = ml_service.explain_prediction(process_data, top_n=top_n)
        
        return {
            "success": True,
            "explanation": explanation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.post("/critical-parameters")
async def get_critical_parameters(
    data: ProcessDataCreate,
    threshold: float = 0.05
):
    """
    Get critical parameters that need attention
    
    Args:
        data: Process data
        threshold: Importance threshold
        
    Returns:
        List of critical parameters
    """
    ml_service = get_ml_service()
    
    # Convert to dict
    process_data = data.model_dump()
    
    try:
        critical = ml_service.get_critical_parameters(process_data, threshold=threshold)
        
        return {
            "success": True,
            "count": len(critical),
            "critical_parameters": critical
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critical parameters analysis failed: {str(e)}")


@router.get("/predictions/recent")
async def get_recent_predictions(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get recent predictions
    
    Args:
        limit: Maximum number of predictions to return
        db: Database session
        
    Returns:
        List of recent predictions
    """
    try:
        predictions = db.query(models.Prediction)\
            .order_by(models.Prediction.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return {
            "success": True,
            "count": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "batch_id": p.batch_id,
                    "timestamp": p.timestamp.isoformat(),
                    "predicted_status": p.predicted_status,
                    "confidence": p.confidence,
                    "probabilities": p.probabilities
                }
                for p in predictions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve predictions: {str(e)}")


@router.get("/predictions/batch/{batch_id}")
async def get_batch_predictions(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Get predictions for a specific batch
    
    Args:
        batch_id: Batch identifier
        db: Database session
        
    Returns:
        List of predictions for the batch
    """
    try:
        predictions = db.query(models.Prediction)\
            .filter(models.Prediction.batch_id == batch_id)\
            .order_by(models.Prediction.timestamp.desc())\
            .all()
        
        if not predictions:
            raise HTTPException(status_code=404, detail=f"No predictions found for batch {batch_id}")
        
        return {
            "success": True,
            "batch_id": batch_id,
            "count": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "timestamp": p.timestamp.isoformat(),
                    "predicted_status": p.predicted_status,
                    "confidence": p.confidence,
                    "probabilities": p.probabilities
                }
                for p in predictions
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve batch predictions: {str(e)}")


@router.get("/statistics")
async def get_prediction_statistics(
    db: Session = Depends(get_db)
):
    """
    Get prediction statistics
    
    Args:
        db: Database session
        
    Returns:
        Statistics about predictions
    """
    try:
        # Total predictions
        total = db.query(models.Prediction).count()
        
        # Status distribution
        from sqlalchemy import func
        status_dist = db.query(
            models.Prediction.predicted_status,
            func.count(models.Prediction.id).label('count')
        ).group_by(models.Prediction.predicted_status).all()
        
        # Average confidence by status
        avg_confidence = db.query(
            models.Prediction.predicted_status,
            func.avg(models.Prediction.confidence).label('avg_confidence')
        ).group_by(models.Prediction.predicted_status).all()
        
        return {
            "success": True,
            "total_predictions": total,
            "status_distribution": {
                status: count for status, count in status_dist
            },
            "average_confidence": {
                status: float(avg_conf) for status, avg_conf in avg_confidence
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@router.delete("/predictions/batch/{batch_id}")
async def delete_batch_predictions(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete predictions for a specific batch
    
    Args:
        batch_id: Batch identifier
        db: Database session
        
    Returns:
        Deletion result
    """
    try:
        deleted = db.query(models.Prediction)\
            .filter(models.Prediction.batch_id == batch_id)\
            .delete()
        
        db.commit()
        
        return {
            "success": True,
            "batch_id": batch_id,
            "deleted_count": deleted
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete predictions: {str(e)}")

# Made with Bob
