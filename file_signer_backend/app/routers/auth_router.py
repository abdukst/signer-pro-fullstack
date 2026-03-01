from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.user_service import autenticate_user, authenticate_user
from app.dependencies.db import get_db
from app.security.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

  user = authenticate_user(db, data.email, data.password)
  if not user:
    raise HTTPException(
      status_code=401,
      detail="Invalid email or password"
    )
  token = create_access_token(subject=str(user.id))
  return {
    "access_token": token,
    "user": {
      "username": user.username,
      "email": user.email
             }
    }