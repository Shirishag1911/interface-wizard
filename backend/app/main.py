"""Main FastAPI application."""
import sys
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import settings
from app.presentation.routes import router

# Configure logging
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL)

# Create logs directory if it doesn't exist
log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)
logger.add(
    settings.LOG_FILE,
    rotation="10 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Generative AI-based healthcare data integration tool for HL7/FHIR interfaces",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for debugging."""
    logger.info(f"📥 {request.method} {request.url.path}")
    logger.info(f"   Headers: {dict(request.headers)}")
    logger.info(f"   Query params: {dict(request.query_params)}")

    try:
        response = await call_next(request)
        logger.info(f"📤 Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ Request failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
        )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["Interface Wizard"])


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
