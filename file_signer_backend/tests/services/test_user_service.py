import pytest
from unittest.mock import patch
from app.schemas.user_schema import UserCreate
from app.services.user_service import register_user, authenticate_user, get_user_active_key, get_user_public_key, rotate_user_key, get_user_profile
from app.security.key_service import initialize_user_keys

def test_register_user(db_session):
  user_data = UserCreate(
    email="test@kst.com",
    username="test",
    fullname="test test",
    password="password"
  )

  new_user = register_user(db_session, user_data)
  """
  Verifies that a valid registration payload successfully saves
  a user and hashes their password.
  """
  assert new_user.id is not None
  assert new_user.email == "test@kst.com"
  assert new_user.username == "test"
  assert new_user.fullname == "test test"
  assert new_user.passwordhash != "password"

def test_register_user_duplicate_email(db_session):
  """
  Ensures that trying to register an already existing email
  is caught and raises a clear ValueError.
  """
  user_data1 = UserCreate(
    email="test@kst.com",
    username="test1",
    fullname="test1 test",
    password="password1"
  )  
  user_data2 = UserCreate(
    email="test@kst.com",
    username="test2",
    fullname="test2 test",
    password="password2"
  )
  register_user(db_session, user_data1)
  with pytest.raises(ValueError, match="This Email is already registered."):
    register_user(db_session, user_data2)

def test_register_user_password_username(db_session):
  """
  Ensures that password length > 8.
  Ensures that username is unique.
  """
  # PASSWORD TEST
  user_data = UserCreate(
    email="test@kst.com",
    username="test1",
    fullname="test1 test",
    password="pass"
  )
  with pytest.raises(ValueError, match="password must be at least 8"):
    register_user(db_session, user_data)

  # USERNAME TEST
  user_data1 = UserCreate(
    email="test1@kst.com",
    username="test",
    fullname="test1 test",
    password="password1"
  )
  user_data2 = UserCreate(
    email="test2@kst.com",
    username="test",
    fullname="test2 test",
    password="password2"
  )
  register_user(db_session, user_data1)
  with pytest.raises(ValueError, match="This username is already taken."):
    register_user(db_session, user_data2)

def test_authenticate_user(db_session):
  """
  Validates that user login verification accurately flags right and wrong credential inputs.
  """
  
  user_data = UserCreate(
    email="test@kst.com",
    username="test",
    fullname="test test",
    password="password"
  )

  # User is not registered
  not_registered_user = authenticate_user(db_session,user_data.email, user_data.password)
  assert not_registered_user is None

  
  register_user(db_session, user_data)

  # Bad Password
  bad_password_user = authenticate_user(db_session,user_data.email, "falsePassword")

  assert bad_password_user is None

  # Success authentication
  verified_user = authenticate_user(db_session,user_data.email, user_data.password)
  assert verified_user is not None
  assert verified_user.email == user_data.email


def test_get_user_public_key(db_session):
  """
  Tests getting user public key, handling users with no keys.
  """
    # 1 register New user
  user_data = UserCreate(
    email="test@kst.com",
    username="test",
    fullname="test test",
    password="password"
  )

  user = register_user(db_session, user_data)

  # path 1 user has no key.
  with pytest.raises(ValueError, match="User has no public key yet: Sign a file first"):
    get_user_public_key(db_session, user.id)
  
  # initialize user key.
  user_key = initialize_user_keys(user.id, user_data.password)
  db_session.add(user_key)
  db_session.commit()

  # path 2: user has key
  assert get_user_public_key(db_session, user.id) is not None

