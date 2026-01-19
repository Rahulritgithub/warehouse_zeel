# Crud/user.py
from sqlalchemy.orm import Session
from Models.user import User


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, password: str):
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session):
    return db.query(User).all()


def delete_user(db: Session, username: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user
