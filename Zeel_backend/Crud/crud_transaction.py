from sqlalchemy.orm import Session
from Models.transaction import Transaction, TransactionType
from Models.storage_bin import StorageBin
from Models.items import Item, ItemTrackStatus


# -------------------------------
# HELPERS
# -------------------------------
def storage_bin_exists(db: Session, rfid: str):
    return db.query(StorageBin).filter(StorageBin.rfid == rfid).first()


def transaction_exists_for_bin(db: Session, rfid: str):
    return db.query(Transaction).filter(Transaction.storage_bin_rfid == rfid).first()


# -------------------------------
# CREATE
# -------------------------------
def create_transaction(db: Session, transaction_data):
    new_tx = Transaction(
        type=transaction_data.type,
        storage_bin_rfid=transaction_data.storage_bin_rfid,
        reason=transaction_data.reason,
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx


# -------------------------------
# READ
# -------------------------------
def get_all_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).offset(skip).limit(limit).all()


def get_transactions_by_rfid(db: Session, rfid: str):
    return db.query(Transaction).filter(Transaction.storage_bin_rfid == rfid).all()


def get_items_by_storage_bin(db: Session, rfid: str):
    return db.query(Item.rfid).filter(Item.storage_bin_rfid == rfid).all()


# -------------------------------
# UPDATE
# -------------------------------
def update_transaction(db: Session, transaction: Transaction, transaction_data):
    transaction.type = transaction_data.type
    transaction.storage_bin_rfid = transaction_data.storage_bin_rfid
    transaction.reason = transaction_data.reason

    db.commit()
    db.refresh(transaction)
    return transaction


def bulk_update_transactions_and_items(
    db: Session, rfids: list[str], tx_type: TransactionType, reason: str
):
    transactions = (
        db.query(Transaction).filter(Transaction.storage_bin_rfid.in_(rfids)).all()
    )

    track_map = {
        TransactionType.INWARD: ItemTrackStatus.INWARD,
        TransactionType.OUTWARD: ItemTrackStatus.OUTWARD,
        TransactionType.RETURN: ItemTrackStatus.RETURN,
    }

    new_track = track_map[tx_type]
    updated_rfids = set()

    for tx in transactions:
        tx.type = tx_type
        tx.reason = reason
        updated_rfids.add(tx.storage_bin_rfid)

    items = db.query(Item).filter(Item.storage_bin_rfid.in_(updated_rfids)).all()

    for item in items:
        item.track = new_track

    db.commit()
    return transactions, items


# -------------------------------
# check existing and missing RFIDs for inward
# -------------------------------


def inward_existing_rfids(db: Session, rfids: list[str]):
    # Query only RFIDs that exist in Item table
    items = (
        db.query(Item.rfid).filter(Item.rfid.in_(rfids), Item.track == "INWARD").all()
    )
    existing_rfids = [item.rfid for item in items]

    # Compute missing RFIDs
    missing_rfids = list(set(rfids) - set(existing_rfids))

    return existing_rfids, missing_rfids


# -------------------------------
# check existing and missing RFIDs for outward
# -------------------------------


def return_existing_rfids(db: Session, rfids: list[str]):
    # Query only RFIDs that exist in Item table
    items = (
        db.query(Item.rfid).filter(Item.rfid.in_(rfids), Item.track == "OUTWARD").all()
    )
    existing_rfids = [item.rfid for item in items]

    # Compute missing RFIDs
    missing_rfids = list(set(rfids) - set(existing_rfids))

    return existing_rfids, missing_rfids


# -------------------------------
# DELETE
# -------------------------------
def delete_transaction(db: Session, transaction: Transaction):
    db.delete(transaction)
    db.commit()
