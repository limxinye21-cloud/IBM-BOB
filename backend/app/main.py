"""
Main FastAPI application for AI Packaging Reliability Copilot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from backend.app.config import settings
from backend.app.db import init_db

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting AI Packaging Reliability Copilot API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise
    
    # Load ML model
    try:
        from backend.app.services.ml_service import initialize_ml_service
        ml_loaded = initialize_ml_service()
        if ml_loaded:
            logger.info("✓ ML model loaded successfully")
        else:
            logger.warning("⚠ ML model not available - using rule-based classification")
    except Exception as e:
        logger.warning(f"⚠ Failed to load ML model: {e}")
        logger.info("Continuing with rule-based classification")
    
    logger.info(f"✓ API started successfully on {settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    # TODO: Cleanup resources


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time semiconductor packaging monitoring and AI copilot system",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected"
    }


# API v1 router group
@app.get(f"{settings.API_V1_PREFIX}/")
async def api_v1_root():
    """API v1 root"""
    return {
        "version": "v1",
        "endpoints": {
            "data": f"{settings.API_V1_PREFIX}/data",
            "status": f"{settings.API_V1_PREFIX}/status",
            "analysis": f"{settings.API_V1_PREFIX}/analysis",
            "copilot": f"{settings.API_V1_PREFIX}/copilot",
            "alerts": f"{settings.API_V1_PREFIX}/alerts"
        }
    }


# Include routers
from backend.app.api.routes import data, ml, copilot, alerts

app.include_router(data.router, prefix=f"{settings.API_V1_PREFIX}", tags=["data"])
app.include_router(ml.router, prefix=f"{settings.API_V1_PREFIX}", tags=["ml"])
app.include_router(copilot.router, prefix=f"{settings.API_V1_PREFIX}", tags=["copilot"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_PREFIX}", tags=["alerts"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

# Made with Bob
