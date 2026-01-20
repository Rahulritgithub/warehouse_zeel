from typing import Optional, List
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


class BulkTransactionUpdateRequest(BaseModel):
    rfids: List[str]  # BULK RFID list from frontend
    type: TransactionType
    reason: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    type: TransactionType
    storage_bin_rfid: str
    reason: Optional[str]
    transaction_date: datetime

    item_rfids: List[str] = []


class BulkRFIDVerifyRequest(BaseModel):
    rfids: List[str]


class BulkRFIDVerifyResponse(BaseModel):
    existing_rfids: List[str]  # RFIDs that exist in Item table
    missing_rfids: List[str]  # RFIDs not found

    class Config:
        from_attributes = True
