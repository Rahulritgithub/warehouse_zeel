# Routes/request.py

from datetime import timezone
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Database.database import get_db
from Models.request import Request
from Schemas.request import RequestCreate, RequestResponse

router = APIRouter(prefix="/requests", tags=["Requests"])


# -----------------------------------
# CREATE REQUEST
# -----------------------------------
@router.post("/add", response_model=RequestResponse)
def create_request(request_data: RequestCreate, db: Session = Depends(get_db)):

    # If request_date has no tzinfo, assume IST
    req_date = request_data.request_date
    if req_date.tzinfo is None:
        req_date = req_date.replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    # Convert to UTC before storing
    req_date_utc = req_date.astimezone(timezone.utc)

    new_req = Request(
        req_from=request_data.req_from,
        req_to=request_data.req_to,
        description=request_data.description,
        request_date=req_date_utc
    )

    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req


# -----------------------------------
# GET ALL REQUESTS
# -----------------------------------
@router.get("/get_all", response_model=list[RequestResponse])
def get_all_requests(db: Session = Depends(get_db)):
    return db.query(Request).all()


# -----------------------------------
# GET REQUEST BY ID
# -----------------------------------
@router.get("/get/{request_id}", response_model=RequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    return req


# -----------------------------------
# DELETE REQUEST
# -----------------------------------
@router.delete("/remove/{request_id}")
def delete_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    db.delete(req)
    db.commit()

    return {"message": "Request deleted successfully"}
