from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from Database.database import get_db
from Schemas.items import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemBulkCreate,
    ItemTrackUpdate,
    ItemFilter,
)
from Models.items import ItemTrackStatus
from Crud import crud_items as items_crud

router = APIRouter(prefix="/items", tags=["Items"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    if items_crud.get_item_by_rfid(db, item.rfid):
        raise HTTPException(status_code=400, detail="RFID already exists")

    return items_crud.create_item(db, item.dict())


@router.post("/bulk_upload", response_model=List[ItemResponse])
def bulk_upload(items: ItemBulkCreate, db: Session = Depends(get_db)):
    items_data = [
        {
            "rfid": rfid,
            "sku_id": items.sku_id,
            "rack_id": items.rack_id,
            "storage_bin_rfid": items.storage_bin_rfid,
            "track": items.track,
        }
        for rfid in items.rfids
    ]

    return items_crud.bulk_create_items(db, items_data)


@router.get("/", response_model=List[ItemResponse])
def get_items(
    skip: int = 0,
    limit: int = 100,
    track: Optional[ItemTrackStatus] = None,
    status: Optional[str] = None,
    sku_id: Optional[int] = None,
    rack_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return items_crud.get_items(db, skip, limit, track, status, sku_id, rack_id)


@router.post("/filter", response_model=List[ItemResponse])
def filter_items(filters: ItemFilter, db: Session = Depends(get_db)):
    return items_crud.filter_items(db, filters)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = items_crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/rfid/{rfid}", response_model=ItemResponse)
def get_item_by_rfid(rfid: str, db: Session = Depends(get_db)):
    item = items_crud.get_item_by_rfid(db, rfid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    item = items_crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return items_crud.update_item(db, item, item_update.dict(exclude_unset=True))


@router.patch("/{item_id}/track", response_model=ItemResponse)
def update_item_track(
    item_id: int, track_update: ItemTrackUpdate, db: Session = Depends(get_db)
):
    item = items_crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return items_crud.update_item_track(
        db,
        item,
        track_update.track,
        track_update.rack_id,
        track_update.storage_bin_rfid,
    )


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = items_crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    items_crud.delete_item(db, item)
    return {"message": "Item deleted successfully"}
