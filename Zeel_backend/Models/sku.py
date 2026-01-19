from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Database.database import Base


class SKU(Base):
    __tablename__ = "skus"

    id = Column(Integer, primary_key=True, index=True)
    sku_code = Column(String(50), unique=True, index=True)  # e.g TS-M-BLU
    product_name = Column(String(100))
    category = Column(String(50))

    mrp = Column(Float)
    sale_price = Column(Float)
    gst_percent = Column(Float)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relationship
    items = relationship("Item", back_populates="sku")
