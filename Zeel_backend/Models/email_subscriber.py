from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from Database.database import Base


class EmailSubscriber(Base):
    __tablename__ = "email_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    last_sent_date = Column(DateTime(timezone=True), nullable=True)
