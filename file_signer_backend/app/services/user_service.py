from app.schemas.user_schema import  UserCreate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import MultipleResultsFound
from app.models.user_model import User
from app.models.user_keys_model import UserKey
from app.security.password import hash_password
from app.security.jwt import create_access_token
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def register_user(db: Session,user: UserCreate):

    if len(user.password)<8:
        raise ValueError("password must be at least 8")
    
    existing_email = db.query(User).filter(User.
    email==user.email).first()
    if existing_email:
        raise ValueError("This Email is already registered.")
    
    existing_username=db.query(User).filter(User.username==user.username).first()

    if existing_username:
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

    return db_user 
def authenticate_user(db:Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not pwd_context.verify(password, user.passwordhash):
        return None
    return user
    
# not used any more 
def autenticate_user(db: Session, email: str, password: str) -> str:
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