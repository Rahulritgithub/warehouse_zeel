# Routes/transaction.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Database.database import get_db
from Models.transaction import Transaction
from Schemas.transaction import TransactionCreate, TransactionResponse
from Models.storage_bin import StorageBin

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# -------------------------------
# CREATE TRANSACTION
# -------------------------------
@router.post("/add", response_model=TransactionResponse)
def create_transaction(transaction_data: TransactionCreate, db: Session = Depends(get_db)):

    # 1️⃣ Check if storage bin exists
    bin_exists = db.query(StorageBin).filter(
        StorageBin.rfid == transaction_data.storage_bin_rfid
    ).first()

    if not bin_exists:
        raise HTTPException(status_code=404, detail="Storage Bin RFID does not exist")

    # 2️⃣ Check if RFID already used in transaction table
    exists_in_transaction = db.query(Transaction).filter(
        Transaction.storage_bin_rfid == transaction_data.storage_bin_rfid
    ).first()

    if exists_in_transaction:
        raise HTTPException(
            status_code=400,
            detail="Transaction for this Storage Bin RFID already exists. Duplicate not allowed."
        )

    # 3️⃣ Insert new transaction
    new_tx = Transaction(
        type=transaction_data.type,
        storage_bin_rfid=transaction_data.storage_bin_rfid,
        reason=transaction_data.reason
    )

    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx



# -------------------------------
# GET ALL TRANSACTIONS
# -------------------------------
@router.get("/get_all", response_model=list[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Transaction).offset(skip).limit(limit).all()


# -------------------------------
# GET ALL TRANSACTIONS FOR A STORAGE BIN RFID
# -------------------------------
@router.get("/get/{rfid}", response_model=list[TransactionResponse])
def get_transaction_by_rfid(rfid: str, db: Session = Depends(get_db)):

    transactions = db.query(Transaction).filter(
        Transaction.storage_bin_rfid == rfid
    ).all()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this RFID")

    return transactions


# -------------------------------
# UPDATE TRANSACTION USING RFID
# -------------------------------
@router.put("/update/{rfid}", response_model=TransactionResponse)
def update_transaction_by_rfid(rfid: str, transaction_data: TransactionCreate, db: Session = Depends(get_db)):

    transaction = db.query(Transaction).filter(
        Transaction.storage_bin_rfid == rfid
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found for this RFID")

    # Update fields
    transaction.type = transaction_data.type
    transaction.storage_bin_rfid = transaction_data.storage_bin_rfid
    transaction.reason = transaction_data.reason

    db.commit()
    db.refresh(transaction)
    return transaction


# -------------------------------
# DELETE TRANSACTION USING RFID
# -------------------------------
@router.delete("/remove/{rfid}")
def delete_transaction_by_rfid(rfid: str, db: Session = Depends(get_db)):

    transaction = db.query(Transaction).filter(
        Transaction.storage_bin_rfid == rfid
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found for this RFID")

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}
