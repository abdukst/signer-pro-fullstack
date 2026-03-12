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

class RotationRequest(BaseModel):
  """
  Schema for confirming key rotation with the user's password.
  """
  password: str