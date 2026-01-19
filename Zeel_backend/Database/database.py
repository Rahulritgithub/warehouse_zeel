from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.settings import settings
import logging

logger = logging.getLogger(__name__)

# ---------------------------
# Database Engine
# ---------------------------
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # auto-reconnect
        pool_size=10,
        max_overflow=20,
    )
except Exception as e:
    logger.error(f"Failed to create DB engine: {e}")
    raise

# ---------------------------
# Session
# ---------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---------------------------
# Base Model
# ---------------------------
Base = declarative_base()


# ---------------------------
# Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
