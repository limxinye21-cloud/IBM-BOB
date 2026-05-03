"""
Data ingestion API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.db import get_db, ProcessData
from backend.app.schemas.data_schema import (
    ProcessDataCreate,
    ProcessDataResponse,
    ProcessDataBatch,
    HistoricalQuery,
    HistoricalResponse
)

router = APIRouter()


@router.post("/ingest", response_model=ProcessDataResponse, status_code=status.HTTP_201_CREATED)
async def ingest_data(
    data: ProcessDataCreate,
    db: Session = Depends(get_db)
):
    """
    Ingest single process data point
    
    Args:
        data: Process data to ingest
        db: Database session
        
    Returns:
        Created process data
    """
    try:
        # Create database model from schema
        db_data = ProcessData(**data.model_dump())
        
        # Add to database
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        
        return db_data
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest data: {str(e)}"
        )


@router.post("/ingest/batch", status_code=status.HTTP_201_CREATED)
async def ingest_batch(
    batch: ProcessDataBatch,
    db: Session = Depends(get_db)
):
    """
    Ingest batch of process data
    
    Args:
        batch: Batch of process data
        db: Database session
        
    Returns:
        Summary of ingestion
    """
    try:
        # Create database models
        db_data_list = [ProcessData(**item.model_dump()) for item in batch.data]
        
        # Bulk insert
        db.bulk_save_objects(db_data_list)
        db.commit()
        
        return {
            "status": "success",
            "count": len(batch.data),
            "message": f"Successfully ingested {len(batch.data)} data points"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest batch: {str(e)}"
        )


@router.get("/latest", response_model=ProcessDataResponse)
async def get_latest_data(
    db: Session = Depends(get_db)
):
    """
    Get latest process data point
    
    Args:
        db: Database session
        
    Returns:
        Latest process data
    """
    data = db.query(ProcessData).order_by(ProcessData.timestamp.desc()).first()
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found"
        )
    
    return data


@router.get("/batch/{batch_id}", response_model=List[ProcessDataResponse])
async def get_batch_data(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all data for a specific batch
    
    Args:
        batch_id: Batch identifier
        db: Database session
        
    Returns:
        List of process data for the batch
    """
    data = db.query(ProcessData).filter(ProcessData.batch_id == batch_id).all()
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for batch {batch_id}"
        )
    
    return data


@router.post("/historical", response_model=HistoricalResponse)
async def query_historical_data(
    query: HistoricalQuery,
    db: Session = Depends(get_db)
):
    """
    Query historical process data
    
    Args:
        query: Query parameters
        db: Database session
        
    Returns:
        Historical data matching query
    """
    # Build query
    db_query = db.query(ProcessData)
    
    # Apply filters
    if query.start_time:
        db_query = db_query.filter(ProcessData.timestamp >= query.start_time)
    
    if query.end_time:
        db_query = db_query.filter(ProcessData.timestamp <= query.end_time)
    
    if query.batch_id:
        db_query = db_query.filter(ProcessData.batch_id == query.batch_id)
    
    if query.status:
        db_query = db_query.filter(ProcessData.status == query.status)
    
    # Get total count
    total = db_query.count()
    
    # Apply pagination
    data = db_query.order_by(ProcessData.timestamp.desc()).offset(query.offset).limit(query.limit).all()
    
    return HistoricalResponse(total=total, data=data)


@router.delete("/batch/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch_data(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete all data for a specific batch
    
    Args:
        batch_id: Batch identifier
        db: Database session
    """
    deleted = db.query(ProcessData).filter(ProcessData.batch_id == batch_id).delete()
    
    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for batch {batch_id}"
        )
    
    db.commit()
    
    return None


@router.get("/recent")
async def get_historical_data_get(
    hours: int = 24,
    limit: int = 200,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    GET endpoint for recent historical data (supports query params).
    Returns up to `limit` records from the last `hours` hours.
    """
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(ProcessData).filter(ProcessData.timestamp >= cutoff)
    if status_filter:
        q = q.filter(ProcessData.status == status_filter)
    records = q.order_by(ProcessData.timestamp.asc()).limit(limit).all()
    return {
        "success": True,
        "total": len(records),
        "data": [
            {c.name: getattr(r, c.name) for c in r.__table__.columns}
            for r in records
        ]
    }


@router.get("/stats")
async def get_data_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics about stored data
    
    Args:
        db: Database session
        
    Returns:
        Data statistics
    """
    total_records = db.query(ProcessData).count()
    
    # Count by status
    good_count = db.query(ProcessData).filter(ProcessData.status == "GOOD").count()
    warning_count = db.query(ProcessData).filter(ProcessData.status == "WARNING").count()
    severe_count = db.query(ProcessData).filter(ProcessData.status == "SEVERE").count()
    
    # Get date range
    oldest = db.query(ProcessData).order_by(ProcessData.timestamp.asc()).first()
    newest = db.query(ProcessData).order_by(ProcessData.timestamp.desc()).first()
    
    # Get unique batches
    unique_batches = db.query(ProcessData.batch_id).distinct().count()
    
    return {
        "total_records": total_records,
        "status_distribution": {
            "GOOD": good_count,
            "WARNING": warning_count,
            "SEVERE": severe_count
        },
        "date_range": {
            "oldest": oldest.timestamp if oldest else None,
            "newest": newest.timestamp if newest else None
        },
        "unique_batches": unique_batches
    }

# Made with Bob
