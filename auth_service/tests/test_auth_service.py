import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from models.user import User
from services.auth_service import register_user, authenticate_user
from pydantic import BaseModel


class UserRegisterData(BaseModel):
    username: str
    email: str
    password: str


class UserLoginData(BaseModel):
    email: str
    password: str


@pytest.fixture
def db_session():
    # Tạo mock session
    session = MagicMock(spec=Session)
    return session


def test_register_user_success(db_session):
    # Arrange
    user_data = UserRegisterData(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    db_session.query().filter().first.return_value = None

    # Act
    with patch('services.auth_service.SessionLocal', return_value=db_session):
        result = register_user(user_data)

    # Assert
    assert result is not None
    assert db_session.add.called
    assert db_session.commit.called


def test_register_user_existing_email(db_session):
    # Arrange
    user_data = UserRegisterData(
        username="testuser",
        email="existing@example.com",
        password="password123"
    )
    db_session.query().filter().first.return_value = User()

    # Act
    with patch('services.auth_service.SessionLocal', return_value=db_session):
        result = register_user(user_data)

    # Assert
    assert result is None


def test_authenticate_user_success(db_session):
    # Arrange
    user_data = UserLoginData(
        email="test@example.com",
        password="password123"
    )
    mock_user = User()
    mock_user.email = "test@example.com"
    mock_user.hashed_password = "hashed_password"
    db_session.query().filter().first.return_value = mock_user

    # Act
    with patch('services.auth_service.SessionLocal', return_value=db_session), \
            patch('services.auth_service.verify_password', return_value=True):
        result = authenticate_user(user_data)

    # Assert
    assert result is not None


def test_authenticate_user_invalid_credentials(db_session):
    # Arrange
    user_data = UserLoginData(
        email="wrong@example.com",
        password="wrongpassword"
    )
    db_session.query().filter().first.return_value = None

    # Act
    with patch('services.auth_service.SessionLocal', return_value=db_session):
        result = authenticate_user(user_data)

    # Assert
    assert result is None
