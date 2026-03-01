from app.schemas.user_schema import  UserCreate
from sqlalchemy.orm import Session
from app.models.user_model import User
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

def get_user_public_key(user: User):
    if not user.public_key:
        raise ValueError("User has no public key yet: Sign a file first")
    return user.public_key
      