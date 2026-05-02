"""
Alert API routes for AI Packaging Reliability Copilot
Automated alerting and notification system
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.app.db.database import get_db
from backend.app.db import models
from backend.app.schemas.data_schema import ProcessDataCreate
from backend.app.services.alert_service import get_alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/check")
async def check_alerts(
    data: ProcessDataCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Check for alert conditions in process data
    
    Args:
        data: Process data to check
        background_tasks: Background task manager
        db: Database session
        
    Returns:
        List of triggered alerts
    """
    alert_service = get_alert_service()
    
    try:
        # Convert to dict
        process_data = data.model_dump()
        
        # Check for alerts
        alerts = alert_service.check_alerts(process_data)
        
        if alerts:
            # Store alerts in database
            for alert in alerts:
                db_alert = models.AlertHistory(
                    alert_id=alert['alert_id'],
                    batch_id=alert['batch_id'],
                    machine_id=alert['machine_id'],
                    timestamp=datetime.fromisoformat(alert['timestamp']),
                    severity=alert['severity'],
                    alert_type=alert['type'],
                    title=alert['title'],
                    message=alert_service.generate_alert_message(alert),
                    status='active',
                    acknowledged=False
                )
                db.add(db_alert)
            
            db.commit()
            
            # Send notifications in background
            for alert in alerts:
                background_tasks.add_task(
                    send_alert_notification,
                    alert=alert,
                    recipients=['engineer@example.com'],
                    channels=['dashboard', 'email']
                )
        
        return {
            'success': True,
            'alerts_triggered': len(alerts),
            'alerts': alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert check failed: {str(e)}")


@router.get("/active")
async def get_active_alerts(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get active alerts
    
    Args:
        limit: Maximum number of alerts
        db: Database session
        
    Returns:
        List of active alerts
    """
    try:
        alerts = db.query(models.AlertHistory)\
            .filter(models.AlertHistory.status == 'active')\
            .order_by(models.AlertHistory.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return {
            'success': True,
            'count': len(alerts),
            'alerts': [
                {
                    'id': a.id,
                    'alert_id': a.alert_id,
                    'batch_id': a.batch_id,
                    'machine_id': a.machine_id,
                    'timestamp': a.timestamp.isoformat(),
                    'severity': a.severity,
                    'type': a.alert_type,
                    'title': a.title,
                    'acknowledged': a.acknowledged,
                    'resolved': a.resolved
                }
                for a in alerts
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@router.get("/history")
async def get_alert_history(
    hours: int = 24,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get alert history
    
    Args:
        hours: Number of hours to retrieve
        severity: Filter by severity (INFO, WARNING, CRITICAL)
        db: Database session
        
    Returns:
        Alert history
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        query = db.query(models.AlertHistory)\
            .filter(models.AlertHistory.timestamp >= cutoff_time)
        
        if severity:
            query = query.filter(models.AlertHistory.severity == severity)
        
        alerts = query.order_by(models.AlertHistory.timestamp.desc()).all()
        
        return {
            'success': True,
            'count': len(alerts),
            'time_range': f'Last {hours} hours',
            'alerts': [
                {
                    'id': a.id,
                    'alert_id': a.alert_id,
                    'batch_id': a.batch_id,
                    'timestamp': a.timestamp.isoformat(),
                    'severity': a.severity,
                    'type': a.alert_type,
                    'title': a.title,
                    'status': a.status
                }
                for a in alerts
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/{alert_id}")
async def get_alert_details(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed alert information
    
    Args:
        alert_id: Alert identifier
        db: Database session
        
    Returns:
        Alert details
    """
    try:
        alert = db.query(models.AlertHistory)\
            .filter(models.AlertHistory.alert_id == alert_id)\
            .first()
        
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        return {
            'success': True,
            'alert': {
                'id': alert.id,
                'alert_id': alert.alert_id,
                'batch_id': alert.batch_id,
                'machine_id': alert.machine_id,
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity,
                'type': alert.alert_type,
                'title': alert.title,
                'message': alert.message,
                'status': alert.status,
                'acknowledged': alert.acknowledged,
                'acknowledged_by': alert.acknowledged_by,
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'resolved': alert.resolved,
                'resolved_by': alert.resolved_by,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                'resolution_notes': alert.resolution_notes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert: {str(e)}")


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str,
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert
    
    Args:
        alert_id: Alert identifier
        acknowledged_by: User who acknowledged
        db: Database session
        
    Returns:
        Acknowledgment result
    """
    try:
        alert = db.query(models.AlertHistory)\
            .filter(models.AlertHistory.alert_id == alert_id)\
            .first()
        
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now()
        
        db.commit()
        
        return {
            'success': True,
            'alert_id': alert_id,
            'message': 'Alert acknowledged',
            'acknowledged_by': acknowledged_by,
            'acknowledged_at': alert.acknowledged_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolved_by: str,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Resolve an alert
    
    Args:
        alert_id: Alert identifier
        resolved_by: User who resolved
        resolution_notes: Optional resolution notes
        db: Database session
        
    Returns:
        Resolution result
    """
    try:
        alert = db.query(models.AlertHistory)\
            .filter(models.AlertHistory.alert_id == alert_id)\
            .first()
        
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        alert.status = 'resolved'
        alert.resolved = True
        alert.resolved_by = resolved_by
        alert.resolved_at = datetime.now()
        alert.resolution_notes = resolution_notes
        
        db.commit()
        
        return {
            'success': True,
            'alert_id': alert_id,
            'message': 'Alert resolved',
            'resolved_by': resolved_by,
            'resolved_at': alert.resolved_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/statistics/summary")
async def get_alert_statistics(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get alert statistics
    
    Args:
        hours: Time range in hours
        db: Database session
        
    Returns:
        Alert statistics
    """
    try:
        from sqlalchemy import func
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Total alerts
        total = db.query(models.AlertHistory)\
            .filter(models.AlertHistory.timestamp >= cutoff_time)\
            .count()
        
        # Active alerts
        active = db.query(models.AlertHistory)\
            .filter(
                models.AlertHistory.timestamp >= cutoff_time,
                models.AlertHistory.status == 'active'
            ).count()
        
        # Severity distribution
        severity_dist = db.query(
            models.AlertHistory.severity,
            func.count(models.AlertHistory.id).label('count')
        ).filter(
            models.AlertHistory.timestamp >= cutoff_time
        ).group_by(models.AlertHistory.severity).all()
        
        # Type distribution
        type_dist = db.query(
            models.AlertHistory.alert_type,
            func.count(models.AlertHistory.id).label('count')
        ).filter(
            models.AlertHistory.timestamp >= cutoff_time
        ).group_by(models.AlertHistory.alert_type).all()
        
        # Acknowledgment rate
        acknowledged = db.query(models.AlertHistory)\
            .filter(
                models.AlertHistory.timestamp >= cutoff_time,
                models.AlertHistory.acknowledged == True
            ).count()
        
        ack_rate = (acknowledged / total * 100) if total > 0 else 0
        
        # Resolution rate
        resolved = db.query(models.AlertHistory)\
            .filter(
                models.AlertHistory.timestamp >= cutoff_time,
                models.AlertHistory.resolved == True
            ).count()
        
        resolution_rate = (resolved / total * 100) if total > 0 else 0
        
        return {
            'success': True,
            'time_range': f'Last {hours} hours',
            'total_alerts': total,
            'active_alerts': active,
            'severity_distribution': {
                severity: count for severity, count in severity_dist
            },
            'type_distribution': {
                alert_type: count for alert_type, count in type_dist
            },
            'acknowledgment_rate': round(ack_rate, 1),
            'resolution_rate': round(resolution_rate, 1)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@router.post("/workflow/create")
async def create_alert_workflow(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """
    Create automated workflow for alert
    (Integration point for watsonx Orchestrate)
    
    Args:
        alert_id: Alert identifier
        db: Database session
        
    Returns:
        Workflow definition
    """
    alert_service = get_alert_service()
    
    try:
        # Get alert from database
        alert_record = db.query(models.AlertHistory)\
            .filter(models.AlertHistory.alert_id == alert_id)\
            .first()
        
        if not alert_record:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        # Create alert dict for workflow
        alert_dict = {
            'alert_id': alert_record.alert_id,
            'batch_id': alert_record.batch_id,
            'severity': alert_record.severity,
            'type': alert_record.alert_type,
            'escalation_required': alert_record.severity == 'CRITICAL'
        }
        
        # Create workflow
        workflow = alert_service.create_workflow(alert_dict)
        
        return {
            'success': True,
            'workflow': workflow
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")


def send_alert_notification(alert: dict, recipients: List[str], channels: List[str]):
    """
    Background task to send alert notifications
    
    Args:
        alert: Alert dictionary
        recipients: List of recipients
        channels: Notification channels
    """
    alert_service = get_alert_service()
    
    try:
        result = alert_service.send_notification(
            alert=alert,
            recipients=recipients,
            channels=channels
        )
        print(f"Notification sent for alert {alert['alert_id']}: {result['success']}")
    except Exception as e:
        print(f"Failed to send notification for alert {alert['alert_id']}: {e}")

# Made with Bob
