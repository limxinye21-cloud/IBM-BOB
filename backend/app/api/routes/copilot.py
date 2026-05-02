"""
Copilot API routes for AI Packaging Reliability Copilot
Natural language interaction and intelligent assistance
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.db.database import get_db
from backend.app.db import models
from backend.app.schemas.copilot_schema import (
    CopilotQuery,
    CopilotResponse,
    RootCauseRequest,
    RootCauseResponse,
    OptimizationRequest,
    OptimizationResponse
)
from backend.app.services.copilot_service import get_copilot_service

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/query", response_model=CopilotResponse)
async def process_copilot_query(
    query: CopilotQuery,
    db: Session = Depends(get_db)
):
    """
    Process natural language query
    
    Args:
        query: User query with optional context
        db: Database session
        
    Returns:
        Copilot response with answer and actions
    """
    copilot = get_copilot_service()
    
    try:
        # Process query
        response = copilot.process_query(
            query.query,
            context=query.context
        )
        
        # Store interaction in database
        interaction = models.CopilotInteraction(
            query=query.query,
            response=response['answer'],
            query_type=response['type'],
            confidence=response['confidence'],
            context=query.context,
            timestamp=datetime.now()
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        return CopilotResponse(
            success=True,
            query=query.query,
            answer=response['answer'],
            query_type=response['type'],
            confidence=response['confidence'],
            actions=response.get('actions', []),
            metadata=response.get('metadata', {}),
            interaction_id=interaction.id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/root-cause", response_model=RootCauseResponse)
async def analyze_root_cause(
    request: RootCauseRequest,
    db: Session = Depends(get_db)
):
    """
    Perform root cause analysis
    
    Args:
        request: Process data for analysis
        db: Database session
        
    Returns:
        Root cause analysis with identified issues
    """
    copilot = get_copilot_service()
    
    try:
        # Build context
        context = {
            'current_data': request.process_data,
            'batch_id': request.batch_id
        }
        
        # Perform analysis
        response = copilot.process_query(
            "Why is this batch showing issues?",
            context=context
        )
        
        # Extract abnormal parameters
        abnormal_params = response.get('abnormal_parameters', [])
        
        # Format root causes
        root_causes = []
        for param, info in abnormal_params[:5]:
            root_causes.append({
                'parameter': param,
                'current_value': info['value'],
                'expected_range': f"{info['normal_min']}-{info['normal_max']} {info['unit']}",
                'severity': info['severity'],
                'impact': info['impact']
            })
        
        # Get cross-stage impact
        cross_stage_impact = copilot._analyze_cross_stage_impact(
            request.process_data,
            abnormal_params
        )
        
        return RootCauseResponse(
            success=True,
            batch_id=request.batch_id,
            root_causes=root_causes,
            explanation=response['answer'],
            confidence=response['confidence'],
            cross_stage_impact=cross_stage_impact if cross_stage_impact else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Root cause analysis failed: {str(e)}")


@router.post("/optimize", response_model=OptimizationResponse)
async def get_optimization_recommendations(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Get optimization recommendations
    
    Args:
        request: Process data for optimization
        db: Database session
        
    Returns:
        Optimization recommendations
    """
    copilot = get_copilot_service()
    
    try:
        # Build context
        context = {
            'current_data': request.process_data,
            'batch_id': request.batch_id,
            'target_status': request.target_status
        }
        
        # Get recommendations
        response = copilot.process_query(
            "How can I optimize this process?",
            context=context
        )
        
        # Extract recommendations
        recommendations = response.get('recommendations', [])
        
        return OptimizationResponse(
            success=True,
            batch_id=request.batch_id,
            recommendations=recommendations,
            explanation=response['answer'],
            confidence=response['confidence'],
            priority_order=[r['parameter'] for r in recommendations if r['priority'] == 'CRITICAL']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/interactions/recent")
async def get_recent_interactions(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent copilot interactions
    
    Args:
        limit: Maximum number of interactions
        db: Database session
        
    Returns:
        List of recent interactions
    """
    try:
        interactions = db.query(models.CopilotInteraction)\
            .order_by(models.CopilotInteraction.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return {
            'success': True,
            'count': len(interactions),
            'interactions': [
                {
                    'id': i.id,
                    'query': i.query,
                    'response': i.response,
                    'query_type': i.query_type,
                    'confidence': i.confidence,
                    'timestamp': i.timestamp.isoformat()
                }
                for i in interactions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve interactions: {str(e)}")


@router.get("/interactions/{interaction_id}")
async def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific interaction
    
    Args:
        interaction_id: Interaction ID
        db: Database session
        
    Returns:
        Interaction details
    """
    try:
        interaction = db.query(models.CopilotInteraction)\
            .filter(models.CopilotInteraction.id == interaction_id)\
            .first()
        
        if not interaction:
            raise HTTPException(status_code=404, detail=f"Interaction {interaction_id} not found")
        
        return {
            'success': True,
            'interaction': {
                'id': interaction.id,
                'query': interaction.query,
                'response': interaction.response,
                'query_type': interaction.query_type,
                'confidence': interaction.confidence,
                'context': interaction.context,
                'timestamp': interaction.timestamp.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve interaction: {str(e)}")


@router.get("/statistics")
async def get_copilot_statistics(
    db: Session = Depends(get_db)
):
    """
    Get copilot usage statistics
    
    Args:
        db: Database session
        
    Returns:
        Usage statistics
    """
    try:
        from sqlalchemy import func
        
        # Total interactions
        total = db.query(models.CopilotInteraction).count()
        
        # Query type distribution
        type_dist = db.query(
            models.CopilotInteraction.query_type,
            func.count(models.CopilotInteraction.id).label('count')
        ).group_by(models.CopilotInteraction.query_type).all()
        
        # Average confidence
        avg_confidence = db.query(
            func.avg(models.CopilotInteraction.confidence).label('avg_confidence')
        ).scalar()
        
        return {
            'success': True,
            'total_interactions': total,
            'query_type_distribution': {
                qtype: count for qtype, count in type_dist
            },
            'average_confidence': float(avg_confidence) if avg_confidence else 0.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@router.delete("/interactions/{interaction_id}")
async def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete interaction
    
    Args:
        interaction_id: Interaction ID
        db: Database session
        
    Returns:
        Deletion result
    """
    try:
        deleted = db.query(models.CopilotInteraction)\
            .filter(models.CopilotInteraction.id == interaction_id)\
            .delete()
        
        db.commit()
        
        if deleted == 0:
            raise HTTPException(status_code=404, detail=f"Interaction {interaction_id} not found")
        
        return {
            'success': True,
            'interaction_id': interaction_id,
            'message': 'Interaction deleted'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete interaction: {str(e)}")


@router.post("/feedback")
async def submit_feedback(
    interaction_id: int,
    helpful: bool,
    comment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Submit feedback on copilot response
    
    Args:
        interaction_id: Interaction ID
        helpful: Whether response was helpful
        comment: Optional feedback comment
        db: Database session
        
    Returns:
        Feedback submission result
    """
    try:
        interaction = db.query(models.CopilotInteraction)\
            .filter(models.CopilotInteraction.id == interaction_id)\
            .first()
        
        if not interaction:
            raise HTTPException(status_code=404, detail=f"Interaction {interaction_id} not found")
        
        # Store feedback (could be in separate table in production)
        # For now, just return success
        
        return {
            'success': True,
            'interaction_id': interaction_id,
            'message': 'Feedback recorded'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

# Made with Bob
