from sqlalchemy.orm import Session
from Models.sku import SKU


def get_sku_by_code(db: Session, sku_code: str):
    return db.query(SKU).filter(SKU.sku_code == sku_code).first()


def get_sku_by_id(db: Session, sku_id: int):
    return db.query(SKU).filter(SKU.id == sku_id).first()


def get_all_skus(db: Session):
    return db.query(SKU).all()


def create_sku(db: Session, sku_data: dict):
    sku = SKU(**sku_data)
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku


def update_sku(db: Session, sku: SKU, update_data: dict):
    for key, value in update_data.items():
        setattr(sku, key, value)

    db.commit()
    db.refresh(sku)
    return sku


def can_delete_sku(sku: SKU) -> bool:
    return not bool(sku.items)


def delete_sku(db: Session, sku: SKU):
    db.delete(sku)
    db.commit()
