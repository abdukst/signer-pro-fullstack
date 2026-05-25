import io
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.file_service import sign_file, verify_file, verify_file_offline, validate_file,compute_key_fingerprint, get_signature_info

# ============================================
  #   sign_file
  # 1 path: simulate validate_file throw error
# ============================================
@patch('app.services.file_service.validate_file')
def test_sign_file_validate_file_error(mock_validate_file):
  # 1 
  mock_db_session = MagicMock()
  mock_user = MagicMock()
  moch_file_obj = MagicMock()

  mock_validate_file.side_effect = ValueError("File Type '.exe' is not allowed")

  with pytest.raises(ValueError, match="File Type '.exe' is not allowed"):
    sign_file(
      mock_db_session,
      user=mock_user,
      password="password",
      filename="testName",
      file_obj=moch_file_obj
    )

  mock_db_session.add.assert_not_called()
  mock_db_session.commit.assert_not_called()

# ============================================
  #   sign_file
  # 2 path: simulate hash_file throw error
# ============================================
@patch('app.services.file_service.validate_file')
@patch('app.services.file_service.hash_file')
def test_sign_file_hash_file_error(mock_hash_file, mock_validate_file):
  # 1 
  mock_db_session = MagicMock()
  mock_user = MagicMock()
  moch_file_obj = MagicMock()
  mock_validate_file.return_value = None
  mock_hash_file.side_effect = IOError('File stream closed unexpectedly')

  with pytest.raises(IOError, match='File stream closed unexpectedly'):
    sign_file(
      mock_db_session,
      user=mock_user,
      password="password",
      filename="testName",
      file_obj=moch_file_obj
    )


  mock_db_session.add.assert_not_called()
  mock_db_session.commit.assert_not_called()

# ============================================
  #   sign_file
  # 3 path: simulate get_user_active_key throw error
# ============================================
@patch('app.services.file_service.get_user_active_key')
@patch('app.services.file_service.validate_file')
@patch('app.services.file_service.hash_file')
def test_sign_file_active_key_error(mock_hash_file, mock_validate_file, mock_get_active_key):

  mock_db_session = MagicMock()
  mock_user = MagicMock()
  moch_file_obj = MagicMock()
  mock_validate_file.return_value = None
  mock_hash_file.return_value = None
  mock_get_active_key.side_effect = ValueError()

  with pytest.raises(ValueError):
    sign_file(
      mock_db_session,
      user=mock_user,
      password="password",
      filename="testName",
      file_obj=moch_file_obj
    )

  mock_db_session.add.assert_not_called()
  mock_db_session.commit.assert_not_called()


# ============================================
  #   sign_file
  # 4 path: simulate user has no active key
  # get_user_active_key return None
# ============================================
@patch('app.services.file_service.initialize_user_keys')
@patch('app.services.file_service.get_user_active_key')
@patch('app.services.file_service.validate_file')
@patch('app.services.file_service.hash_file')
def test_sign_file_no_active_key (mock_hash_file,       
                                  mock_validate_file, 
                                  mock_get_active_key, mock_initialize_user_key):

  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock()
  mock_validate_file.return_value = None
  mock_hash_file.return_value = None
  mock_get_active_key.return_value = None
  mock_initialize_user_key.side_effect = ValueError()

  with pytest.raises(ValueError):
    sign_file(
      mock_db_session,
      user=mock_user,
      password="password",
      filename="testName",
      file_obj=moch_file_obj
    )
    # 3. VERIFY: The function crashed early before any database interactions
  mock_db_session.add.assert_not_called()
  mock_db_session.flush.assert_not_called()
  mock_db_session.commit.assert_not_called()

# ============================================
  #   sign_file
  # 5 path: simulate user has active key
  # get_user_active_key return key
  # sign_data fail
# ============================================
@patch('app.services.file_service.sign_data')
@patch('app.services.file_service.initialize_user_keys')
@patch('app.services.file_service.get_user_active_key')
@patch('app.services.file_service.validate_file')
@patch('app.services.file_service.hash_file')
def test_sign_file_has_active_key(mock_hash_file,       
                                  mock_validate_file, 
                                  mock_get_active_key, mock_initialize_user_key,mock_sign_data):

  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock()
  mock_validate_file.return_value = None
  mock_hash_file.return_value = None
  mock_get_active_key.return_value = None
  mock_sign_data.side_effect = ValueError('Technical error in the signing service')

  with pytest.raises(ValueError, match='Technical error in the signing service'):
    sign_file(
        mock_db_session,
        user= mock_user,
        password="password",
        filename="testName",
        file_obj=moch_file_obj
      )
    
  mock_initialize_user_key.assert_called_once_with(user_id= 1,password= 'password')
  mock_db_session.add.assert_called_once()
  mock_db_session.flush.assert_called_once()
  mock_db_session.commit.assert_not_called()
  mock_db_session.rollback.assert_called_once()

