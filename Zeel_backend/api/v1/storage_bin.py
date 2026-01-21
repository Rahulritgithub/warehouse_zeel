from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from Database.database import get_db
from Schemas.storage_bin import StorageBinCreate, StorageBinUpdate, StorageBinResponse
from Crud import crud_storage_bin as crud_storage_bin

from Services.storage_bin_cache import (
    get_storage_bin_cache,
    set_storage_bin_cache,
    delete_storage_bin_cache,
    delete_storage_bin_list_cache,
)

router = APIRouter(prefix="/storage_bins", tags=["StorageBins"])


# ----------------------------
# CREATE StorageBin
# ----------------------------
@router.post("/add", response_model=StorageBinResponse)
def create_storage_bin(storage_bin: StorageBinCreate, db: Session = Depends(get_db)):

    if crud_storage_bin.get_storage_bin_by_rfid(db, storage_bin.rfid):
        raise HTTPException(status_code=400, detail="RFID already exists")

    if storage_bin.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be greater than 0")

    new_bin = crud_storage_bin.create_storage_bin(
        db=db,
        rfid=storage_bin.rfid,
        rack_id=storage_bin.rack_id,
        capacity=storage_bin.capacity,
    )

    # Invalidate list cache
    delete_storage_bin_list_cache()

    return new_bin


# ----------------------------
# READ all StorageBins
# ----------------------------
@router.get("/get_all", response_model=List[StorageBinResponse])
def get_all_storage_bins(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    cache_key = f"storage_bins:{skip}:{limit}"

    cached_bins = get_storage_bin_cache(cache_key)
    if cached_bins:
        return cached_bins

    bins = crud_storage_bin.get_all_storage_bins(db, skip, limit)

    #  Cache serialized data
    set_storage_bin_cache(cache_key, bins)

    return bins


# ----------------------------
# READ StorageBin by RFID
# ----------------------------
@router.get("/{rfid}", response_model=StorageBinResponse)
def get_storage_bin(rfid: str, db: Session = Depends(get_db)):

    cached_bin = get_storage_bin_cache(rfid)
    if cached_bin:
        return cached_bin

    storage_bin = crud_storage_bin.get_storage_bin_by_rfid(db, rfid)
    if not storage_bin:
        raise HTTPException(status_code=404, detail="StorageBin not found")

    set_storage_bin_cache(rfid, storage_bin)

    return storage_bin


# ----------------------------
# UPDATE StorageBin
# ----------------------------
@router.put("/update/{rfid}", response_model=StorageBinResponse)
def update_storage_bin(
    rfid: str, storage_bin_update: StorageBinUpdate, db: Session = Depends(get_db)
):
    storage_bin = crud_storage_bin.get_storage_bin_by_rfid(db, rfid)
    if not storage_bin:
        raise HTTPException(status_code=404, detail="StorageBin not found")

    update_data = storage_bin_update.dict(exclude_unset=True)

    if "rfid" in update_data and update_data["rfid"] != rfid:
        if crud_storage_bin.get_storage_bin_by_rfid(db, update_data["rfid"]):
            raise HTTPException(status_code=400, detail="RFID already exists")
        delete_storage_bin_cache(rfid)

    if "capacity" in update_data and update_data["capacity"] <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be greater than 0")

    updated_bin = crud_storage_bin.update_storage_bin(db, storage_bin, update_data)

    set_storage_bin_cache(updated_bin.rfid, updated_bin)
    delete_storage_bin_list_cache()

    return updated_bin


# ----------------------------
# DELETE StorageBin
# ----------------------------
@router.delete("/remove/{rfid}")
def delete_storage_bin(rfid: str, db: Session = Depends(get_db)):
    storage_bin = crud_storage_bin.get_storage_bin_by_rfid(db, rfid)
    if not storage_bin:
        raise HTTPException(status_code=404, detail="StorageBin not found")

    crud_storage_bin.delete_storage_bin(db, storage_bin)

    # Remove cache
    delete_storage_bin_cache(rfid)
    delete_storage_bin_list_cache()

    return {"message": "Storage bin deleted successfully"}
