from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from Database.database import get_db
from Models.email_subscriber import EmailSubscriber
from Schemas.email_subscriber import EmailSubscriberCreate, EmailSubscriberResponse
import asyncio
from scheduler import get_todays_requests
from Utils.email_service import send_email

router = APIRouter(prefix="/email-subscribers", tags=["Email Subscribers"])

# -----------------------------------
# ADD EMAIL SUBSCRIBER
# -----------------------------------
@router.post("/add", response_model=EmailSubscriberResponse)
def add_email_subscriber(
    subscriber_data: EmailSubscriberCreate,
    db: Session = Depends(get_db)
):
    """Add a new email to receive daily summaries"""
    
    # Check if email already exists
    existing = db.query(EmailSubscriber).filter(
        EmailSubscriber.email == subscriber_data.email
    ).first()
    
    if existing:
        # Update existing subscriber
        existing.is_active = subscriber_data.is_active
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new subscriber
    new_subscriber = EmailSubscriber(
        email=subscriber_data.email,
        is_active=subscriber_data.is_active
    )
    
    db.add(new_subscriber)
    db.commit()
    db.refresh(new_subscriber)
    
    return new_subscriber

# -----------------------------------
# GET ALL SUBSCRIBERS
# -----------------------------------
@router.get("/all", response_model=List[EmailSubscriberResponse])
def get_all_subscribers(db: Session = Depends(get_db)):
    """Get all email subscribers"""
    return db.query(EmailSubscriber).all()

# -----------------------------------
# GET ACTIVE SUBSCRIBERS
# -----------------------------------
@router.get("/active", response_model=List[EmailSubscriberResponse])
def get_active_subscribers(db: Session = Depends(get_db)):
    """Get only active email subscribers"""
    return db.query(EmailSubscriber).filter(
        EmailSubscriber.is_active == True
    ).all()

# -----------------------------------
# UPDATE SUBSCRIBER STATUS
# -----------------------------------
@router.patch("/{email}/toggle")
def toggle_subscriber_status(
    email: str,
    active: bool,
    db: Session = Depends(get_db)
):
    """Enable/disable email subscriber"""
    subscriber = db.query(EmailSubscriber).filter(
        EmailSubscriber.email == email
    ).first()
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="Email subscriber not found")
    
    subscriber.is_active = active
    db.commit()
    db.refresh(subscriber)
    
    status = "activated" if active else "deactivated"
    return {"message": f"Email subscriber {status} successfully"}

# -----------------------------------
# DELETE SUBSCRIBER
# -----------------------------------
@router.delete("/{email}")
def delete_subscriber(email: str, db: Session = Depends(get_db)):
    """Remove email subscriber"""
    subscriber = db.query(EmailSubscriber).filter(
        EmailSubscriber.email == email
    ).first()
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="Email subscriber not found")
    
    db.delete(subscriber)
    db.commit()
    
    return {"message": f"Email subscriber {email} removed successfully"}

# -----------------------------------
# SEND TEST EMAIL TO SUBSCRIBER
# -----------------------------------
@router.post("/{email}/test")
async def send_test_email_to_subscriber(email: str, db: Session = Depends(get_db)):
    """Send a test email to a specific subscriber"""
    # Verify subscriber exists
    subscriber = db.query(EmailSubscriber).filter(
        EmailSubscriber.email == email
    ).first()
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="Email subscriber not found")
    
    subject = "Test Email - Request Management System"
    
    body = f"""
    =================================
    TEST EMAIL
    =================================
    
    This is a test email from the
    Request Management System.
    
    Your email ({email}) is successfully
    subscribed to receive daily summaries.
    
    You will receive:
    • Morning summary at 9:00 AM IST
    • Evening summary at 5:00 PM IST
    
    =================================
    If you did not subscribe, please
    contact the administrator.
    =================================
    """
    
    success = await send_email(email, subject, body)
    
    if success:
        return {"message": f"Test email sent successfully to {email}"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send test email"
        )

# -----------------------------------
# MANUALLY TRIGGER DAILY SUMMARY
# -----------------------------------
@router.post("/broadcast/{timeslot}")
async def trigger_manual_broadcast(timeslot: str):
    """Manually trigger daily summary broadcast"""
    if timeslot not in ["morning", "evening"]:
        raise HTTPException(
            status_code=400,
            detail="Timeslot must be 'morning' or 'evening'"
        )
    
    from scheduler import send_daily_summary_to_all
    result = await send_daily_summary_to_all(timeslot)
    
    return {
        "message": f"Manual {timeslot} broadcast completed",
        "result": result
    }