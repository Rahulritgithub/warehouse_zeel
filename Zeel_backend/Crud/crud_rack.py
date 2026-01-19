from sqlalchemy.orm import Session
from Models.rack import Rack
from Models.storage_bin import StorageBin


def create_rack(db: Session, rack_id: str, location: str):
    rack = Rack(rack_id=rack_id, location=location)
    db.add(rack)
    db.commit()
    db.refresh(rack)
    return rack


def get_all_racks(db: Session):
    return db.query(Rack).all()


def get_rack_by_id(db: Session, rack_id: str):
    return db.query(Rack).filter(Rack.rack_id == rack_id).first()


def update_rack(db: Session, rack: Rack, update_data: dict):
    for field, value in update_data.items():
        setattr(rack, field, value)

    db.commit()
    db.refresh(rack)
    return rack


def has_bins(db: Session, rack_id: str) -> bool:
    return (
        db.query(StorageBin).filter(StorageBin.rack_id == rack_id).first() is not None
    )


def delete_rack(db: Session, rack: Rack):
    db.delete(rack)
    db.commit()
