"""Main FastAPI application for CatalogAI backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from .config import settings
from .db import create_db_and_tables
from .routers import health, scans, admin
from .pipeline.classifier import is_model_available, train

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting CatalogAI backend...")
    
    try:
        # Initialize database
        create_db_and_tables()
        logger.info("Database initialized")
        
        # Check if model exists, train if not
        if not is_model_available():
            logger.info("Model not found, training initial model...")
            try:
                seed_dir = Path(__file__).parent.parent.parent / "data" / "seeds"
                if seed_dir.exists():
                    metrics = train(seed_dir)
                    logger.info(f"Initial model trained with accuracy: {metrics.get('accuracy', 'unknown')}")
                else:
                    logger.warning("Seed data directory not found, model training skipped")
            except Exception as e:
                logger.error(f"Failed to train initial model: {e}")
        else:
            logger.info("Model loaded successfully")
        
        logger.info("CatalogAI backend startup complete")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Don't fail startup completely, let the app run in degraded mode
    
    yield
    
    # Shutdown
    logger.info("Shutting down CatalogAI backend...")


# Create FastAPI app
app = FastAPI(
    title="CatalogAI - Authenticity Detection",
    description="AI-powered image authenticity detection for product catalogs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(scans.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "CatalogAI - Authenticity Detection API",
        "version": "1.0.0",
        "description": "AI-powered image authenticity detection for product catalogs",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/status")
async def status():
    """Simple status endpoint."""
    return {
        "status": "running",
        "model_available": is_model_available()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )