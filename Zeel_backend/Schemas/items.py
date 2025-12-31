from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from Schemas.transaction import TransactionResponse


class ItemBase(BaseModel):
    rfid: Optional[str] = None
    rack_id: Optional[str] = None
    storage_bin_rfid: Optional[str] = None


class ItemCreate(ItemBase):
    rfid: str
    rack_id: str
    storage_bin_rfid: str


class ItemUpdate(BaseModel):
    rfid: Optional[str] = None
    rack_id: str
    storage_bin_rfid: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    # Nested relationships
    transactions: List["TransactionResponse"] = []

    class Config:
        orm_mode = True
