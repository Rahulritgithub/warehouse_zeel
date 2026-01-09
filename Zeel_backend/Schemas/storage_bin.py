from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class StorageBinBase(BaseModel):
    rfid: str
    rack_id: str
    capacity: int = Field(default=1, ge=1, description="Maximum number of items the bin can hold")


class StorageBinCreate(StorageBinBase):
    rfid: str
    rack_id: str
    capacity: int = Field(default=1, ge=1)


class StorageBinUpdate(BaseModel):
    rfid: Optional[str] = None
    rack_id: Optional[str] = None
    capacity: Optional[int] = Field(default=None, ge=1)


class StorageBinResponse(StorageBinBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True