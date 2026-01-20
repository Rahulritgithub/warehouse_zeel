import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --------------------------------------------------
# 1. SET TEST ENV VARIABLES (BEFORE APP IMPORT)
# --------------------------------------------------
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["MAIL_USERNAME"] = "test@example.com"
os.environ["MAIL_PASSWORD"] = "test123"
os.environ["MAIL_FROM"] = "test@example.com"
os.environ["MAIL_PORT"] = "587"
os.environ["MAIL_SERVER"] = "smtp.test.com"

# --------------------------------------------------
# 2. IMPORT APP + DB AFTER ENV SET
# --------------------------------------------------
from main import app
from Database.database import Base, get_db

# --------------------------------------------------
# 3. CREATE TEST DATABASE ENGINE
# --------------------------------------------------
engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
)


# --------------------------------------------------
# 4. CREATE TABLES ONCE
# --------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --------------------------------------------------
# 5. SHARED DB SESSION (CRITICAL FIX)
# --------------------------------------------------
@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# --------------------------------------------------
# 6. OVERRIDE get_db TO USE SAME SESSION
# --------------------------------------------------
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
