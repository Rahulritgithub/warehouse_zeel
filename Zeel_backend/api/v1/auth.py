from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Database.database import get_db
from Schemas.user import UserLogin, UserResponse
from Crud import crud_auth as auth_crud
from core.security import create_access_token as create_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=UserResponse)
def login_api(request: UserLogin, db: Session = Depends(get_db)):
    user = auth_crud.authenticate_user(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    token = create_token({"username": user.username, "role": user.role})

    return {"id": user.id, "username": user.username, "role": user.role, "token": token}
