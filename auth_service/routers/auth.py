# auth.py
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from services.auth_service import register_user, authenticate_user
from utils.security import create_access_token, SECRET_KEY, ALGORITHM, hash_password, verify_password
from utils.cache import cache_response, invalidate_cache
from database import SessionLocal, get_db
from models.user import User
from sqlalchemy.orm import Session
from uuid import UUID

import logging

logger = logging.getLogger(__name__)



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # change tokenUrl accordingly

# Global in‑memory storage for token blacklisting (logout and token revocation)
blacklisted_tokens = set()


# Dependency to get the current authenticated user
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to retrieve the current authenticated user.

    Raises:
        HTTPException: If the token is blacklisted, invalid, or user is not found.
    """
    if token in blacklisted_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


class UserResponse(BaseModel):
    id: UUID
    username: Optional[str] = None
    email: str
    full_name: Optional[str] = None
    is_active: bool
    age: Optional[int] = None
    gender: Optional[str] = None
    russian_level: Optional[str] = None
    gemini_api_key: Optional[str] = None
    # Exam time fields
    time_start: Optional[datetime] = None
    duration: Optional[int] = None
    time_end: Optional[datetime] = None

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    russian_level: Optional[str] = None
    gemini_api_key: Optional[str] = None


class UpdateEmailRequest(BaseModel):
    email: str


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


class UserRegister(BaseModel):
    username: Optional[str] = None
    email: str
    password: str
    full_name: str
    gemini_api_key: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/register",
             summary="User registration",
             response_model=RegisterResponse,
             status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """
    Register a new user with the following information:
    - username: the user's username (optional)
    - email: the user's email address
    - password: the user's password
    - full_name: the user's full name
    - gemini_api_key: the user's Gemini API key (optional)

    Returns:
        JSON response containing a success message and user details.

    Raises:
        HTTPException: If registration fails due to existing email or username.
    """
    created_user = register_user(user)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email or username already exists."
        )
    return RegisterResponse(
        message="Registration successful",
        user=created_user
    )


@router.post("/login",
             summary="User login",
             response_model=TokenResponse)
async def login(user: UserLogin, request: Request):
    """
    Authenticate a user and return access and refresh tokens.

    Parameters:
        user: User login data including email and password.
        request: The incoming request.

    Returns:
        JSON response containing access token, refresh token, and token type.

    Raises:
        HTTPException: If the email or password is incorrect.
    """
    tokens = authenticate_user(user)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    return tokens


@router.post("/refresh-token",
             summary="Refresh access token",
             response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest):
    """
    Generate a new access token using a valid refresh token.

    Parameters:
        data: Refresh token payload.

    Returns:
        JSON response containing the new access token along with the refresh token.

    Raises:
        HTTPException: If the refresh token is invalid or expired.
    """
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = {
            "sub": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "username": payload.get("username")
        }
        new_access_token = create_access_token(token_data)
        return {
            "access_token": new_access_token,
            "refresh_token": data.refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired"
        )


@router.post("/logout", summary="Logout user")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout the user by blacklisting the current authentication token.

    Parameters:
        token: The token extracted from the request.

    Returns:
        JSON message confirming successful logout.
    """
    blacklisted_tokens.add(token)
    return {"message": "Successfully logged out"}


@router.post("/revoke-token", summary="Revoke token")
async def revoke_token(token: str = Depends(oauth2_scheme)):
    """
    Revoke the provided token explicitly by blacklisting it.

    Parameters:
        token: The token to revoke.

    Returns:
        JSON message indicating the token has been revoked.
    """
    blacklisted_tokens.add(token)
    return {"message": "Token has been revoked"}


