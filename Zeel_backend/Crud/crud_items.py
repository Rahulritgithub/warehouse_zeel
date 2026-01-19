from sqlalchemy.orm import Session
from typing import List, Optional
from Models.items import Item, ItemTrackStatus
from Schemas.items import ItemFilter


# ---------- CREATE ----------


def get_item_by_rfid(db: Session, rfid: str):
    return db.query(Item).filter(Item.rfid == rfid).first()


def get_item_by_id(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()


def create_item(db: Session, item_data: dict):
    item = Item(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def bulk_create_items(db: Session, items_data: List[dict]):
    created_items = []

    for data in items_data:
        if get_item_by_rfid(db, data["rfid"]):
            continue
        item = Item(**data)
        db.add(item)
        created_items.append(item)

    db.commit()
    for item in created_items:
        db.refresh(item)

    return created_items


# ---------- READ ----------


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    track: Optional[ItemTrackStatus] = None,
    status: Optional[str] = None,
    sku_id: Optional[int] = None,
    rack_id: Optional[str] = None,
):
    query = db.query(Item)

    if track:
        query = query.filter(Item.track == track)
    if status:
        query = query.filter(Item.status == status)
    if sku_id:
        query = query.filter(Item.sku_id == sku_id)
    if rack_id:
        query = query.filter(Item.rack_id == rack_id)

    return query.offset(skip).limit(limit).all()


def filter_items(db: Session, filters: ItemFilter):
    query = db.query(Item)

    if filters.track:
        query = query.filter(Item.track == filters.track)
    if filters.status:
        query = query.filter(Item.status == filters.status)
    if filters.sku_id:
        query = query.filter(Item.sku_id == filters.sku_id)
    if filters.rack_id:
        query = query.filter(Item.rack_id == filters.rack_id)

    return query.all()


def get_items_by_track(db: Session, track: ItemTrackStatus):
    return db.query(Item).filter(Item.track == track).all()


# ---------- UPDATE ----------


def update_item(db: Session, item: Item, update_data: dict):
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def update_item_track(
    db: Session,
    item: Item,
    track: ItemTrackStatus,
    rack_id: Optional[str] = None,
    storage_bin_rfid: Optional[str] = None,
):
    item.track = track

    if rack_id:
        item.rack_id = rack_id
    if storage_bin_rfid:
        item.storage_bin_rfid = storage_bin_rfid

    db.commit()
    db.refresh(item)
    return item


# ---------- DELETE ----------


def delete_item(db: Session, item: Item):
    db.delete(item)
    db.commit()
