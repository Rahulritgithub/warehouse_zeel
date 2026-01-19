from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from Database.database import Base


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    req_from = Column(String(255))
    req_to = Column(String(255))
    description = Column(String(500))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    request_date = Column(DateTime(timezone=True))
    is_sent = Column(Boolean, default=False)  # Track if email was sent
