from app.schemas.user_schema import  UserCreate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import MultipleResultsFound
from app.models.user_model import User
from app.models.user_keys_model import UserKey
from app.security.password import hash_password
from app.security.jwt import create_access_token
from passlib.context import CryptContext
from datetime import datetime, timezone

import logging


logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def register_user(db: Session,user: UserCreate):

    if len(user.password)<8:
        raise ValueError("password must be at least 8")
    
    existing_email = db.query(User).filter(User.
    email==user.email).first()
    if existing_email:
        logger.warning(f"Registration attempt failed: Email {user.email} already exists.")
        raise ValueError("This Email is already registered.")
    
    existing_username=db.query(User).filter(User.username==user.username).first()

    if existing_username:
        logger.warning(f"Registration attempt failed: Username {user.username} already taken.")
        raise ValueError("This username is already taken.")

    hashed_password = hash_password(user.password)

    db_user = User(
       email = user.email,
       username = user.username,
       fullname = user.fullname,
       passwordhash = hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"NEW USER REGISTERED: ID {db_user.id} | Email: {db_user.email}")
    return db_user 
def authenticate_user(db:Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"AUTH FAILED: No account found for email: {email}")
        return None
    if not pwd_context.verify(password, user.passwordhash):
        logger.warning(f"AUTH FAILED: Incorrect password for user: {email}")
        return None
    
    logger.info(f"AUTH SUCCESS: User {email} logged in.")
    return user
    
    user = db.query(User).filter(User.email == email).first()
    print(user)

    if not user:
        return None
    if not pwd_context.verify(password, user.passwordhash):
        return None
    return create_access_token(subject=str(user.id))

def get_user_public_key(db: Session,user_id: int):
    user_aktive_key = get_user_active_key(db=db, user_id=user_id)
    if not user_aktive_key:
        raise ValueError("User has no public key yet: Sign a file first")
    return user_aktive_key.public_key
      
def get_user_active_key(db:Session, user_id: int) -> UserKey | None:
    try:
        return db.query(UserKey).filter(
            UserKey.user_id == user_id,
            UserKey.is_active == True
            # one_or_none() is an "Integrity Check. It tells SQLAlchemy: "I expect 0 or 1. If you find 2, scream loudly (raise an error)." This is much safer for a cryptographic system.
        ).one_or_none()
    except MultipleResultsFound:
        # This triggers if the Unique Index failed or wasn't applied correctly
        # and somehow two keys are marked 'is_active=True'.
        raise ValueError("Critical Security Error: Multiple active keys found for this account. Please contact support.")
    except SQLAlchemyError:
        # This catches "Database Locked", "Connection Lost", etc.
        # We log the real error 'e' internally, but show the user a clean message.
        raise ValueError("A database error occurred while retrieving your security keys.")
    except Exception:
        # any other error
        raise ValueError("Could not load your key. Pleas try again")

def rotate_user_key(db: Session, user: User, password: str):
    """
    Verifies the password and deactivates the current active key.
    """
    #We ask the user to provide their password again in the request to "confirm" the rotation, ensuring a hacker with a stolen browser session can't randomly rotate their keys
    logger.info(f"KEY ROTATION INITIATED: User {user.email}")
    if not pwd_context.verify(password, user.passwordhash):
        logger.warning(f"Key rotation DENIED: Invalid password for user {user.email}")
        raise ValueError("Invalid password. Rotation denied.")
    
    # get the user active key that should be deactivated
    active_user_key = get_user_active_key(db=db, user_id=user.id)
    if not active_user_key:
        logger.error(f"KEY ROTATION ERROR: No active key found for user {user.id}")
        raise ValueError("No active key found to rotate.")
    try:
        # Deactivate the key and save the changes
        active_user_key.is_active = False
        active_user_key.revoked_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"KEY ROTATION SUCCESS: Key {active_user_key.key_fingerprint} revoked for user {user.email}")
    except Exception as e:
        db.rollback()
        logger.error(f"Key rotation FAILED for user {user.email}: {str(e)}", exc_info=True)
        raise e

def get_user_profile(db: Session, user: User):
    logger.info(f"PROFILE VIEWED: User Email: {user.email}")
    active_key = get_user_active_key(db = db, user_id = user.id)
    # Attach these temporary attributes to the user object.
    # Pydantic will pick these up because they match the names in UserResponse.
    if active_key:
        user.active_key_fingerprint = active_key.key_fingerprint
        user.active_public_key = active_key.public_key
        user.key_status = active_key.is_active

    return user