# ============================================
  #   sign_file
  # 6 path: sign_data fail. false password
# ============================================
@patch('app.services.file_service.FileRecord')
@patch('app.services.file_service.sign_data')
@patch('app.services.file_service.get_user_active_key')
@patch('app.services.file_service.validate_file')
@patch('app.services.file_service.hash_file')
def test_sign_file_failed_password(mock_hash_file,       
                    mock_validate_file, 
                    mock_get_active_key, 
                    mock_sign_data,
                    mock_file_record):

  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock()
  mock_validate_file.return_value = None
  mock_hash_file.return_value = 'Fake Hash'
  mock_get_active_key.return_value = MagicMock(id=1, user_id=1, key_fingerprint = 'A1:B2')

  mock_sign_data.side_effect = ValueError('SIGNING DENIED: Invalid password attempt for user test@user.com')
  
  with pytest.raises(ValueError, match='SIGNING DENIED: Invalid password attempt for user test@user.com'):
    mock_signature = sign_file(
          mock_db_session,
          user= mock_user,
          password="false_password",
          filename="testName",
          file_obj=moch_file_obj
    )

  mock_db_session.add.assert_not_called()
  mock_db_session.commit.assert_not_called()
  mock_db_session.refresh.assert_not_called()
  mock_db_session.rollback.assert_called_once()

  
# ============================================
  #   sign_file
  # 7 path: sign_data success
# ============================================
@patch('app.services.file_service.FileRecord')
@patch('app.services.file_service.sign_data')
@patch('app.services.file_service.get_user_active_key')
@patch('app.services.file_service.validate_file')
@patch('app.services.file_service.hash_file')
def test_sign_file_success(mock_hash_file,       
                    mock_validate_file, 
                    mock_get_active_key, 
                    mock_sign_data,
                    mock_file_record):

  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock()
  mock_validate_file.return_value = None
  mock_hash_file.return_value = 'Fake Hash'
  mock_get_active_key.return_value = MagicMock(id=1, user_id=1, key_fingerprint = 'A1:B2')

  mock_sign_data.return_value = 'fake_signature'
  
  
  mock_signature = sign_file(
        mock_db_session,
        user= mock_user,
        password="password",
        filename="testName",
        file_obj=moch_file_obj
  )


  mock_db_session.add.assert_called_once()
  mock_db_session.commit.assert_called_once()
  mock_db_session.refresh.assert_called_once()

  mock_sign_data.assert_called_once_with(
                                    user_key= mock_get_active_key(),
                                    password="password",
                                    data = b"Fake Hash"
                                    )
  mock_file_record.assert_called_once_with(
    user_id= 1,
    filename= 'testName',
    file_hash= 'Fake Hash',
    signature = 'fake_signature',
    signer_identifier = 'test@user.com',
    key_fingerprint = 'A1:B2'
  )
  
  assert mock_signature['signature'] == 'fake_signature'
  assert mock_signature['file_hash'] == 'Fake Hash'
  assert mock_signature['key_fingerprint'] == 'A1:B2'

# ============================================
  # verify file
  # 1 path: User not found.
# ============================================
@patch('app.services.file_service.hash_file')
def test_verify_file_not_user(mock_hash_file):
  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock(id=1)
  mock_db_session.query.return_value.filter.return_value.first.return_value = None

  with pytest.raises(ValueError, match='Signer identity not found'):
    verify_file(
      mock_db_session, 
      user_id=mock_user.id,
      file_id=moch_file_obj.id, 
      file_obj=moch_file_obj)
    
  mock_hash_file.assert_not_called()
  mock_db_session.query.assert_called_once()


 # ============================================
  # verify file
  # 2 path: User found. File not found.
