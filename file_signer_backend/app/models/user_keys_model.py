from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class UserKey(Base):
  """
  Construct new UserKey.
  ( id: Integer,
    user_id: Integer,
    key_fingerprint: Str,
    public_key: Str, 
    encrypted_private_key: LargeBinary, 
    key_salt: LargeBinary,
    key_iv: LargeBinary, 
    is_active: Boolean:Default=True,
    created_at: DateTime:server_default=func.now(), 
    revoked_at: DateTime, 
    owner: ,
    signed_files: )
  """
  __tablename__ = "user_keys"
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  # The unique fingerprint to match with FileRecords
  key_fingerprint = Column(String, unique=True, index=True, nullable=False)

  # Cryptographic Material
  public_key = Column(String, nullable=False)
  encrypted_private_key = Column(LargeBinary, nullable=False)
  key_salt = Column(LargeBinary, nullable=False)
  key_iv = Column(LargeBinary, nullable=False)


  # Lifecycle Management
  is_active = Column(Boolean, default = True, nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  revoked_at = Column(DateTime(timezone=True), nullable=True)

  owner = relationship("User", back_populates="keys")

  #Link back to files so we can see all files signed by this specific key
  signed_files = relationship("FileRecord", back_populates="signing_key")

  # THE SAFETY BOUNCER:
    # This ensures a single user can't have two 'True' active keys at once.
  __table_args__ = (
    # This Index says: "For a specific user_id, there can be only ONE row 
    # where is_active is True. If is_active is False, they can have 100 rows."
    Index(
      "idx_only_one_active_key_per_user",
      "user_id",
      unique=True,
      sqlite_where=(is_active == True)
    ),
  )


