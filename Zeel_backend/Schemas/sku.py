from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SKUBase(BaseModel):
    sku_code: str
    product_name: str
    category: Optional[str] = None
    mrp: float
    sale_price: float
    gst_percent: float


class SKUCreate(SKUBase):
    pass


class SKUUpdate(BaseModel):
    product_name: Optional[str]
    category: Optional[str]
    mrp: Optional[float]
    sale_price: Optional[float]
    gst_percent: Optional[float]
    is_active: Optional[bool]


class SKUResponse(SKUBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