def test_get_user_active_key(db_session):
  """
  Tests finding an active key, handling users with no keys, 
  and triggering the critical security warning if multiple active keys exist.
  """

  # register New user
  user_data = UserCreate(
    email="test@kst.com",
    username="test",
    fullname="test test",
    password="password"
  )

  user = register_user(db_session, user_data)
  # Path 1: User has no key yet (Should return None cleanly)
  assert get_user_active_key(db_session, user.id) is None

  user_key = initialize_user_keys(user.id, user_data.password)
  db_session.add(user_key)
  db_session.commit()

   # Path 2: User has  key.
  assert get_user_active_key(db_session,user.id) is not None


  # Path 3: Multikeys found

  # We mock the query execution to simulate what happens if the database 
  # somehow bypassed the unique index constraint and returned multiple active keys.
  from sqlalchemy.orm.exc import MultipleResultsFound
  from sqlalchemy.exc import SQLAlchemyError

  # mocking the MultipleResultsFound exception
  # We force the query or the session to throw MultipleResultsFound
  with patch("sqlalchemy.orm.Query.one_or_none", side_effect=MultipleResultsFound):
    with pytest.raises(ValueError, match="Critical Security Error: Multiple active keys found for this account. Please contact support."):
      get_user_active_key(db_session,user.id)
  
  # path 4: connection to Database lost
  with patch("sqlalchemy.orm.Query.one_or_none", side_effect=SQLAlchemyError("Connection timed out")):
    with pytest.raises(ValueError, match="A database error occurred while retrieving your security keys."):
      get_user_active_key(db_session, user.id)
  
  # path 5: fallback, any other errors
  with patch("sqlalchemy.orm.Query.one_or_none", side_effect=RuntimeError("Unexpected system failure")):
  # Verify it triggers the fallback ValueError message
    with pytest.raises(ValueError, match="Could not load your key. Pleas try again"):
      get_user_active_key(db_session, user.id)

def test_rotate_user_key(db_session):
  """
  Verifies that key rotation cleanly deactivates keys and sets timestamps,
  while securely rejecting incorrect password confirmations.
  """

  # register New user
  user_data = UserCreate(
    email="test@kst.com",
    username="test",
    fullname="test test",
    password="password"
  )

  user = register_user(db_session, user_data)

  # inialize user key
  user_key = initialize_user_keys(user.id, user_data.password)
  db_session.add(user_key)
  db_session.commit()

  # 1 path: password wrong.
  with pytest.raises(ValueError, match="Invalid password. Rotation denied."):
    rotate_user_key(db_session, user, "falsePasswor")
  
  # 2 path: successful scenario
  rotate_user_key(db_session, user, user_data.password)
  assert user_key.is_active is False

  # 3 path: user has no active key.
  with pytest.raises(ValueError, match="No active key found to rotate."):
    rotate_user_key(db_session, user, user_data.password)
  
  # 4 path: unexpected errors
    # 4a. Initialize a new key so the function can reach the commit phase again
  new_user_key = initialize_user_keys(user.id, user_data.password)
  db_session.add(new_user_key)
  db_session.commit()

  # 4b. Temporarily force the real session's commit function to fail
  with patch.object(db_session, "commit", side_effect=Exception("Database disk full during rotation")):
    # 4c. Verify that the function catches the crash and bubbles it up
    with pytest.raises(Exception, match="Database disk full during rotation"):
      rotate_user_key(db_session, user, user_data.password)

  # 4c. PROOF OF ROLLBACK: Refresh the key from the real SQLite memory.
  # If rollback worked, changes were discarded and it must still be active (True).
  assert new_user_key.is_active is True

def test_get_user_profile(db_session):
  """
  Validates that the profile service accurately maps key metadata dynamically
  onto the User object attributes so Pydantic can read them.
  """
  # register New user
  user_data = UserCreate(
    email="test@kst.com",
    username="test",
    fullname="test test",
    password="password"
  )
  user = register_user(db_session, user_data)

  # inialize user key
  user_key = initialize_user_keys(user.id, user_data.password)
  db_session.add(user_key)
  db_session.commit()

  user_profile = get_user_profile(db_session, user)

  assert user_profile.email == "test@kst.com"
  assert user_profile.username == "test"
  assert user_profile.fullname == "test test"
  assert user_profile.active_key_fingerprint is not None
  assert user_profile.active_public_key is not None
  assert user_profile.key_status is True

  




  






    













  









 



  