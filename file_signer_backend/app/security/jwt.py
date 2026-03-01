from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
ALGORITHM = "HS256"

if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES is missing in environment")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing in environment")

def create_access_token(subject: str) -> str:
  expire = datetime.now(timezone.utc)+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  payload = {
    "sub" : subject,
    "exp" :expire
  }

  token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

  return token