"""Admin management endpoints for CatalogAI."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pathlib import Path
import time
import logging

from ..schemas import ThresholdsIn, ThresholdsOut, TrainingResponse
from ..models import ThresholdConfig
from ..db import get_session
from ..config import settings
from ..pipeline.classifier import train, get_model_metrics as get_saved_model_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/thresholds", response_model=ThresholdsOut)
async def get_thresholds(session: Session = Depends(get_session)):
    """Get current threshold configuration."""
    try:
        # Try to get from database first
        query = select(ThresholdConfig).order_by(ThresholdConfig.updated_at.desc())
        threshold_config = session.exec(query).first()
        
        if threshold_config:
            return ThresholdsOut(
                thresh_auth=threshold_config.thresh_auth,
                thresh_syn=threshold_config.thresh_syn,
                updated_at=threshold_config.updated_at,
                updated_by=threshold_config.updated_by
            )
        else:
            # Return current settings as fallback
            from datetime import datetime
            return ThresholdsOut(
                thresh_auth=settings.thresh_auth,
                thresh_syn=settings.thresh_syn,
                updated_at=datetime.utcnow(),
                updated_by="system"
            )
            
    except Exception as e:
        logger.error(f"Error getting thresholds: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving thresholds")


@router.put("/thresholds", response_model=ThresholdsOut)
async def update_thresholds(
    thresholds: ThresholdsIn,
    session: Session = Depends(get_session)
):
    """Update threshold configuration."""
    try:
        # Validate thresholds
        if thresholds.thresh_syn <= thresholds.thresh_auth:
            raise HTTPException(
                status_code=400,
                detail="thresh_syn must be greater than thresh_auth"
            )
        
        # Update settings object (for immediate effect)
        settings.thresh_auth = thresholds.thresh_auth
        settings.thresh_syn = thresholds.thresh_syn
        
        # Save to database for persistence
        threshold_config = ThresholdConfig(
            thresh_auth=thresholds.thresh_auth,
            thresh_syn=thresholds.thresh_syn,
            updated_by="admin"
        )
        
        session.add(threshold_config)
        session.commit()
        session.refresh(threshold_config)
        
        logger.info(f"Thresholds updated: auth={thresholds.thresh_auth}, syn={thresholds.thresh_syn}")
        
        return ThresholdsOut(
            thresh_auth=threshold_config.thresh_auth,
            thresh_syn=threshold_config.thresh_syn,
            updated_at=threshold_config.updated_at,
            updated_by=threshold_config.updated_by
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Error updating thresholds")


@router.post("/train", response_model=TrainingResponse)
async def retrain_model():
    """Retrain the authenticity detection model."""
    start_time = time.time()
    
    try:
        logger.info("Starting model retraining...")
        
        # Path to seed data (align with main.py)
        seed_dir = Path(__file__).parent.parent.parent / "data" / "seeds"
        
        if not seed_dir.exists():
            raise HTTPException(
                status_code=500,
                detail="Seed data directory not found"
            )
        
        # Train model
        metrics = train(seed_dir)
        
        training_time = (time.time() - start_time) * 1000
        
        logger.info(f"Model retraining completed in {training_time:.2f}ms")
        
        return TrainingResponse(
            success=True,
            message="Model retrained successfully",
            metrics=metrics,
            training_time_ms=training_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retraining model: {e}")
        training_time = (time.time() - start_time) * 1000
        
        return TrainingResponse(
            success=False,
            message=f"Training failed: {str(e)}",
            metrics={},
            training_time_ms=training_time
        )


@router.get("/metrics")
async def get_metrics():
    """Get current model performance metrics."""
    try:
        metrics = get_saved_model_metrics()
        
        if metrics is None:
            raise HTTPException(
                status_code=404,
                detail="No model metrics available. Train model first."
            )
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model metrics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving model metrics")