# ============================================
@patch('app.services.file_service.hash_file')
def test_verify_file_not_file(mock_hash_file):
  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock(id=1)
  mock_db_session.query.return_value.filter.return_value.first.side_effect = [
    mock_user,
    None
  ]
  with pytest.raises(ValueError, match='File not found'):
    verify_file(
      mock_db_session, 
      user_id=mock_user.id,
      file_id=moch_file_obj.id, 
      file_obj=moch_file_obj)
    
  #mock_hash_file.assert_not_called()
  assert mock_db_session.query.return_value.filter.return_value.first.call_count == 2
 
# ============================================
  # verify file
  # 3 path: User found. File found. 
  # hash_file throw error 
# ============================================
@patch('app.services.file_service.FileRecord')
@patch('app.services.file_service.hash_file')
def test_verify_file_hash_error(mock_hash_file, mock_file_record):
  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock(id=1)
  mock_file_record.return_value = MagicMock()
  mock_hash_file.side_effect = IOError('File stream closed unexpectedly')
  mock_db_session.query.return_value.filter.return_value.first.side_effect = [
    mock_user,
    mock_file_record
  ]
  with pytest.raises(IOError, match='File stream closed unexpectedly'):
    verify_file(
      mock_db_session, 
      user_id=mock_user.id,
      file_id=moch_file_obj.id, 
      file_obj=moch_file_obj)
    
  #mock_hash_file.assert_not_called()
  assert mock_db_session.query.return_value.filter.return_value.first.call_count == 2

# ============================================
  # verify file
  # 4 path: incoming hash MODIFIED. 
# ============================================
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.FileRecord')
@patch('app.services.file_service.hash_file')
def test_verify_file_hash_error(mock_hash_file, mock_file_record, mock_verify_signature):
  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock(id=1)
  mock_file_record = MagicMock(file_hash='A1:B2')
  mock_hash_file.return_value = 'A1:B2:C3'
  mock_db_session.query.return_value.filter.return_value.first.side_effect = [
    mock_user,
    mock_file_record
  ]
  with pytest.raises(ValueError, match='Integrity check failed: The file has been modified since it was signed.'):
    verify_file(
      mock_db_session, 
      user_id=mock_user.id,
      file_id=moch_file_obj.id, 
      file_obj=moch_file_obj)
    
  mock_verify_signature.assert_not_called()
  assert mock_db_session.query.return_value.filter.return_value.first.call_count == 2


# ============================================
  # verify file
  # 5 path: Error: Signing key missed. 
# ============================================
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.FileRecord')
@patch('app.services.file_service.hash_file')
def test_verify_file_key_missed(mock_hash_file, mock_file_record, mock_verify_signature):
  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock(id=1)
  mock_file_record = MagicMock(
    file_hash='A1:B2:C3',
    signing_key = None)
  mock_hash_file.return_value = 'A1:B2:C3'
  mock_db_session.query.return_value.filter.return_value.first.side_effect = [
    mock_user,
    mock_file_record
  ]
  with pytest.raises(ValueError, match='Verification Error: The specific key used for this signature is missing from our records.'):
    verify_file(
      mock_db_session, 
      user_id=mock_user.id,
      file_id=moch_file_obj.id, 
      file_obj=moch_file_obj)
    
  mock_verify_signature.assert_not_called()
    
 
# ============================================
  # verify file
  # 6 path: verify_signature throw error. 
# ============================================
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.FileRecord')
@patch('app.services.file_service.hash_file')
def test_verify_file_signature_error(mock_hash_file, mock_file_record, mock_verify_signature):
  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock(id=1)
  mock_file_record = MagicMock()
  mock_file_record.file_hash='A1:B2:C3'
  mock_file_record.signing_key.public_key = None
  mock_file_record.signature  = ''
  
  mock_hash_file.return_value = 'A1:B2:C3'

  mock_db_session.query.return_value.filter.return_value.first.side_effect = [
    mock_user,
    mock_file_record
  ]
  mock_verify_signature.side_effect = ValueError('dentity Verification Error: The public key is invalid or corrupted.')
  with pytest.raises(ValueError, match='dentity Verification Error: The public key is invalid or corrupted.'):
    verify_file(
            mock_db_session, 
            user_id=mock_user.id,
            file_id=moch_file_obj.id, 
            file_obj=moch_file_obj)
    
  mock_verify_signature.assert_called_once_with(
    None,
    b'A1:B2:C3',
    ''
  )
  

