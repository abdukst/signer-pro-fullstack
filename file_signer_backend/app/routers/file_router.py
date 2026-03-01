from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import base64
import io
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.services.file_service import sign_file, verify_file, verify_file_offline, get_signature_info
from app.schemas.file_schema import  FileResponse, FileAuditResponse
from app.dependencies.auth import get_current_user
from app.models. file_model import FileRecord

router = APIRouter(prefix="/files",tags=["Files"])

"""
uploaded_file: must match the The key (the string) in the file.js in the formData we send from the frontend
"""
@router.post("/sign")
def sign_uploaded_file(
  uploaded_file: UploadFile = File(...),
  password: str = Form(...),
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
): 
  try: 
    record = sign_file(
      db,
      user= current_user,
      password=password,
      filename=uploaded_file.filename,
      file_obj=uploaded_file.file
    )
     # Encode signature so it can live in a text file
    signature_b64 = base64.b64encode(record["signature"]).decode()
    sig_filename = uploaded_file.filename + ".sig"
    # creates a virtual file in the server's RAM to stream from it to the frontend
    file_like = io.BytesIO(signature_b64.encode())
    return StreamingResponse(
      file_like,
      media_type="application/octet_stream",
      headers= {
        "Content-Disposition": f"attachment; filename={sig_filename}"
      }
    )
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify/{file_id}")
def verify_uploaded_file(
  file_id: int,
  uploaded_file: UploadFile = File(...),
  db: Session = Depends(get_db),
  current_user=Depends(get_current_user)
):
  try: 
    is_valid = verify_file(
      db=db,
      user_id=current_user.id,
      file_id=file_id,
      file_obj=uploaded_file.file
    )
    return {"valid": is_valid}
  except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))

@router.post("/verify-independent")
def verify_uploaded_file_independent(
  uploaded_file: UploadFile = File(...),
  signature_file: UploadFile = File(...),
  public_key: str = Form(...)
):
  try:
    signature_file_content = signature_file.file.read().decode()
    is_valid = verify_file_offline(
      public_key=public_key,
      file_obj=uploaded_file.file,
      signature_b64=signature_file_content
    )
    #  moves the "cursor" again to the begin
    signature_file.file.seek(0)
  except ValueError as e :
    raise HTTPException(status_code=400, detail=str(e))
  return is_valid

@router.get("/{file_id}/signature-inspection", response_model=FileAuditResponse)
def inspect_signature(
  file_id: int,
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
):
  try:
    return get_signature_info(
      db=db,
      user_id = current_user.id,
      file_id=file_id
      )
  except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
  
    
@router.get("/", response_model=list[FileResponse])
def list_user_files(
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
):
  try:
    files = (
    db.query(FileRecord).filter(FileRecord.user_id == current_user.id).order_by(FileRecord.created_at.desc()).all()
    )
    return files
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


  
