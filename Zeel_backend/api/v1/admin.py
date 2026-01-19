from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Database.database import get_db
from Schemas.user import UserCreate, UserResponse
from Crud import crud_user as user_crud

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user_api(request: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    return user_crud.create_user(db, request.username, request.password)


@router.get("/users", response_model=List[UserResponse])
def get_all_users_api(db: Session = Depends(get_db)):
    return user_crud.get_all_users(db)


@router.delete("/users/{username}")
def delete_user_api(username: str, db: Session = Depends(get_db)):
    deleted_user = user_crud.delete_user(db, username)

    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User '{username}' deleted successfully"}
