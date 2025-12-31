from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Database.database import SessionLocal
from Schemas.user import UserLogin, UserResponse
from Models.user import User
from Utils.hashing import verify_password
from Utils.token import create_token
from Database.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=UserResponse)
def login(request: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username")

    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_token({"username": user.username, "role": user.role})

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "token": token
    }
