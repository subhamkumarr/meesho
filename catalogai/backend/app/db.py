"""Database connection and session management."""

from sqlmodel import SQLModel, create_engine, Session
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.db_url,
    echo=settings.log_level == "DEBUG",
    connect_args={"check_same_thread": False} if "sqlite" in settings.db_url else {}
)


def create_db_and_tables():
    """Create database tables if they don't exist."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session