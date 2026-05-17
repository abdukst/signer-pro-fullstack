import pytest
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from app.security.key_service import generate_key_pair, serialize_private_key, serialize_public_key, derive_key, encrypt_private_key, decrypt_private_key, compute_key_fingerprint, sign_data, verify_signature

# 1. TEST KEY GENERATION & SERIALIZATION
def test_key_generation_and_serialization():
  """
    1. Ensures RSA keys are generated with correct sizes and successfully
    2. Ensures converion of Keys to standard PEM string/bytes formats is correct.
    """
  private_key, public_key = generate_key_pair()

  # 1 Assert they are the correct cryptographic types and parameters.
  assert isinstance(private_key, rsa.RSAPrivateKey)
  assert private_key.key_size == 2048

  assert isinstance(public_key, rsa.RSAPublicKey)
  assert public_key.key_size == 2048

  # 2 Test Serialization
  private_key_pem = serialize_private_key(private_key)
  public_key_pem = serialize_public_key(public_key)
  # serialization of the keys to bytes is correct?
  assert isinstance(private_key_pem, bytes)
  assert isinstance(public_key_pem, bytes)
  # PEM format PrivateFormat() , PublicFormat()?
  assert b"-----BEGIN PRIVATE KEY-----" in private_key_pem
  assert b"-----END PRIVATE KEY-----" in private_key_pem
  assert b"-----BEGIN PUBLIC KEY-----" in public_key_pem
  assert b"-----END PUBLIC KEY-----" in public_key_pem

def test_key_derivation():
  """
  Validates that a password yields a consistent 32-byte key,
  and that a slight password variation yields a totally unique key.
  """
  # 16 Bytes salt
  salt = b"1234123412341234"
  password1 = "password_1"
  password2 = "password_2"
  key1 = derive_key(password1, salt)
  key2 = derive_key(password1, salt)
  key3 = derive_key(password2, salt)

  # 1 Must be 32 bytes for AES-256
  assert len(key1) == 32 

  # 2 Deterministic check
  assert key1 == key2

  # 3 slight password variation
  assert key1 != key3

def test_private_key_encryption_loop():
  """
  Verifies that private key data can be securely locked and unlocked 
  using the password loop, and that invalid inputs cause decryption failures.
  """
  private_k, public_k = generate_key_pair()
  #private_k_b = serialize_private_key(private_k)
  #public_k_b = serialize_public_key(public_k)
  print("\n")

  #print(public_k_b)
  private_k_b = b'-----BEGIN PRIVATE KEY-----\nMIIEvQIBADAN/tnaG5gf\n-----END PRIVATE KEY-----\n'
  password = "password"

  # Encrypt
  ciphertext1, salt1, iv1 = encrypt_private_key(private_k_b, password)
  ciphertext2, salt2, iv2 = encrypt_private_key(private_k_b, password)

  # 1. test Encryption result
  # a. salt, iv should be different every loop and the should have length of 16
  # b. ciphertext should be different every loop
  assert ciphertext1 != ciphertext2

  assert salt1 != salt2
  assert len(salt1) == 16

  assert iv1 != iv2
  assert len(iv1) == 16

  # c. the Encryption should change the private key.
  assert ciphertext1 != private_k_b

  # 2. test decryption private key.
  decrypted_private_key = decrypt_private_key(ciphertext1, password, salt1, iv1)

  assert decrypted_private_key == private_k_b



# 4. TEST SIGNING & VERIFICATION LOOP (RSA-PSS)
def test_signature_signung_and_veriffication():
  """
  Tests the complete asymmetric cryptographic lifecycle:
  Signing data, verifying it, and catching tampering attempts.
  """
  private_key, public_key = generate_key_pair()
  public_key_pem_str = serialize_public_key(public_key).decode()
  document_hash = b"a45cf83d29...sha256_mock_hash..."

  # Mocking a UserKey wrapper structure for sign_data compatibility
  class MockingUserKey:
    def __init__(self, priv_key):
      self.priv_key = priv_key
  
  # We monkeypatch unlock_private_key locally within this test scope
  # to avoid needing a database or real encrypted structures
  import app.security.key_service as ks
  ks.unlock_private_key = lambda user_key, password: user_key.priv_key

  mock_user_key = MockingUserKey(private_key)

  # Create Signature
  signature1 = sign_data(mock_user_key, "password", document_hash)
  signature2 = sign_data(mock_user_key, "password", document_hash)

  # signature is unique ?
  assert signature1 != signature2

  # Verify Success Path
  assert verify_signature(public_key_pem_str, document_hash, signature1)

  
  # Verify Failure Path (Data Tampering)
  tampered_hash = b"b5cf83d29...tampered_mock_hash..."
  with pytest.raises(ValueError, match="The signature does not match"):
    verify_signature(public_key_pem_str, tampered_hash, signature1)

# 5. TEST FINGERPRINT GENERATION
def test_compute_key_fingerprint():
  """
  Ensures fingerprints are properly formatted, deterministic, and capitalized.
  """

  public_k_b = b'-----BEGIN PUBLIC KEY-----\nMIIBIjAN7qMDW\n-----END PUBLIC KEY-----\n'
   
  key_fingerprint1 = compute_key_fingerprint(public_k_b)
  key_fingerprint2 = compute_key_fingerprint(public_k_b)

  # same fingerprint if same inpute?
  assert key_fingerprint1 == key_fingerprint2

  # fingerprint formatting?
  assert ":" in key_fingerprint1
  assert key_fingerprint1.isupper()


















  


