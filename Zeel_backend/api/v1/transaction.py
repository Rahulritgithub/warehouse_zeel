from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Database.database import get_db
from Schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    BulkTransactionUpdateRequest,
    BulkRFIDVerifyRequest,
    BulkRFIDVerifyResponse,
)
from Crud import crud_transaction as crud_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# -------------------------------
# CREATE TRANSACTION
# -------------------------------
@router.post("/add", response_model=TransactionResponse)
def create_transaction(
    transaction_data: TransactionCreate, db: Session = Depends(get_db)
):
    if not crud_transaction.storage_bin_exists(db, transaction_data.storage_bin_rfid):
        raise HTTPException(status_code=404, detail="Storage Bin RFID does not exist")

    if crud_transaction.transaction_exists_for_bin(
        db, transaction_data.storage_bin_rfid
    ):
        raise HTTPException(
            status_code=400,
            detail="Transaction for this Storage Bin RFID already exists",
        )

    return crud_transaction.create_transaction(db, transaction_data)


# -------------------------------
# GET ALL TRANSACTIONS
# -------------------------------
@router.get("/get_all", response_model=list[TransactionResponse])
def get_all_transactions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    transactions = crud_transaction.get_all_transactions(db, skip, limit)
    response = []

    for tx in transactions:
        items = crud_transaction.get_items_by_storage_bin(db, tx.storage_bin_rfid)
        item_rfids = [item.rfid for item in items]

        response.append(
            TransactionResponse(
                id=tx.id,
                type=tx.type,
                storage_bin_rfid=tx.storage_bin_rfid,
                reason=tx.reason,
                transaction_date=tx.transaction_date,
                item_rfids=item_rfids,
            )
        )

    return response


# -------------------------------
# GET TRANSACTION BY RFID
# -------------------------------
@router.get("/get/{rfid}", response_model=list[TransactionResponse])
def get_transaction_by_rfid(rfid: str, db: Session = Depends(get_db)):
    transactions = crud_transaction.get_transactions_by_rfid(db, rfid)

    if not transactions:
        raise HTTPException(
            status_code=404, detail="No transactions found for this storage bin RFID"
        )

    items = crud_transaction.get_items_by_storage_bin(db, rfid)
    item_rfids = [item.rfid for item in items]

    return [
        TransactionResponse(
            id=tx.id,
            type=tx.type,
            storage_bin_rfid=tx.storage_bin_rfid,
            reason=tx.reason,
            transaction_date=tx.transaction_date,
            item_rfids=item_rfids,
        )
        for tx in transactions
    ]


# -------------------------------
# UPDATE TRANSACTION
# -------------------------------
@router.put("/update/{rfid}", response_model=TransactionResponse)
def update_transaction_by_rfid(
    rfid: str, transaction_data: TransactionCreate, db: Session = Depends(get_db)
):
    transactions = crud_transaction.get_transactions_by_rfid(db, rfid)
    if not transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return crud_transaction.update_transaction(db, transactions[0], transaction_data)


# -------------------------------
# DELETE TRANSACTION
# -------------------------------
@router.delete("/remove/{rfid}")
def delete_transaction_by_rfid(rfid: str, db: Session = Depends(get_db)):
    transactions = crud_transaction.get_transactions_by_rfid(db, rfid)
    if not transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    crud_transaction.delete_transaction(db, transactions[0])
    return {"message": "Transaction deleted successfully"}


# -------------------------------
# BULK UPDATE BY RFID
# -------------------------------
@router.put("/update-by-rfid-bulk")
def bulk_update_transaction(
    payload: BulkTransactionUpdateRequest, db: Session = Depends(get_db)
):
    if not payload.rfids:
        raise HTTPException(status_code=400, detail="RFID list cannot be empty")

    transactions, items = crud_transaction.bulk_update_transactions_and_items(
        db=db, rfids=payload.rfids, tx_type=payload.type, reason=payload.reason
    )

    if not transactions:
        raise HTTPException(
            status_code=404, detail="No transactions found for provided RFIDs"
        )

    return {
        "message": "Bulk RFID update completed successfully",
        "transaction_type": payload.type,
        "rfids_received": len(payload.rfids),
        "transactions_updated": len(transactions),
        "items_updated": len(items),
    }


@router.post("/inward/verify-rfids", response_model=BulkRFIDVerifyResponse)
def inward_bulk_rfids(payload: BulkRFIDVerifyRequest, db: Session = Depends(get_db)):
    if not payload.rfids:
        raise HTTPException(status_code=400, detail="RFID list cannot be empty")

    existing_rfids, missing_rfids = crud_transaction.inward_existing_rfids(
        db, payload.rfids
    )
    print(existing_rfids, missing_rfids)

    return BulkRFIDVerifyResponse(
        existing_rfids=existing_rfids, missing_rfids=missing_rfids
    )


@router.post("/outward/verify-rfids", response_model=BulkRFIDVerifyResponse)
def outward_bulk_rfids(payload: BulkRFIDVerifyRequest, db: Session = Depends(get_db)):
    if not payload.rfids:
        raise HTTPException(status_code=400, detail="RFID list cannot be empty")

    existing_rfids, missing_rfids = crud_transaction.outward_existing_rfids(
        db, payload.rfids
    )

    return BulkRFIDVerifyResponse(
        existing_rfids=existing_rfids, missing_rfids=missing_rfids
    )
