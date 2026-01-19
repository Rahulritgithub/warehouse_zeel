from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Database.database import get_db
from Schemas.sku import SKUCreate, SKUUpdate, SKUResponse
from Crud import crud_sku as sku_crud

router = APIRouter(prefix="/skus", tags=["SKU"])


@router.post("/add", response_model=SKUResponse, status_code=status.HTTP_201_CREATED)
def create_sku(sku: SKUCreate, db: Session = Depends(get_db)):
    if sku_crud.get_sku_by_code(db, sku.sku_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists"
        )

    return sku_crud.create_sku(db, sku.dict())


@router.get("/get_all", response_model=List[SKUResponse])
def get_all_skus(db: Session = Depends(get_db)):
    return sku_crud.get_all_skus(db)


@router.get("/get/{sku_id}", response_model=SKUResponse)
def get_sku(sku_id: int, db: Session = Depends(get_db)):
    sku = sku_crud.get_sku_by_id(db, sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found"
        )
    return sku


@router.put("/update/{sku_id}", response_model=SKUResponse)
def update_sku(sku_id: int, sku_update: SKUUpdate, db: Session = Depends(get_db)):
    sku = sku_crud.get_sku_by_id(db, sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found"
        )

    update_data = sku_update.dict(exclude_unset=True)
    return sku_crud.update_sku(db, sku, update_data)


@router.delete("/remove/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sku(sku_id: int, db: Session = Depends(get_db)):
    sku = sku_crud.get_sku_by_id(db, sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found"
        )

    if not sku_crud.can_delete_sku(sku):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete SKU with existing items",
        )

    sku_crud.delete_sku(db, sku)
    return None
