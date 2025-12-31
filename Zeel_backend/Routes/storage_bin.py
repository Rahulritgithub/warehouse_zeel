from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from Database.database import get_db
from Models.storage_bin import StorageBin
from Schemas.storage_bin import StorageBinCreate, StorageBinUpdate, StorageBinResponse

router = APIRouter(prefix="/storage_bins", tags=["StorageBins"]
)

# ----------------------------
# CREATE StorageBin
# ----------------------------
@router.post("/add", response_model=StorageBinResponse)
def create_storage_bin(storage_bin: StorageBinCreate, db: Session = Depends(get_db)):
    # Check if RFID already exists
    existing_bin = db.query(StorageBin).filter(StorageBin.rfid == storage_bin.rfid).first()
    if existing_bin:
        raise HTTPException(status_code=400, detail="RFID already exists")
    
    new_bin = StorageBin(rfid=storage_bin.rfid, rack_id=storage_bin.rack_id)
    db.add(new_bin)
    db.commit()
    db.refresh(new_bin)
    return new_bin

# ----------------------------
# READ all StorageBins
# ----------------------------
@router.get("/get_all", response_model=List[StorageBinResponse])
def get_all_storage_bins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bins = db.query(StorageBin).offset(skip).limit(limit).all()
    return bins

# ----------------------------
# READ StorageBin by ID
# ----------------------------
@router.get("/{bin_id}", response_model=StorageBinResponse)
def get_storage_bin(rfid: str, db: Session = Depends(get_db)):
    storage_bin = db.query(StorageBin).filter(StorageBin.rfid == rfid).first()
    if not storage_bin:
        raise HTTPException(status_code=404, detail="StorageBin not found")
    return storage_bin

# ----------------------------
# UPDATE StorageBin
# ----------------------------
@router.put("/update/{bin_id}", response_model=StorageBinResponse)
def update_storage_bin(rfid: str, storage_bin_update: StorageBinUpdate, db: Session = Depends(get_db)):
    storage_bin = db.query(StorageBin).filter(StorageBin.rfid == rfid).first()
    if not storage_bin:
        raise HTTPException(status_code=404, detail="StorageBin not found")
    
    storage_bin.rfid = storage_bin_update.rfid
    storage_bin.rack_id = storage_bin_update.rack_id
    db.commit()
    db.refresh(storage_bin)
    return storage_bin

# ----------------------------
# DELETE StorageBin
# ----------------------------
@router.delete("/remove/{rfid}", status_code=200)
def delete_storage_bin(rfid: str, db: Session = Depends(get_db)):
    storage_bin = db.query(StorageBin).filter(StorageBin.rfid == rfid).first()
    if not storage_bin:
        raise HTTPException(status_code=404, detail="StorageBin not found")
    
    db.delete(storage_bin)
    db.commit()
    return {"message": "deleted"}

