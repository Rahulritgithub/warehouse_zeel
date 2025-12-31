from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from Database.database import Base
from Models.storage_bin import StorageBin

class TransactionType(str, enum.Enum):
    INWARD = "inward"
    OUTWARD = "outward"
    RETURN = "return"


from sqlalchemy import UniqueConstraint

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(TransactionType), nullable=False)
    reason = Column(String(255), default=None)
    storage_bin_rfid = Column(String(100), ForeignKey(StorageBin.rfid))
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())

    storage_bin = relationship("StorageBin", back_populates="transactions")

    __table_args__ = (
        UniqueConstraint("storage_bin_rfid", "type", name="uq_rfid_transaction_type"),
    )
