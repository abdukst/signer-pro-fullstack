from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class FileRecord(Base):
  __tablename__ = "files"
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
  filename = Column(String, nullable=False)
  file_hash = Column(String, nullable=False)
  signature = Column(LargeBinary, nullable=True)
  signer_identifier = Column(String, nullable=False)
  key_fingerprint = Column(String, ForeignKey("user_keys.key_fingerprint"), nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

  owner = relationship("User")
  signing_key = relationship("UserKey", back_populates="signed_files")
  
  