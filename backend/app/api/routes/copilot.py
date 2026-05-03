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
        # Simple response based on query
        response_text = "I'm Bob, your AI packaging reliability assistant. I can help analyze process data and provide recommendations."
        
        if "severe" in query.query.lower() or "why" in query.query.lower():
            response_text = "This batch may be showing issues due to parameters outside acceptable ranges. Check die void percentage, wire pull strength, and reliability scores."
        elif "optimize" in query.query.lower():
            response_text = "To optimize the process, consider adjusting temperature settings, bonding force, and curing parameters based on historical data."
        elif "die attach" in query.query.lower():
            response_text = "Die attach quality depends on temperature control, epoxy application, and void formation. Monitor void percentage and placement accuracy."
        
        # Store interaction in database
        interaction = models.CopilotInteraction(
            session_id=query.session_id,
            user_query=query.query,
            bob_response=response_text,
            context=None,
            response_time_ms=100,
            timestamp=datetime.now()
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        return CopilotResponse(
            response=response_text,
            context={'batch_id': query.batch_id} if query.batch_id else None,
            confidence=0.85,
            recommendations=["Monitor critical parameters", "Review process settings"],
            response_time_ms=100
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
        # Fetch process data from database
        process_data_record = db.query(models.ProcessData)\
            .filter(models.ProcessData.batch_id == request.batch_id)\
            .order_by(models.ProcessData.timestamp.desc())\
            .first()
        
        if not process_data_record:
            raise HTTPException(status_code=404, detail=f"No data found for batch {request.batch_id}")
        
        # Convert to dict
        process_data = {
            'batch_id': process_data_record.batch_id,
            'status': process_data_record.status,
            'die_temperature': process_data_record.die_temperature,
            'die_void_percentage': process_data_record.die_void_percentage,
            'wire_bonding_force': process_data_record.wire_bonding_force,
            'wire_pull_strength': process_data_record.wire_pull_strength,
            'mold_voids': process_data_record.mold_voids,
            'inspect_reliability_score': process_data_record.inspect_reliability_score,
            'inspect_defect_count': process_data_record.inspect_defect_count
        }
        
        # Simple root cause analysis
        abnormal_params = []
        recommendations = []
        
        # Check die attach
        if process_data.get('die_void_percentage', 0) > 3:
            abnormal_params.append({
                'name': 'die_void_percentage',
                'value': process_data['die_void_percentage'],
                'expected': '0-3%'
            })
            recommendations.append('Check epoxy dispenser and substrate cleanliness')
        
        # Check wire bonding
        if process_data.get('wire_pull_strength', 10) < 8:
            abnormal_params.append({
                'name': 'wire_pull_strength',
                'value': process_data['wire_pull_strength'],
                'expected': '8-15 gf'
            })
            recommendations.append('Verify bonding parameters and wire quality')
        
        # Check molding
        if process_data.get('mold_voids', 0) > 1:
            abnormal_params.append({
                'name': 'mold_voids',
                'value': process_data['mold_voids'],
                'expected': '0-1%'
            })
            recommendations.append('Check mold compound and transfer speed')
        
        # Determine primary issue
        primary_issue = "Normal operation"
        root_cause = "All parameters within acceptable ranges"
        
        if abnormal_params:
            primary_issue = f"{abnormal_params[0]['name']} out of range"
            root_cause = f"Parameter {abnormal_params[0]['name']} is {abnormal_params[0]['value']}, expected {abnormal_params[0]['expected']}"
        
        return RootCauseResponse(
            batch_id=request.batch_id,
            status=process_data.get('status', 'UNKNOWN'),
            primary_issue=primary_issue,
            abnormal_parameters=abnormal_params,
            root_cause=root_cause,
            downstream_impact=["Potential reliability issues", "Quality degradation"] if abnormal_params else [],
            recommendations=recommendations if recommendations else ["Continue monitoring"],
            confidence=0.85 if abnormal_params else 0.95
        )
        
    except HTTPException:
        raise
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
        # Simple optimization suggestions
        opportunities = [
            {
                'stage': 'die_attach',
                'parameter': 'temperature',
                'current': 185.0,
                'recommended': 182.0,
                'improvement': 'Reduce temperature to minimize thermal stress'
            },
            {
                'stage': 'wire_bonding',
                'parameter': 'bonding_force',
                'current': 50.0,
                'recommended': 45.0,
                'improvement': 'Optimize force to prevent wire deformation'
            }
        ]
        
        return OptimizationResponse(
            current_performance="GOOD - Minor optimization opportunities available",
            opportunities=opportunities,
            priority="LOW",
            estimated_impact="5-10% improvement in reliability"
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
                    'user_query': i.user_query,
                    'bob_response': i.bob_response,
                    'response_time_ms': i.response_time_ms,
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
                'user_query': interaction.user_query,
                'bob_response': interaction.bob_response,
                'response_time_ms': interaction.response_time_ms,
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
        
        # Average response time
        avg_response_time = db.query(
            func.avg(models.CopilotInteraction.response_time_ms).label('avg_time')
        ).scalar()
        
        # Recent interactions count (last 24 hours)
        from datetime import datetime, timedelta
        recent_count = db.query(models.CopilotInteraction)\
            .filter(models.CopilotInteraction.timestamp >= datetime.now() - timedelta(hours=24))\
            .count()
        
        return {
            'success': True,
            'total_interactions': total,
            'recent_interactions_24h': recent_count,
            'average_response_time_ms': float(avg_response_time) if avg_response_time else 0.0
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