# ============================================
  # verify file
  # 7 path: verify_signature success. 
# ============================================
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.FileRecord')
@patch('app.services.file_service.hash_file')
def test_verify_file_success(mock_hash_file, mock_file_record, mock_verify_signature):
  mock_db_session = MagicMock()
  mock_user = MagicMock(id=1, email = 'test@user.com')
  moch_file_obj = MagicMock(id=1)
  mock_file_record = MagicMock()
  mock_file_record.file_hash='A1:B2:C3'
  mock_file_record.signing_key.public_key = 'fake_key'
  mock_file_record.signature  = 'fake_signature'
  mock_hash_file.return_value = 'A1:B2:C3'

  mock_db_session.query.return_value.filter.return_value.first.side_effect = [
    mock_user,
    mock_file_record
  ]
  mock_verify_signature.return_value = True
  
  restult = verify_file(
            mock_db_session, 
            user_id=mock_user.id,
            file_id=moch_file_obj.id, 
            file_obj=moch_file_obj)
    
  mock_verify_signature.assert_called_once_with(
    'fake_key',
    b'A1:B2:C3',
    'fake_signature'
  )
  assert restult is True
  

# ============================================
  # verify file offline
  # 1 path: hash_file error. 
# ============================================
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.hash_file')
def test_verify_file_offline_hash_error(mock_hash_file, mock_verify_signature):
  mock_public_key = MagicMock()
  mock_file_obj = MagicMock()
  mock_hash_file.side_effect = IOError()
  with pytest.raises(IOError):
    verify_file_offline(
      public_key=mock_public_key,
      file_obj=mock_file_obj,
      signature_b64='fake_signature'
    )
  mock_verify_signature.assert_not_called()
  
# ============================================
  # verify file offline
  # 2 path: invalid signature ecncoding. 
# ============================================
@patch('app.services.file_service.base64.b64decode')
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.hash_file')
def test_verify_file_offline_ecncoding_error(mock_hash_file, mock_verify_signature, mock_b64decode):
  mock_public_key = MagicMock()
  mock_file_obj = MagicMock()
  mock_hash_file.return_value = 'fake_hash'
  mock_b64decode.side_effect = Exception()
  
  with pytest.raises(Exception, match='invalid signature ecncoding'):
    verify_file_offline(
      public_key=mock_public_key,
      file_obj=mock_file_obj,
      signature_b64='fake_signature'
    )
  mock_verify_signature.assert_not_called()

  
# ============================================
  # verify file offline
  # 3 path: verify_signature throw error. 
# ============================================

@patch('app.services.file_service.base64.b64decode')
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.hash_file')
def test_verify_file_offline_signature_error(mock_hash_file, mock_verify_signature, mock_b64decode):

  mock_file_obj = MagicMock()
  mock_hash_file.return_value = 'fake_hash'
  mock_verify_signature.side_effect = ValueError()
  mock_b64decode.return_value = 'fake_b64_signature'
  
  with pytest.raises(ValueError):
    verify_file_offline(
      public_key='fake_public_key',
      file_obj=mock_file_obj,
      signature_b64='fake_signature'
    )
  mock_verify_signature.assert_called_once_with(
      public_key_str='fake_public_key', data=b'fake_hash',
      signature='fake_b64_signature'
  )

# ============================================
  # verify file offline
  # 4 path: verify_signature return False. 
# ============================================
@patch('app.services.file_service.base64.b64decode')
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.hash_file')
def test_verify_file_offline_signature_false(mock_hash_file, mock_verify_signature, mock_b64decode):

  mock_file_obj = MagicMock()
  mock_hash_file.return_value = 'fake_hash'
  mock_b64decode.return_value = 'fake_b64_signature'
  mock_verify_signature.return_value = False
  
  
  result = verify_file_offline(
      public_key='fake_public_key',
      file_obj=mock_file_obj,
      signature_b64='fake_signature'
    )
  mock_verify_signature.assert_called_once_with(
      public_key_str='fake_public_key', data=b'fake_hash',
      signature='fake_b64_signature'
  )
  assert result is False

