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
  active_key_fingerprint: str | None = None
  active_public_key: str | None = None
  key_status: bool | None = None

  model_config = ConfigDict(from_attributes=True)

class RotationRequest(BaseModel):
  """
  Schema for confirming key rotation with the user's password.
  """
  password: str