from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class TransactionType(str, Enum):
    INWARD = "inward"
    OUTWARD = "outward"
    RETURN = "return"


class TransactionBase(BaseModel):
    type: TransactionType
    storage_bin_rfid: str
    reason: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    transaction_date: datetime

    class Config:
        from_attributes = True
