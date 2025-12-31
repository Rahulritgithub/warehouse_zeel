from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from Database.database import get_db
from Models.rack import Rack
from Models.storage_bin import StorageBin
from Schemas.rack import RackCreate, RackUpdate, RackResponse
from typing import List

router = APIRouter(prefix="/racks", tags=["Racks"])


# Create rack
@router.post("/add", response_model=RackResponse, status_code=status.HTTP_201_CREATED)
def create_rack(rack: RackCreate, db: Session = Depends(get_db)):
    db_rack = Rack(
        rack_id=rack.rack_id,
        location=rack.location
    )
    db.add(db_rack)
    db.commit()
    db.refresh(db_rack)
    return db_rack


# Get all racks
@router.get("/get_all", response_model=List[RackResponse])
def get_all_racks(db: Session = Depends(get_db)):
    return db.query(Rack).all()


# Get rack by ID
@router.get("/{rack_id}", response_model=RackResponse)
def get_rack_by_id(rack_id: str, db: Session = Depends(get_db)):
    rack = db.query(Rack).filter(Rack.rack_id == rack_id).first()
    if not rack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rack not found")
    return rack


# Update rack
@router.put("/update/{rack_id}", response_model=RackResponse)
def update_rack(rack_id: str, rack_update: RackUpdate, db: Session = Depends(get_db)):
    rack = db.query(Rack).filter(Rack.rack_id == rack_id).first()
    if not rack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rack not found")

    if rack_update.location:
        rack.location = rack_update.location
    if rack_update.rack_id:
        rack.rack_id = rack_update.rack_id

    db.commit()
    db.refresh(rack)
    return rack


@router.delete("/remove/{rack_id}", status_code=200)
def delete_rack(rack_id: str, db: Session = Depends(get_db)):
    rack = db.query(Rack).filter(Rack.rack_id == rack_id).first()
    if not rack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rack not found"
        )

    # Check if any bin is present in this rack
    bins_in_rack = db.query(StorageBin).filter(StorageBin.rack_id == rack_id).first()

    if bins_in_rack:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Rack is not empty"
        )

    db.delete(rack)
    db.commit()

    return {"message": "Rack deleted successfully"}

