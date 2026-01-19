from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class RequestBase(BaseModel):
    req_from: str
    req_to: str
    description: Optional[str] = None
    request_date: datetime


class RequestCreate(RequestBase):
    pass


class RequestResponse(RequestBase):
    id: int
    created_date: datetime

    class Config:
        orm_mode = True
