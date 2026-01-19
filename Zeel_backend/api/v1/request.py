from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Database.database import get_db
from Schemas.request import RequestCreate, RequestResponse
from Crud import crud_request as request_crud

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "/add", response_model=RequestResponse, status_code=status.HTTP_201_CREATED
)
def create_request(request_data: RequestCreate, db: Session = Depends(get_db)):
    return request_crud.create_request(db, request_data)


@router.get("/get_all", response_model=List[RequestResponse])
def get_all_requests(db: Session = Depends(get_db)):
    return request_crud.get_all_requests(db)


@router.get("/get/{request_id}", response_model=RequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = request_crud.get_request_by_id(db, request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request not found"
        )
    return req


@router.delete("/remove/{request_id}", status_code=status.HTTP_200_OK)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    req = request_crud.get_request_by_id(db, request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request not found"
        )

    request_crud.delete_request(db, req)
    return {"message": "Request deleted successfully"}
