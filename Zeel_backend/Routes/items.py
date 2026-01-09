from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from Database.database import get_db
from Models.items import Item
from Models.rack import Rack
from Models.storage_bin import StorageBin
from Schemas.items import ItemCreate, ItemUpdate, ItemResponse
from Models.sku import SKU


router = APIRouter(prefix="/items", tags=["Items"])


# ----------------------------
# CREATE ITEM
# ----------------------------
@router.post("/add", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):

    if db.query(Item).filter(Item.rfid == item.rfid).first():
        raise HTTPException(status_code=400, detail="RFID already exists")

    sku = db.query(SKU).filter(SKU.id == item.sku_id).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    if not db.query(Rack).filter(Rack.rack_id == item.rack_id).first():
        raise HTTPException(status_code=404, detail="Rack not found")

    if not db.query(StorageBin).filter(
        StorageBin.rfid == item.storage_bin_rfid
    ).first():
        raise HTTPException(status_code=404, detail="Storage Bin not found")

    new_item = Item(
        rfid=item.rfid,
        sku_id=item.sku_id,
        rack_id=item.rack_id,
        storage_bin_rfid=item.storage_bin_rfid
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item




# ----------------------------
# READ ALL ITEMS
# ----------------------------
@router.get("/get_all", response_model=List[ItemResponse])
def get_all_items(
    db: Session = Depends(get_db),
    rack_id: Optional[str] = None,
    storage_bin_rfid: Optional[int] = None
):
    query = db.query(Item)

    if rack_id:
        query = query.filter(Item.rack_id == rack_id)
    if storage_bin_rfid:
        query = query.filter(Item.storage_bin_rfid == storage_bin_rfid)

    return query.all()


# ----------------------------
# READ ITEM BY RFID
# ----------------------------
@router.get("/get/{rfid}", response_model=ItemResponse)
def get_item_by_rfid(rfid: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.rfid == rfid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# ----------------------------
# UPDATE ITEM BY RFID
# ----------------------------
@router.put("/update/{rfid}", response_model=ItemResponse)
def update_item(rfid: str, item_update: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.rfid == rfid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update only provided fields
    if item_update.rfid is not None and item_update.rfid != rfid:
        duplicate = db.query(Item).filter(Item.rfid == item_update.rfid).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="RFID already exists")
        item.rfid = item_update.rfid

    if item_update.rack_id:
        rack = db.query(Rack).filter(Rack.rack_id == item_update.rack_id).first()
        if not rack:
            raise HTTPException(status_code=404, detail="Rack not found")
        item.rack_id = item_update.rack_id

    if item_update.storage_bin_rfid is not None:
        bin_ = db.query(StorageBin).filter(StorageBin.id == item_update.storage_bin_id).first()
        if not bin_:
            raise HTTPException(status_code=404, detail="Storage Bin not found")
        item.storage_bin_rfid = item_update.storage_bin_rfid

    db.commit()
    db.refresh(item)
    return item


# ----------------------------
# DELETE ITEM BY RFID
# ----------------------------
@router.delete("/remove/{rfid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(rfid: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.rfid == rfid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return None
