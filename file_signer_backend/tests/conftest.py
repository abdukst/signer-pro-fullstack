# Global test configurations & fixtures
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

from app.schemas.user_schema import UserCreate
from app.services.user_service import register_user

# Create a clean, isolated SQLite database entirely in RAM for the test run
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
  """
  generate an isolated in-memory database, builds the clean tables,
  yields a session to a test, and completely destroys it afterward.
  """

  engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
  )

  TestingSessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind=engine
  )

  # Generate all tables (users, files, user_keys) fresh in RAM
  Base.metadata.create_all(bind=engine)

  session = TestingSessionLocal()

  try:
    yield session
  finally:
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Helper fixture to automatically generate a clean user 
    for any test that requires a registered account.
    """
    user_data = UserCreate(
        email="signer@example.com",
        username="filesigner",
        fullname="File Signer",
        password="password"
    )
    return register_user(db_session, user_data)

