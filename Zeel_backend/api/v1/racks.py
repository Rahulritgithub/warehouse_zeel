from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Database.database import get_db
from Schemas.rack import RackCreate, RackUpdate, RackResponse
from Crud import crud_rack as rack_crud

router = APIRouter(prefix="/racks", tags=["Racks"])


@router.post("/add", response_model=RackResponse, status_code=status.HTTP_201_CREATED)
def create_rack(rack: RackCreate, db: Session = Depends(get_db)):
    return rack_crud.create_rack(db, rack_id=rack.rack_id, location=rack.location)


@router.get("/get_all", response_model=List[RackResponse])
def get_all_racks(db: Session = Depends(get_db)):
    return rack_crud.get_all_racks(db)


@router.get("/{rack_id}", response_model=RackResponse)
def get_rack_by_id(rack_id: str, db: Session = Depends(get_db)):
    rack = rack_crud.get_rack_by_id(db, rack_id)
    if not rack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rack not found"
        )
    return rack


@router.put("/update/{rack_id}", response_model=RackResponse)
def update_rack(rack_id: str, rack_update: RackUpdate, db: Session = Depends(get_db)):
    rack = rack_crud.get_rack_by_id(db, rack_id)
    if not rack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rack not found"
        )

    update_data = rack_update.dict(exclude_unset=True)
    return rack_crud.update_rack(db, rack, update_data)


@router.delete("/remove/{rack_id}", status_code=status.HTTP_200_OK)
def delete_rack(rack_id: str, db: Session = Depends(get_db)):
    rack = rack_crud.get_rack_by_id(db, rack_id)
    if not rack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rack not found"
        )

    if rack_crud.has_bins(db, rack_id):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Rack is not empty"
        )

    rack_crud.delete_rack(db, rack)
    return {"message": "Rack deleted successfully"}
