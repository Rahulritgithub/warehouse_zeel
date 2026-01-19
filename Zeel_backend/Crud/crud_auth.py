from sqlalchemy.orm import Session
from Models.user import User
from Utils.hashing import verify_password


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
