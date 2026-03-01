from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
  email: EmailStr
  password: str
  
class UserLoginInfo(BaseModel):
  username: str
  email: EmailStr

class TokenResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"
  user: UserLoginInfo