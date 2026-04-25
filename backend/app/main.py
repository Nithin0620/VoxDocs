"""
VoxDocs FastAPI Application.
Main entry point for the Voice Document Assistant backend.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from app import config
from app.routes import upload, query, voice

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description="AI-powered Voice Document Assistant API",
    version=config.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# === MIDDLEWARE ===

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)


# === ROUTES ===

# Include routers
app.include_router(upload.router, prefix=config.API_V1_PREFIX)
app.include_router(query.router, prefix=config.API_V1_PREFIX)
app.include_router(voice.router, prefix=config.API_V1_PREFIX)


# === HEALTH CHECKS ===

@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    Returns the status of the API.
    """
    return {
        "status": "healthy",
        "version": config.APP_VERSION,
        "name": config.APP_NAME
    }


@app.get("/")
async def root() -> dict:
    """
    Root endpoint with API information.
    """
    return {
        "name": config.APP_NAME,
        "version": config.APP_VERSION,
        "description": "AI-powered Voice Document Assistant",
        "docs": "/docs",
        "health": "/health"
    }


# === ERROR HANDLERS ===

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    General exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }


# === STARTUP/SHUTDOWN ===

@app.on_event("startup")
async def startup_event():
    """Called when application starts."""
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info("API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Called when application shuts down."""
    logger.info(f"Shutting down {config.APP_NAME}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
