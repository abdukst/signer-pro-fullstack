from datetime import datetime
from pydantic import BaseModel, ConfigDict

class FileBase(BaseModel):
  filename: str

class FileCreate(FileBase):
  pass

class FileResponse(FileBase):
  id: int
  file_hash:str
  created_at: datetime
  model_config = ConfigDict(from_attributes=True)

class FileAuditResponse(FileResponse):
  signer_identifier: str
  key_fingerprint: str
  signature: str
  