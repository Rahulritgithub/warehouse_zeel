from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from Database.database import get_db
from Models.items import Item, ItemTrackStatus
from Schemas.items import (
    ItemCreate, 
    ItemUpdate, 
    ItemResponse, 
    ItemBulkCreate,
    ItemTrackUpdate,
    ItemFilter
)

router = APIRouter(prefix="/items", tags=["items"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    try:
        # Check if RFID already exists
        existing_item = db.query(Item).filter(Item.rfid == item.rfid).first()
        if existing_item:
            raise HTTPException(status_code=400, detail="RFID already exists")
        
        db_item = Item(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=List[ItemResponse])
def create_items_bulk(items: ItemBulkCreate, db: Session = Depends(get_db)):
    """Create multiple items in bulk"""
    try:
        created_items = []
        
        for rfid in items.rfids:
            # Check if RFID already exists
            existing_item = db.query(Item).filter(Item.rfid == rfid).first()
            if existing_item:
                continue  # Skip existing RFIDs
            
            item_data = {
                "rfid": rfid,
                "sku_id": items.sku_id,
                "rack_id": items.rack_id,
                "storage_bin_rfid": items.storage_bin_rfid,
                "track": items.track
            }
            
            db_item = Item(**item_data)
            db.add(db_item)
            created_items.append(db_item)
        
        db.commit()
        
        # Refresh all created items
        for item in created_items:
            db.refresh(item)
        
        return created_items
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating bulk items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ItemResponse])
def get_items(
    skip: int = 0, 
    limit: int = 100,
    track: Optional[ItemTrackStatus] = None,
    status: Optional[str] = None,
    sku_id: Optional[int] = None,
    rack_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all items with optional filters"""
    try:
        query = db.query(Item)
        
        # Apply filters
        if track:
            query = query.filter(Item.track == track)
        if status:
            query = query.filter(Item.status == status)
        if sku_id:
            query = query.filter(Item.sku_id == sku_id)
        if rack_id:
            query = query.filter(Item.rack_id == rack_id)
        
        items = query.offset(skip).limit(limit).all()
        return items
    except Exception as e:
        logger.error(f"Error getting items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filter", response_model=List[ItemResponse])
def filter_items(filter_data: ItemFilter, db: Session = Depends(get_db)):
    """Filter items with complex criteria"""
    try:
        query = db.query(Item)
        
        # Apply filters
        if filter_data.track:
            query = query.filter(Item.track == filter_data.track)
        if filter_data.status:
            query = query.filter(Item.status == filter_data.status)
        if filter_data.sku_id:
            query = query.filter(Item.sku_id == filter_data.sku_id)
        if filter_data.rack_id:
            query = query.filter(Item.rack_id == filter_data.rack_id)
        
        items = query.all()
        return items
    except Exception as e:
        logger.error(f"Error filtering items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rfid/{rfid}", response_model=ItemResponse)
def get_item_by_rfid(rfid: str, db: Session = Depends(get_db)):
    """Get item by RFID"""
    try:
        item = db.query(Item).filter(Item.rfid == rfid).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        logger.error(f"Error getting item by RFID {rfid}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item"""
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Update fields
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{item_id}/track", response_model=ItemResponse)
def update_item_track(item_id: int, track_update: ItemTrackUpdate, db: Session = Depends(get_db)):
    """Update item track status with optional location update"""
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Update track status
        db_item.track = track_update.track
        
        # Update location if provided
        if track_update.rack_id:
            db_item.rack_id = track_update.rack_id
        if track_update.storage_bin_rfid:
            db_item.storage_bin_rfid = track_update.storage_bin_rfid
        
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating item track {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/rfid/{rfid}/track", response_model=ItemResponse)
def update_item_track_by_rfid(rfid: str, track_update: ItemTrackUpdate, db: Session = Depends(get_db)):
    """Update item track status by RFID"""
    try:
        db_item = db.query(Item).filter(Item.rfid == rfid).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Update track status
        db_item.track = track_update.track
        
        # Update location if provided
        if track_update.rack_id:
            db_item.rack_id = track_update.rack_id
        if track_update.storage_bin_rfid:
            db_item.storage_bin_rfid = track_update.storage_bin_rfid
        
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating item track by RFID {rfid}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track/{track_status}", response_model=List[ItemResponse])
def get_items_by_track(track_status: ItemTrackStatus, db: Session = Depends(get_db)):
    """Get all items by track status"""
    try:
        items = db.query(Item).filter(Item.track == track_status).all()
        return items
    except Exception as e:
        logger.error(f"Error getting items by track {track_status}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        db.delete(db_item)
        db.commit()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))