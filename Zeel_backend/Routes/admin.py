from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Database.database import SessionLocal
from Schemas.user import UserCreate, UserResponse
from Models.user import User
from Utils.hashing import hash_password
from Database.database import get_db


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/create-user", response_model=UserResponse)
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.username == request.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=request.username,
        password=hash_password(request.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    print(users)
    return users

@router.delete("/users/{username}")
def delete_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": f"User '{username}' deleted successfully"}
