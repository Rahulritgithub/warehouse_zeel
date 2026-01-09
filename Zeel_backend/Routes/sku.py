from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Database.database import get_db
from Models.sku import SKU
from Schemas.sku import SKUCreate, SKUUpdate, SKUResponse

router = APIRouter(prefix="/skus", tags=["SKU"])


@router.post("/add", response_model=SKUResponse, status_code=status.HTTP_201_CREATED)
def create_sku(sku: SKUCreate, db: Session = Depends(get_db)):

    if db.query(SKU).filter(SKU.sku_code == sku.sku_code).first():
        raise HTTPException(status_code=400, detail="SKU already exists")

    new_sku = SKU(**sku.dict())
    db.add(new_sku)
    db.commit()
    db.refresh(new_sku)
    return new_sku


@router.get("/get_all", response_model=List[SKUResponse])
def get_all_skus(db: Session = Depends(get_db)):
    return db.query(SKU).all()


@router.get("/get/{sku_id}", response_model=SKUResponse)
def get_sku(sku_id: int, db: Session = Depends(get_db)):
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku


@router.put("/update/{sku_id}", response_model=SKUResponse)
def update_sku(sku_id: int, sku_update: SKUUpdate, db: Session = Depends(get_db)):

    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    for key, value in sku_update.dict(exclude_unset=True).items():
        setattr(sku, key, value)

    db.commit()
    db.refresh(sku)
    return sku


@router.delete("/remove/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sku(sku_id: int, db: Session = Depends(get_db)):

    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    if sku.items:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete SKU with existing items"
        )

    db.delete(sku)
    db.commit()
    return None
