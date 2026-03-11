from sqlalchemy.orm import Session
from app.models.file_model import FileRecord
from app.models.user_model import User
from app.models.user_keys_model import UserKey
from app.security.hashing import hash_file
from app.security.key_service import initialize_user_keys, sign_data, verify_signature, format_signature_to_b64
from app.services.user_service import get_user_active_key
import os
import base64
import hashlib


MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg"}

def sign_file(db: Session,
              *,
              user: User,
              password: str,
              filename:str,
              file_obj
              ):
  
  # 1. Validate upload file (raises ValueError if too big/
  validate_file(filename=filename, file_obj=file_obj)
  # hash file to sign it.
  file_hash = hash_file(file_obj=file_obj)
  
  # check if user has active key
  user_active_key = get_user_active_key(db=db, user_id= user.id)
  
  # If it's the user's first time, generate the key or no active key.
  if not user_active_key:
    
    user_active_key = initialize_user_keys(user_id=user.id, password=password)
    
    db.add(user_active_key)
    
    # WE STOP HERE: We need to push the key to the DB so it gets 
    # its 'id' and 'key_fingerprint' before we link a file to it.
    # make db to be aware of changes without making them permanent until we finish the transaction.
    db.flush()
  
  
  # 1. THE CORE ACTION: Sign the file hash
  # If the password is wrong, 'sign_data' raises a ValueError here.
  # Because we haven't 'committed' yet, a failure here means the 
  # new key (if created) is never permanently saved.
  
  try:
    signature = sign_data(
      user_key=user_active_key,
      password=password,
      data=file_hash.encode()
      )
  except ValueError as e:

    db.rollback()

    # This catches "Invalid Password" error from unlock_private_key
    raise e
  except Exception:

    db.rollback()

    # This catches any other unexpected technical crash
    raise ValueError("Technical error in the signing service")
  
  # 2. METADATA GENERATION
  # We pull these directly from the 'active_key' object we found/flushed
  signer_identifier = user.email
  key_fingerprint = user_active_key.key_fingerprint
  
  # 3. DB PERSISTENCE: Create the FileRecord
  file_record = FileRecord(
    user_id= user.id,
    filename= filename,
    file_hash= file_hash,
    signature = signature,
    signer_identifier = signer_identifier,
    key_fingerprint = key_fingerprint
    )
  
  db.add(file_record)

  # 4. THE ATOMIC COMMIT (The All-or-Nothing Rule)
  # This saves the New Key (if any) AND the FileRecord together.
  # If anything failed before this line, nothing is saved.
  db.commit()
  db.refresh(file_record)

  return {
    "filename": filename,
    "file_hash": file_hash,
    "signature": signature,
    "signer": signer_identifier,
    "key_fingerprint": key_fingerprint
  }

def verify_file(db: Session,
                *,
                user_id: int,
                file_id: int,
                file_obj
                ) -> bool:

  file_record = db.query(FileRecord).filter(
    FileRecord.id==file_id,
    FileRecord.user_id==user_id
    ).first()
  
  
  
  if not file_record:
    raise ValueError("File not found")
 
  # claculate the incoming file hash
  incoming_file_hash = hash_file(file_obj=file_obj)
  
  # 1. check if the original hash without signature matchs the incoming file hash with out signature.
  # Integrity (Has the file changed?)
  if incoming_file_hash != file_record.file_hash:
    raise ValueError("Integrity check failed: The file has been modified since it was signed.")
  
  user = db.query(User).filter(User.id==user_id).first()
  if not user:
    raise ValueError("Signer identity not found")
  
  # get the the key that signed this file.
  file_signing_key = file_record.signing_key
  if not file_signing_key:
    raise ValueError("Verification Error: The specific key used for this signature is missing from our records.")

  # Check 2: Authenticity (Was it really this user?)
  # This will now either return True or raise a ValueError
  return verify_signature(
    file_signing_key.public_key,
    incoming_file_hash.encode(),
    file_record.signature
  )
  
def verify_file_offline(*, public_key:str, file_obj, signature_b64: str) -> bool:
  # compute the hash for the incoming file
  file_hash = hash_file(file_obj=file_obj)
  try :
    signature = base64.b64decode(signature_b64)
  except Exception:
    raise ValueError("invalid signature ecncoding")
  
  
  # decode the signature from the incomeing .sig file 
  is_valid = verify_signature(public_key_str=public_key, data=file_hash.encode(), signature = signature)
  return is_valid


def validate_file(filename: str, file_obj):
  _, ext = os.path.splitext(filename.lower())
  if ext not in ALLOWED_EXTENSIONS:
    raise ValueError(f"File Type '{ext}' is not allowed")
  # Move the "cursor" to the very end of the file
  file_obj.seek(0, 2)
  # Ask: "What position is the cursor at?" (This is the size in bytes)
  size = file_obj.tell()
  # VERY IMPORTANT: Move the cursor back to the start
  file_obj.seek(0)
  if size > MAX_FILE_SIZE:
    raise ValueError("File exceeds maximum allowed size")
  
def compute_key_fingerprint(public_key_str: str) -> str:
  """
  create a stable SHA256 fingerprint of the public key.
  this idenifies which key signed the document.
  """
  digest = hashlib.sha256(public_key_str.encode()).hexdigest()
  
  # format like real certificte fingerprints
  return ":".join(digest[i:i+2] for i in range(0, len(digest), 2))

def get_signature_info(db:Session,*, user_id: int, file_id: int):
  """
  Retrieve signature metadata without verifying the file again.
  Used for audit / inspection / UI display
  """
  fileRecord = db.query(FileRecord).filter(
    FileRecord.id == file_id,
    FileRecord.user_id == user_id
    ).first()
  if not fileRecord:
    raise ValueError("Signature record not found")
  return {
    "id": fileRecord.id,
    "filename": fileRecord.filename,
    "signer_identifier": fileRecord.signer_identifier,
    "signature" : format_signature_to_b64(fileRecord.signature),
    "key_fingerprint": fileRecord.key_fingerprint,
    "file_hash": fileRecord.file_hash,
    "created_at": fileRecord.created_at
  }