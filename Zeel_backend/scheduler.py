import asyncio
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from Database.database import SessionLocal
from Models.email_subscriber import EmailSubscriber
from Models.request import Request
from Utils.email_service import send_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_daily_summary_to_email(email: str, timeslot: str, requests_data: list):
    """Send daily summary to a specific email address"""
    try:
        ist = ZoneInfo("Asia/Kolkata")
        current_time = datetime.now(ist)

        # Determine greeting based on timeslot
        if timeslot == "morning":
            greeting = "Good Morning"
            time_note = "9:00 AM"
        else:  # evening
            greeting = "Good Evening"
            time_note = "5:00 PM"

        subject = f"{greeting} - Daily Request Summary"

        # Format requests list
        requests_text = ""
        if requests_data:
            for req in requests_data:
                requests_text += f"""
                Request ID: {req["id"]}
                From: {req["req_from"]}
                To: {req["req_to"]}
                Description: {req["description"] or "No description"}
                Scheduled: {req["request_date"].astimezone(ist).strftime("%Y-%m-%d %H:%M")}
                {"-" * 40}
                """
        else:
            requests_text = "No active requests today.\n"

        body = f"""
        =================================
        {greeting.upper()} REQUEST SUMMARY
        =================================
        
        Summary Time: {time_note}
        Date: {current_time.strftime("%Y-%m-%d")}
        
        =================================
        TODAY'S REQUESTS ({len(requests_data)} total)
        =================================
        
        {requests_text}
        
        =================================
        SYSTEM INFORMATION
        =================================
        • Total subscribers: [Will be shown in actual email]
        • Active requests: {len(requests_data)}
        • Summary generated at: {current_time.strftime("%H:%M:%S %Z")}
        
        =================================
        This is your daily {timeslot} summary.
        
        You are receiving this email because you are
        subscribed to Request Management System.
        
        To unsubscribe, please contact the administrator.
        =================================
        """

        # Send email
        success = await send_email(to=email, subject=subject, body=body)

        if success:
            # Update last_sent_date in database
            db = SessionLocal()
            try:
                subscriber = (
                    db.query(EmailSubscriber)
                    .filter(EmailSubscriber.email == email)
                    .first()
                )
                if subscriber:
                    subscriber.last_sent_date = datetime.now(timezone.utc)
                    db.commit()
            except Exception as e:
                logger.error(f"Error updating last_sent_date for {email}: {str(e)}")
            finally:
                db.close()

            logger.info(f"Daily {timeslot} summary sent to {email}")
            return True
        else:
            logger.error(f"Failed to send daily {timeslot} summary to {email}")
            return False

    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        return False


def get_todays_requests():
    """Get all requests scheduled for today"""
    db = SessionLocal()
    try:
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Convert to UTC for query
        today_start_utc = today_start.astimezone(timezone.utc)
        today_end_utc = today_end.astimezone(timezone.utc)

        # Get all requests for today
        requests = (
            db.query(Request)
            .filter(Request.request_date.between(today_start_utc, today_end_utc))
            .all()
        )

        # Convert to dictionary list
        requests_data = []
        for req in requests:
            requests_data.append(
                {
                    "id": req.id,
                    "req_from": req.req_from,
                    "req_to": req.req_to,
                    "description": req.description,
                    "request_date": req.request_date,
                    "email": req.email if hasattr(req, "email") else None,
                }
            )

        logger.info(f"Found {len(requests)} requests for today")
        return requests_data

    except Exception as e:
        logger.error(f"Error getting today's requests: {str(e)}")
        return []
    finally:
        db.close()


def get_active_subscribers():
    """Get all active email subscribers"""
    db = SessionLocal()
    try:
        subscribers = db.query(EmailSubscriber).filter(EmailSubscriber.is_active).all()

        emails = [subscriber.email for subscriber in subscribers]
        logger.info(f"Found {len(emails)} active subscribers")
        return emails

    except Exception as e:
        logger.error(f"Error getting active subscribers: {str(e)}")
        return []
    finally:
        db.close()


async def send_daily_summary_to_all(timeslot: str):
    """Send daily summary to all active subscribers"""
    logger.info(f"Starting daily {timeslot} summary broadcast")

    # Get today's requests
    requests_data = get_todays_requests()

    # Get all active subscribers
    subscribers = get_active_subscribers()

    if not subscribers:
        logger.warning(f"No active subscribers for {timeslot} summary")
        return {"sent": 0, "failed": 0, "total_subscribers": 0}

    sent_count = 0
    failed_count = 0

    # Send email to each subscriber
    for email in subscribers:
        success = await send_daily_summary_to_email(email, timeslot, requests_data)

        if success:
            sent_count += 1
        else:
            failed_count += 1

    logger.info(
        f"Daily {timeslot} summary: Sent to {sent_count}/{len(subscribers)} subscribers"
    )
    return {
        "sent": sent_count,
        "failed": failed_count,
        "total_subscribers": len(subscribers),
        "timeslot": timeslot,
    }


def run_morning_broadcast():
    """Wrapper for morning broadcast job"""
    try:
        asyncio.run(send_daily_summary_to_all("morning"))
    except Exception as e:
        logger.error(f"Error in morning broadcast job: {str(e)}")


def run_evening_broadcast():
    """Wrapper for evening broadcast job"""
    try:
        asyncio.run(send_daily_summary_to_all("evening"))
    except Exception as e:
        logger.error(f"Error in evening broadcast job: {str(e)}")


def start_scheduler():
    """Start the background scheduler with daily broadcast jobs"""
    scheduler = BackgroundScheduler(timezone=ZoneInfo("Asia/Kolkata"))

    # Schedule Morning Broadcast (9:00 AM IST daily)
    scheduler.add_job(
        run_morning_broadcast,
        CronTrigger(hour=9, minute=30, timezone=ZoneInfo("Asia/Kolkata")),
        id="morning_broadcast_job",
        name="Send morning summary to all subscribers",
        replace_existing=True,
        misfire_grace_time=300,  # 5 minutes grace period
    )

    # Schedule Evening Broadcast (5:00 PM IST daily)
    scheduler.add_job(
        run_evening_broadcast,
        CronTrigger(hour=17, minute=0, timezone=ZoneInfo("Asia/Kolkata")),
        id="evening_broadcast_job",
        name="Send evening summary to all subscribers",
        replace_existing=True,
        misfire_grace_time=300,  # 5 minutes grace period
    )

    scheduler.start()
    logger.info("Daily broadcast scheduler started successfully")
    logger.info("Morning broadcast: 9:00 AM IST daily")
    logger.info("Evening broadcast: 5:00 PM IST daily")

    return scheduler
