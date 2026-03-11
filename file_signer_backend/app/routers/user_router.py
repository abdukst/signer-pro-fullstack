from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import register_user, get_user_public_key
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register_user_endpoint(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(db, user)


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.get("/public-key")
def get_public_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
                   ):
    try:
        return get_user_public_key(
            db=db,
            user_id = current_user.id
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


 