@router.post("/verify-email/initiate", summary="Initiate email verification")
async def initiate_email_verification(current_user: User = Depends(get_current_user)):
    """
    Generate a verification token for email confirmation and simulate sending it.
    In production, this token should be emailed to the user.

    Parameters:
        current_user: The currently authenticated user.

    Returns:
        JSON message with the verification token.
    """
    token = create_access_token(
        {"sub": current_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"message": "Verification email sent", "verification_token": token}


@router.get("/verify-email",
            summary="Verify user email",
            status_code=status.HTTP_200_OK)
async def verify_email(token: str):
    """
    Verify the user's email using the provided token.

    Parameters:
        token: The email verification token.

    Returns:
        JSON message indicating successful email verification.

    Raises:
        HTTPException: If the token payload is invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        db.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.email_verified = True
    db.add(user)
    db.commit()
    db.close()
    return {"message": "Email successfully verified"}


@router.post("/forgot-password", summary="Initiate password reset flow", status_code=status.HTTP_200_OK)
async def forgot_password(request_data: ForgotPasswordRequest):
    """
    Accept an email address and, if a user exists, create a short-lived reset token.
    In production, this token should be emailed to the user.

    Parameters:
        request_data: Contains the user's email.

    Returns:
        JSON message confirming that if the email exists, a reset link has been sent.
    """
    db = SessionLocal()
    user = db.query(User).filter(User.email == request_data.email).first()
    db.close()
    # Always return the same response to avoid email harvesting
    if user:
        reset_token = create_access_token(
            {"sub": user.email},
            expires_delta=timedelta(minutes=15)
        )
        return {"message": "If your email exists in the system, a password reset link was sent.",
                "reset_token": reset_token}
    return {"message": "If your email exists in the system, a password reset link was sent."}


@router.post("/reset-password", summary="Reset password using token", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetPasswordRequest):
    """
    Reset the user's password after verifying the provided reset token.

    Parameters:
        data: Contains the reset token and the new password.

    Returns:
        JSON confirmation message that the password has been reset.

    Raises:
        HTTPException: If the token is invalid, expired, or if the user is not found.
    """
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        db.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    db.commit()
    db.close()
    return {"message": "Password has been reset successfully"}


@router.post("/change-password", summary="Change password for authenticated user", status_code=status.HTTP_200_OK)
async def change_password(
        data: ChangePasswordRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Change the password for the authenticated user after verifying the old password.

    Parameters:
        data: Contains the old and new passwords.
        current_user: The currently authenticated user.

    Returns:
        JSON confirmation message that the password has been changed.

    Raises:
        HTTPException: If the old password is incorrect or the user is not found.
    """
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.hashed_password = hash_password(data.new_password)
        db.commit()
        db.close()
        return {"message": "Password has been changed successfully"}
    db.close()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get("/profile", summary="Retrieve current user profile", response_model=UserResponse)
@cache_response(expire_time_seconds=300)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieve the profile of the currently authenticated user.

    Parameters:
        current_user: The currently authenticated user.

    Returns:
        JSON response containing user profile details.
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "age": current_user.age,
        "gender": current_user.gender,
        "russian_level": current_user.russian_level,
        "gemini_api_key": current_user.gemini_api_key,
        "time_start": current_user.time_start,
        "duration": current_user.duration,
        "time_end": current_user.time_end
    }
    # return current_user


@router.put("/profile", summary="Update user profile", response_model=UserResponse)
async def update_profile(
        request: UpdateUserRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)

):

    try:
        # Lấy user mới từ database
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Kiểm tra nếu username được cập nhật
        if request.username and request.username != user.username:
            # Kiểm tra username mới đã tồn tại chưa
            existing_user = db.query(User).filter(
                User.username == request.username,
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken"
                )

        # Cập nhật thông tin
        for key, value in request.dict(exclude_unset=True).items():
            setattr(user, key, value)

        try:
            db.commit()
            # Xóa cache
            await invalidate_cache(f"get_user_by_id:{user.id}")
            await invalidate_cache(f"get_user_by_email:{user.email}")

            # Refresh sau khi commit
            db.refresh(user)

            return user

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()



@router.put("/profile/email", summary="Update user email and reset verification", response_model=UserResponse)
async def update_email(
        update_data: UpdateEmailRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Update the user's email and reset email verification status.

    Parameters:
        update_data: Contains the new email.
        current_user: The currently authenticated user.

    Returns:
        The updated user profile.

    Raises:
        HTTPException: If the user is not found.
    """
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.email != update_data.email:
        user.email = update_data.email
        user.email_verified = False
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    return user


@router.delete("/profile", summary="Deactivate user account", status_code=status.HTTP_200_OK)
async def delete_account(current_user: User = Depends(get_current_user)):
    """
    Deactivate the account of the currently authenticated user.
    Instead of a hard delete, the user account is set as inactive.

    Parameters:
        current_user: The currently authenticated user.

    Returns:
        JSON message confirming account deactivation.

    Raises:
        HTTPException: If the user is not found.
    """
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    db.add(user)
    db.commit()
    db.close()
    return {"message": "User account has been deactivated"}


@router.delete("/profile/permanent", summary="Permanently delete user account", status_code=status.HTTP_200_OK)
async def delete_account_permanent(current_user: User = Depends(get_current_user)):
    """
    Permanently delete the account of the currently authenticated user.
    This action removes the user from the database entirely.

    Parameters:
        current_user: The currently authenticated user.

    Returns:
        JSON message confirming permanent deletion.

    Raises:
        HTTPException: If the user is not found.
    """
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    db.close()
    return {"message": "User account has been permanently deleted"}


@router.post("/validate-token",
             summary="Validate JWT token",
             status_code=status.HTTP_200_OK)
async def validate_token(token: str = Depends(oauth2_scheme)):
    """
    Xác thực tính hợp lệ của JWT token.

    Parameters:
        token: JWT token cần xác thực (được truyền qua Authorization header)

    Returns:
        JSON response với thông tin user nếu token hợp lệ

    Raises:
        HTTPException: Nếu token không hợp lệ, hết hạn hoặc đã bị thu hồi
    """
    # Kiểm tra token có trong blacklist không
    if token in blacklisted_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    try:
        # Giải mã và xác thực token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Kiểm tra user có tồn tại trong database không
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        db.close()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Trả về thông tin cơ bản của user để xác nhận token hợp lệ
        return {
            "valid": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username
            }
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or token has expired"
        )
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
