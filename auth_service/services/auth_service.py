# auth_service.py
import logging
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models.user import User
from utils.cache import cache_response, invalidate_cache
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from datetime import datetime, timezone

# Thêm cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def register_user(user_data):
    db = SessionLocal()
    try:
        # Kiểm tra email đã tồn tại
        query = User.email == user_data.email
        if user_data.username:
            query = query | (User.username == user_data.username)
        existing_user = db.query(User).filter(query).first()
        if existing_user:
            logger.warning(f"Attempt to register with existing email/username: {user_data.email}")
            return None

        # Tạo user mới
        hashed_password = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            gemini_api_key=user_data.gemini_api_key,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        user_response = {
            "id": str(db_user.id),
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "gemini_api_key": db_user.gemini_api_key,
            "is_active": db_user.is_active
        }
        logger.info(f"Successfully registered new user: {user_data.email}")
        return user_response
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()


def authenticate_user(user_data):
    db = SessionLocal()
    try:
        # Tìm user theo email
        user = db.query(User).filter(User.email == user_data.email).first()

        # Nếu không tìm thấy user hoặc mật khẩu không đúng
        if not user or not verify_password(user_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {user_data.email}")
            return None

        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "username": user.username
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Cập nhật thời gian đăng nhập gần nhất
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        db.commit()

        logger.info(f"Successful login for user: {user_data.email}")

        return {"access_token": access_token, "refresh_token": refresh_token}

    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return None
    finally:
        db.close()


@cache_response(expire_time_seconds=300)
async def get_user_by_email(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    finally:
        db.close()


@cache_response(expire_time_seconds=300)
async def get_user_by_id(user_id: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    finally:
        db.close()
