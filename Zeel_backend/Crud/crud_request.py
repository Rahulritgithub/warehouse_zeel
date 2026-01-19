from datetime import timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from Models.request import Request


def create_request(db: Session, request_data):
    # If request_date has no tzinfo, assume IST
    req_date = request_data.request_date
    if req_date.tzinfo is None:
        req_date = req_date.replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    # Convert to UTC before storing
    req_date_utc = req_date.astimezone(timezone.utc)

    new_request = Request(
        req_from=request_data.req_from,
        req_to=request_data.req_to,
        description=request_data.description,
        request_date=req_date_utc,
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


def get_all_requests(db: Session):
    return db.query(Request).all()


def get_request_by_id(db: Session, request_id: int):
    return db.query(Request).filter(Request.id == request_id).first()


def delete_request(db: Session, request: Request):
    db.delete(request)
    db.commit()
