from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
  email: EmailStr
  username: str
  fullname: str | None = None
  password: str

class UserResponse(BaseModel):
  id: int
  email: EmailStr
  username: str
  fullname: str | None = None

  model_config =ConfigDict(from_attributes=True)

