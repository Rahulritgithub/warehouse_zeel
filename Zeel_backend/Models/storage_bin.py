from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Database.database import Base


class StorageBin(Base):
    __tablename__ = "storage_bins"

    id = Column(Integer, primary_key=True, index=True)
    rfid = Column(String(100), unique=True, index=True)
    rack_id = Column(String(100), ForeignKey("racks.rack_id"))  # Fixed ForeignKey
    capacity = Column(Integer, default=1, nullable=False)  # Added capacity field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    rack = relationship("Rack", back_populates="storage_bins")
    items = relationship("Item", back_populates="storage_bin")
    transactions = relationship("Transaction", back_populates="storage_bin")
