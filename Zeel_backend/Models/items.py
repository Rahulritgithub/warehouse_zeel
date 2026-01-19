from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Database.database import Base
from Models.rack import Rack
from Models.storage_bin import StorageBin
import enum


class ItemTrackStatus(enum.Enum):
    INWARD = "INWARD"
    OUTWARD = "OUTWARD"
    RETURN = "RETURN"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    rfid = Column(String(100), unique=True, index=True)

    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)

    rack_id = Column(String(100), ForeignKey(Rack.rack_id))
    storage_bin_rfid = Column(String(100), ForeignKey(StorageBin.rfid))

    status = Column(String(20), default="IN_STOCK")  # IN_STOCK / SOLD / DAMAGED
    track = Column(Enum(ItemTrackStatus), default=ItemTrackStatus.INWARD)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    rack = relationship("Rack", back_populates="items")
    storage_bin = relationship("StorageBin", back_populates="items")
    sku = relationship("SKU", back_populates="items")
