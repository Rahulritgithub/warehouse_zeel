from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class StorageBinBase(BaseModel):
    rfid: str
    rack_id: str



class StorageBinCreate(StorageBinBase):
    rfid: str
    rack_id: str


class StorageBinUpdate(BaseModel):
    rfid: str
    rack_id: str



class StorageBinResponse(StorageBinBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
