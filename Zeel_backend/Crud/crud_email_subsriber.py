from sqlalchemy.orm import Session
from Models.email_subscriber import EmailSubscriber


def get_by_email(db: Session, email: str):
    return db.query(EmailSubscriber).filter(EmailSubscriber.email == email).first()


def create_subscriber(db: Session, email: str, is_active: bool):
    subscriber = EmailSubscriber(email=email, is_active=is_active)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


def update_subscriber_status(db: Session, subscriber, is_active: bool):
    subscriber.is_active = is_active
    db.commit()
    db.refresh(subscriber)
    return subscriber


def get_all_subscribers(db: Session):
    return db.query(EmailSubscriber).all()


def get_active_subscribers(db: Session):
    return db.query(EmailSubscriber).filter(EmailSubscriber.is_active).all()


def delete_subscriber(db: Session, subscriber):
    db.delete(subscriber)
    db.commit()