# ============================================
# verify file offline
# 5 path: verify_signature return True. 
# ============================================
@patch('app.services.file_service.base64.b64decode')
@patch('app.services.file_service.verify_signature')
@patch('app.services.file_service.hash_file')
def test_verify_file_offline_signature_true(mock_hash_file, mock_verify_signature, mock_b64decode):

  mock_file_obj = MagicMock()
  mock_hash_file.return_value = 'fake_hash'
  mock_b64decode.return_value = 'fake_b64_signature'
  mock_verify_signature.return_value = True
  
  
  result = verify_file_offline(
      public_key='fake_public_key',
      file_obj=mock_file_obj,
      signature_b64='fake_signature'
    )
  mock_verify_signature.assert_called_once_with(
      public_key_str='fake_public_key', data=b'fake_hash',
      signature='fake_b64_signature'
  )
  assert result is True


# ============================================
# validate_file
# 1 path: validate_file raise error,
#  EXTENSIONS not allowed. 
# ============================================
def test_validate_file_extention_error():
  mock_file_obj = MagicMock()
  file_name = 'test.exe'
  with pytest.raises(ValueError, match="File Type '.exe' is not allowed"):
    validate_file(file_name, mock_file_obj)

  mock_file_obj.seek.assert_not_called()

# ============================================
# validate_file
# 2 path: validate_file raise error,
#   cursor position error, seek() raise value error!
# ============================================
def test_validate_file_cursor_error():
  mock_file_obj = MagicMock()
  file_name = 'test.pdf'
  mock_file_obj.seek.side_effect = ValueError()
  with pytest.raises(ValueError):
    validate_file(file_name, mock_file_obj)

  mock_file_obj.tell.assert_not_called()

# ============================================
# validate_file
# 3 path: validate_file raise error,
#   closed file, tell() raise value error!
# ============================================
def test_validate_file_tell_size_error():
  mock_file_obj = MagicMock()
  file_name = 'test.pdf'
  mock_file_obj.tell.side_effect = ValueError()
  with pytest.raises(ValueError):
    validate_file(file_name, mock_file_obj)
    
  mock_file_obj.seek.assert_called_once()

# ============================================
# validate_file
# 4 path: validate_file raise error,
#   File size bigger than allowed!
#   allowed size: 10 * 1024 * 1024
# ============================================
def test_validate_file_error():
  mock_file_obj = MagicMock()
  file_name = 'test.pdf'
  mock_file_obj.tell.return_value = 10 * 1025 * 1024
  with pytest.raises(ValueError, match='File exceeds maximum allowed size'):
    validate_file(file_name, mock_file_obj)
    
  assert mock_file_obj.seek.call_count == 2

# ============================================
# compute_key_fingerprint
# ============================================

def test_compute_key_fingerprint():
  public_key = 'fake_public_key'
  expected_result = '4e:b4:a7:2f:b1:c8:7a:26:48:c2:2d:a0:e3:29:21:31:aa:11:55:e3:de:35:fa:9a:00:2c:91:01:93:22:69:6e'
  result = compute_key_fingerprint(public_key)
  print(result)
  assert result == expected_result

# ============================================
#   get_signature_info
# 1 path: error
# ============================================

def test_compute_get_signature_info_error():
  mock_db_session = MagicMock()
  mock_db_session.query.return_value.filter.return_value.first.return_value = None

  with pytest.raises(ValueError, match='Signature record not found'):
    get_signature_info(mock_db_session, user_id=1, file_id=1)
  
# ============================================
# get_signature_info
# 2 path: success
# ============================================

@patch('app.services.file_service.format_signature_to_b64')
def test_compute_get_signature_info_success(mock_format_b64):
  mock_db_session = MagicMock()
  mock_format_b64.return_value = "b64_encoded_signature_string" 
  mock_file_record = MagicMock()
  mock_file_record.id = 101
  mock_file_record.filename = "contract.pdf"
  mock_file_record.signer_identifier = "signer@example.com"
  mock_file_record.signature = b"raw_binary_signature"
  mock_file_record.key_fingerprint = "AA:BB:CC:DD"
  mock_file_record.file_hash = "abc123hash"
  mock_file_record.created_at = datetime(2026, 5, 25, 12, 0, 0)
  mock_file_record.signing_key.is_active = True
  mock_file_record.signing_key.public_key = "fake_pub_key_content"
  mock_file_record.signing_key.revoked_at = None

  mock_db_session.query.return_value.filter.return_value.first.return_value = mock_file_record

 
  get_signature_info(mock_db_session, user_id=1, file_id=1) 

  mock_format_b64.assert_called_once_with(b"raw_binary_signature")
  