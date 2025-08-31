from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Debug environment variables
logger.info(f"Environment DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT_SET')}")
logger.info(f"Settings DATABASE_URL: {settings.DATABASE_URL}")

# Validate DATABASE_URL
if not settings.DATABASE_URL or settings.DATABASE_URL.strip() == "" or settings.DATABASE_URL == "sqlite:///./ats.db":
    if os.environ.get('DATABASE_URL'):
        # Railway sets it but pydantic isn't picking it up
        database_url = os.environ.get('DATABASE_URL')
        logger.info(f"Using Railway DATABASE_URL from environment: {database_url[:50]}...")
    else:
        logger.warning("DATABASE_URL is empty or not set. Using default SQLite.")
        database_url = "sqlite:///./ats.db"
else:
    database_url = settings.DATABASE_URL
    logger.info(f"Using database from settings: {database_url.split('@')[0]}@***" if '@' in database_url else database_url)

# Create database engine
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables."""
    # Import all models to ensure they are registered
    # Order matters to avoid circular dependencies
    from app.models import user
    from app.models import job
    from app.models import resume
    from app.models import analysis
    from app.models import application
    
    # Create tables
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()