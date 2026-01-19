from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List
from enum import Enum


class ItemTrackStatus(str, Enum):
    INWARD = "INWARD"
    OUTWARD = "OUTWARD"
    RETURN = "RETURN"


class ItemBase(BaseModel):
    rfid: Optional[str] = None
    sku_id: Optional[int] = None
    rack_id: Optional[str] = None
    storage_bin_rfid: Optional[str] = None
    status: Optional[str] = "IN_STOCK"
    track: Optional[ItemTrackStatus] = ItemTrackStatus.INWARD

    @validator("track")
    def validate_track(cls, v):
        if v not in ItemTrackStatus:
            raise ValueError(
                f"track must be one of: {', '.join([e.value for e in ItemTrackStatus])}"
            )
        return v


class ItemCreate(ItemBase):
    rfid: str
    sku_id: int
    rack_id: str
    storage_bin_rfid: str


class ItemUpdate(BaseModel):
    sku_id: Optional[int] = None
    rack_id: Optional[str] = None
    storage_bin_rfid: Optional[str] = None
    status: Optional[str] = None
    track: Optional[ItemTrackStatus] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
        use_enum_values = True


class ItemBulkCreate(BaseModel):
    rfids: List[str]
    sku_id: int
    rack_id: str
    storage_bin_rfid: str
    track: Optional[ItemTrackStatus] = ItemTrackStatus.INWARD


class ItemTrackUpdate(BaseModel):
    track: ItemTrackStatus
    rack_id: Optional[str] = None
    storage_bin_rfid: Optional[str] = None


class ItemFilter(BaseModel):
    track: Optional[ItemTrackStatus] = None
    status: Optional[str] = None
    sku_id: Optional[int] = None
    rack_id: Optional[str] = None
