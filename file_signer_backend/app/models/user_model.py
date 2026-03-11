from sqlalchemy import Column, Integer, String, Boolean,DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column (String, unique=True, index=True, nullable=False)
  username = Column(String, unique=True, index=True, nullable=False)
  fullname = Column(String, nullable=True)
  passwordhash = Column(String, nullable=False)


  is_active = Column(Boolean, default=True, nullable=False)
  deleted_at = Column(DateTime(timezone=True), nullable=True)
  # Relationship: No 'delete-orphan' here! 
  # We want the keys to stay even if a user is deactivated.
  keys = relationship("UserKey", back_populates="owner")