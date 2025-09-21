"""Health check endpoint for CatalogAI backend."""

from fastapi import APIRouter, Depends
from sqlmodel import Session
from datetime import datetime
import logging

from ..schemas import HealthResponse
from ..db import get_session
from ..pipeline.classifier import is_model_available

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check(session: Session = Depends(get_session)):
    """
    Health check endpoint.
    
    Returns system status including database connectivity and model availability.
    """
    try:
        # Check database connectivity
        try:
            session.connection()
            database_connected = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            database_connected = False
        
        # Check model availability
        model_loaded = is_model_available()
        
        # Determine overall status
        if database_connected and model_loaded:
            status = "healthy"
        elif database_connected:
            status = "degraded"  # DB works but no model
        else:
            status = "unhealthy"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.utcnow(),
            model_loaded=model_loaded,
            database_connected=database_connected
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="error",
            timestamp=datetime.utcnow(),
            model_loaded=False,
            database_connected=False
        )