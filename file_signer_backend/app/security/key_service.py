import os
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.exceptions import InvalidSignature

from app.models.user_keys_model import UserKey
import hashlib

def generate_key_pair():
  """
  Generate an RSA private/public key pair.
  """
  private_key = rsa.generate_private_key(
    public_exponent=65537, key_size=2048
    )
  public_key = private_key.public_key()
  return private_key, public_key

def serialize_private_key(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),  # we encrypt manually
    )


def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    
def derive_key(password: str, salt: bytes):
    """
    Derive a strong encryption key from the user's password.
    Salt: prevents identical passwords producing identical keys
    Iterations: makes brute-force attacks extremely slow
    """
    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=salt,
      iterations=100_00,
    )
    return kdf.derive(password.encode())

  

def encrypt_private_key(private_key_bytes: bytes, password: str):
    """
    Encrypt private key using AES derived from user password.
    """
    salt = os.urandom(16)
    key = derive_key(password=password, salt=salt)
    
    #(Initialization Vector): This is a random "starting point" for the encryption.
    iv = os.urandom(16)
    
    cipher = Cipher(algorithm=algorithms.AES(key=key), mode=modes.CFB(iv))
    encryptor = cipher.encryptor()
    
    ciphertext = encryptor.update(private_key_bytes) + encryptor.finalize()
    
    return ciphertext, salt, iv
def decrypt_private_key(ciphertext: bytes, password: str, salt: bytes, iv: bytes):
  key = derive_key(password=password, salt=salt)
  
  cipher = Cipher(algorithm=algorithms.AES(key=key), mode=modes.CFB(iv))
  decryptor = cipher.decryptor()
  
  return decryptor.update(ciphertext) + decryptor.finalize()
  

"""
Notice the quotes "User" — this is called a forward reference.
Python will not try to resolve User at runtime, but type checkers (and your IDE) will understand it

def initialize_user_keys(user: "User", password: str):
    
    Generate and store encrypted key material for a user.
    Called only once (lazy initialization).
    
    private_key, public_key = generate_key_pair()
    private_bytes = serialize_private_key(private_key=private_key)
    public_bytes = serialize_public_key(public_key=public_key)
    
    ciphertext, salt, iv = encrypt_private_key(private_bytes, password)
    
    user.public_key = public_bytes.decode()
    user.encrypted_private_key = ciphertext
    user.key_salt = salt
    user.key_iv = iv
"""
def initialize_user_keys(user_id: int, password: str):
    try:
      # 1. Generate keys objects.
      private_key, public_key = generate_key_pair()

      # 2. Convert to PEM (Bytes)
      private_bytes = serialize_private_key(private_key=private_key)
      public_bytes = serialize_public_key(public_key=public_key)
      
      # 3. Encrypt the private key
      ciphertext, salt, iv = encrypt_private_key(private_bytes, password)

      # 4. Prepare data for the model
      # Convert PEM bytes to a string for DB storage
      public_key_str = public_bytes.decode()

      # Pass bytes to fingerprint function
      key_fingerprint = compute_key_fingerprint(public_bytes)

      return UserKey(
        user_id = user_id,
        key_fingerprint = key_fingerprint,
        public_key = public_key_str,
        encrypted_private_key = ciphertext,
        key_salt = salt,
        key_iv = iv,
        is_active = True,
      )
    except Exception as e:
       # Prevents the app from proceeding with broken crypto
       raise ValueError(f"Failed to initialize secure keys: {str(e)}")



def compute_key_fingerprint(public_key_pem: bytes) -> str:
  """
  Creates a stable SHA256 fingerprint from the PEM bytes of the public key.
  this idenifies which key signed the document.
  """
  digest = hashlib.sha256(public_key_pem).hexdigest()

  # format like real certificte fingerprints
  # format like: AA:BB:CC...
  return ":".join(digest[i:i+2] for i in range(0, len(digest), 2)).upper()
    
def load_private_key(private_key_bytes: bytes):
  """
  Rebuild RSA private key object from PEM bytes.
  """
  return load_pem_private_key(private_key_bytes, password=None)

def load_public_key(public_key_str: str):
  """
  Rebuild RSA public key object from stored string.
  """
  return load_pem_public_key(public_key_str.encode())
  
    
def unlock_private_key(user_key: UserKey, password: str):
    """
    Decrypt and reconstruct the user's private key.
    This is used only during signing operations.
    """
    # Step 1: Always "succeeds" but might return garbage
    ## Consider upgrading to use Use AES-GCM to separately if the password is correct(separating "Wrong Password" from "Technical Error") 
    
    decrypt_bytes = decrypt_private_key(
        ciphertext=user_key.encrypted_private_key,
        password=password,
        salt = user_key.key_salt,
        iv = user_key.key_iv
      )
    print("----")
    try:
      # Step 2: This is where we actually find out if the password was right because of using AES-CFB, which not like AES-GCM mode that includes a "Tag" (an authentication code)
      return load_private_key(decrypt_bytes)
    except Exception:
       # If Error, it's almost certainly the password
       raise ValueError("Please check your signature password.")
    
    

def sign_data(user_key: UserKey, password: str , data: bytes) -> bytes:
    
   """
   Create a digital signature over data.
   We sign the HASH of the file, not the raw file.
   """
   private_key = unlock_private_key(user_key=user_key, password=password)
   signature = private_key.sign(
     data=data,
     padding=padding.PSS(
       mgf=padding.MGF1(hashes.SHA256()),
       salt_length=padding.PSS.MAX_LENGTH
     ),
     algorithm=hashes.SHA256()
   )
   return signature

def verify_signature(public_key_str: str, data: bytes, signature: bytes) -> bool:
    """
    Verify that the signature was produced by the owner
    of the corresponding private key.
    """
    
    # 1. Step: Try to load the key
    try:
      public_key = load_public_key(public_key_str)
    except Exception as e:
       # If the key is malformed, we stop here with a clear message
       raise ValueError("Identity Verification Error: The public key is invalid or corrupted.")
    # 2. Step: Perform the actual cryptographic verification
    try:
      public_key.verify(
        signature=signature,
        data=data,
        padding = padding.PSS(
          mgf=padding.MGF1(hashes.SHA256()),
          salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=hashes.SHA256()
      )
      return True
    except InvalidSignature:
       raise ValueError("The signature does not match the provided file content.")
    except Exception:
      raise ValueError("Technical error during signature verification")
    
def format_signature_to_b64(signature_bytes: bytes):
  """
  Standardizes how we turn raw signature math into a safe text string.
  we need this function, when we sind the signature to the user in FE
  """
  if not signature_bytes:
    return ""
  return base64.b64encode(signature_bytes).decode(encoding='utf-8')