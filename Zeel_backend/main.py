# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlalchemy.orm import Session
import logging
from Database.database import Base, engine, SessionLocal
from Utils.hashing import hash_password
from scheduler import start_scheduler
from Middleware.api_monitor import api_monitor
from core.logging import setup_logging
from dotenv import load_dotenv

# Import routers
from api.v1 import (
    email_subscribers,
    items,
    racks,
    request as request_router,
    sku,
    admin,
    transaction,
    storage_bin,
)
from Models.user import User

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()

# ---------------------------
# Logging Setup
# ---------------------------
setup_logging()
logger = logging.getLogger(__name__)

# ---------------------------
# FastAPI app initialization
# ---------------------------
app = FastAPI(title="Inventory Backend API", version="1.0.0")

# ---------------------------
# CORS Middleware
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# API Monitoring Middleware
# ---------------------------
app.middleware("http")(api_monitor)

# ---------------------------
# Start Scheduler
# ---------------------------
start_scheduler()

# ---------------------------
# Include Routers
# ---------------------------
api_prefix = "/api/v1"
app.include_router(racks.router, prefix=api_prefix)
app.include_router(storage_bin.router, prefix=api_prefix)
app.include_router(items.router, prefix=api_prefix)
app.include_router(transaction.router, prefix=api_prefix)
app.include_router(request_router.router, prefix=api_prefix)
app.include_router(email_subscribers.router, prefix=api_prefix)
app.include_router(sku.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)


# ---------------------------
# Startup Event
# ---------------------------
@app.on_event("startup")
def startup():
    try:
        logger.info("Starting up application...")

        # Create database tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")

        # Inspect tables
        inspector = inspect(engine)
        logger.info(f"Available tables: {inspector.get_table_names()}")

        # Create default admin user if not exists
        db: Session = SessionLocal()
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            new_admin = User(
                username="admin", password=hash_password("Admin@123"), role="admin"
            )
            db.add(new_admin)
            db.commit()
            logger.info("Default admin user created: username='admin'")

        db.close()
        logger.info("Startup completed successfully.")

    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)


# ---------------------------
# Run server (for direct execution)
# ---------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
