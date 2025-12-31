import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Models.user import User
from Database.database import Base, engine, SessionLocal
from Middleware.api_monitor import api_monitor
import logging
from dotenv import load_dotenv
from sqlalchemy import inspect
from Utils.hashing import hash_password
from scheduler import start_scheduler
from Models.items import Item
from Models.request import Request
from Models.rack import Rack
from Models.storage_bin import StorageBin
from Models.transaction import Transaction
from Models.user import User
from Routes import rack
from Routes import storage_bin
from Routes import items
from Routes import transaction
from Routes import request,email_subscriber


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Inventory Backend API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(api_monitor)

start_scheduler()

app.include_router(rack.router)
app.include_router(storage_bin.router)
app.include_router(items.router)
app.include_router(transaction.router)
app.include_router(request.router)
app.include_router(email_subscriber.router) 

# ---------------------------
#  SINGLE STARTUP FUNCTION
# ---------------------------
@app.on_event("startup")
def startup():
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created.")

        inspector = inspect(engine)
        logger.info(f"Available tables: {inspector.get_table_names()}")

        db = SessionLocal()

        # Create default admin
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            new_admin = User(
                username="admin",
                password=hash_password("Admin@123"),
                role="admin"
            )
            db.add(new_admin)
            db.commit()

        db.close()

    except Exception as e:
        logger.error(f"Startup failed: {e}")


# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
