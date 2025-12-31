from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from Schemas.items import ItemResponse
from Schemas.storage_bin import StorageBinResponse



class RackBase(BaseModel):
    rack_id: Optional[str] = None   # parent rack id (if hierarchical)
    location: Optional[str] = None


class RackCreate(RackBase):
    location: str 


class RackUpdate(BaseModel):
    rack_id: str
    location: Optional[str] = None


class RackResponse(RackBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    storage_bins: List[StorageBinResponse] = []
    items: List[ItemResponse] = []

    class Config:
        from_attributes = True  


