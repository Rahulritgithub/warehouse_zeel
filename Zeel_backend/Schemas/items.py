from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    rfid: Optional[str] = None
    sku_id: Optional[int] = None
    rack_id: Optional[str] = None
    storage_bin_rfid: Optional[str] = None


class ItemCreate(ItemBase):
    rfid: str
    sku_id: int
    rack_id: str
    storage_bin_rfid: str


class ItemUpdate(BaseModel):
    sku_id: Optional[int] = None
    rack_id: Optional[str] = None
    storage_bin_rfid: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
