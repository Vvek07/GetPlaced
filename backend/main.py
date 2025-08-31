from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from decouple import config
import uvicorn
import os
import logging

# Import core modules
from app.core.config import settings
from app.core.database import init_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes with error handling
try:
    from app.api.routes import auth, users, jobs, resumes, matching, analysis
    ROUTES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some routes may not be available due to missing dependencies: {e}")
    # Import only essential routes
    try:
        from app.api.routes import auth, users
        ROUTES_AVAILABLE = False
    except ImportError:
        logger.error("Critical error: Cannot import essential routes")
        ROUTES_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI application
app = FastAPI(
    title="GetPlaced API",
    description="Smart ATS analysis platform API to help you get placed in your dream job",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with error handling
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])

if ROUTES_AVAILABLE:
    try:
        app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
        app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
        app.include_router(matching.router, prefix="/matching", tags=["Matching"])
        app.include_router(analysis.router, prefix="/analyses", tags=["Analysis"])
        logger.info("All routes loaded successfully")
    except Exception as e:
        logger.warning(f"Some advanced routes not available: {e}")
else:
    logger.info("Running in minimal mode - only auth and users available")


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "GetPlaced API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="info"
    )