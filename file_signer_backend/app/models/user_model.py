from sqlalchemy import Column, Integer, String, LargeBinary
from app.database import Base

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column (String, unique=True, index=True, nullable=False)
  username = Column(String, unique=True, index=True, nullable=False)
  fullname = Column(String, nullable=True)
  passwordhash = Column(String, nullable=False)
  public_key = Column(String, nullable=True)
  encrypted_private_key = Column(LargeBinary, nullable=True)
  key_salt = Column(LargeBinary, nullable=True)
  key_iv = Column(LargeBinary, nullable=True)
