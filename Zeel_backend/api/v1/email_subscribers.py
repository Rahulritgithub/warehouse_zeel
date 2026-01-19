from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from Database.database import get_db
from Schemas.email_subscriber import EmailSubscriberCreate, EmailSubscriberResponse
from Crud import crud_email_subsriber as subscriber_crud
from Utils.email_service import send_email

router = APIRouter(prefix="/email-subscribers", tags=["Email Subscribers"])


@router.post("/add", response_model=EmailSubscriberResponse)
def add_email_subscriber(request: EmailSubscriberCreate, db: Session = Depends(get_db)):
    existing = subscriber_crud.get_by_email(db, request.email)

    if existing:
        return subscriber_crud.update_subscriber_status(db, existing, request.is_active)

    return subscriber_crud.create_subscriber(db, request.email, request.is_active)


@router.get("/all", response_model=List[EmailSubscriberResponse])
def get_all_subscribers(db: Session = Depends(get_db)):
    return subscriber_crud.get_all_subscribers(db)


@router.get("/active", response_model=List[EmailSubscriberResponse])
def get_active_subscribers(db: Session = Depends(get_db)):
    return subscriber_crud.get_active_subscribers(db)


@router.patch("/{email}/toggle")
def toggle_subscriber_status(email: str, active: bool, db: Session = Depends(get_db)):
    subscriber = subscriber_crud.get_by_email(db, email)

    if not subscriber:
        raise HTTPException(status_code=404, detail="Email subscriber not found")

    subscriber_crud.update_subscriber_status(db, subscriber, active)

    status_msg = "activated" if active else "deactivated"
    return {"message": f"Email subscriber {status_msg} successfully"}


@router.delete("/{email}")
def delete_subscriber(email: str, db: Session = Depends(get_db)):
    subscriber = subscriber_crud.get_by_email(db, email)

    if not subscriber:
        raise HTTPException(status_code=404, detail="Email subscriber not found")

    subscriber_crud.delete_subscriber(db, subscriber)
    return {"message": f"Email subscriber {email} removed successfully"}


@router.post("/{email}/test")
async def send_test_email(email: str, db: Session = Depends(get_db)):
    subscriber = subscriber_crud.get_by_email(db, email)

    if not subscriber:
        raise HTTPException(status_code=404, detail="Email subscriber not found")

    subject = "Test Email - Request Management System"
    body = f"""
    TEST EMAIL

    Your email ({email}) is successfully subscribed
    to receive daily summaries.
    """

    success = await send_email(email, subject, body)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send test email")

    return {"message": f"Test email sent successfully to {email}"}


@router.post("/broadcast/{timeslot}")
async def trigger_manual_broadcast(timeslot: str):
    if timeslot not in ["morning", "evening"]:
        raise HTTPException(
            status_code=400, detail="Timeslot must be 'morning' or 'evening'"
        )

    from scheduler import send_daily_summary_to_all

    result = await send_daily_summary_to_all(timeslot)

    return {"message": f"Manual {timeslot} broadcast completed", "result": result}
