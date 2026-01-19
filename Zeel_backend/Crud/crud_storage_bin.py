from sqlalchemy.orm import Session
from Models.storage_bin import StorageBin


def get_storage_bin_by_rfid(db: Session, rfid: str):
    return db.query(StorageBin).filter(StorageBin.rfid == rfid).first()


def get_all_storage_bins(db: Session, skip: int = 0, limit: int = 100):
    return db.query(StorageBin).offset(skip).limit(limit).all()


def create_storage_bin(db: Session, rfid: str, rack_id: int, capacity: int):
    new_bin = StorageBin(rfid=rfid, rack_id=rack_id, capacity=capacity)
    db.add(new_bin)
    db.commit()
    db.refresh(new_bin)
    return new_bin


def update_storage_bin(db: Session, storage_bin: StorageBin, update_data: dict):
    for key, value in update_data.items():
        setattr(storage_bin, key, value)

    db.commit()
    db.refresh(storage_bin)
    return storage_bin


def delete_storage_bin(db: Session, storage_bin: StorageBin):
    db.delete(storage_bin)
    db.commit()
