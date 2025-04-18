# config.py - Configuration file containing all environment variables
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables từ file .env


class Config:

    # Cấu hình ứng dụng
    VERSION = os.getenv("VERSION", "0.1.0")

    # Cấu hình bảo mật
    PORT = int(os.getenv("PORT", 8800))
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    # Cấu hình cơ sở dữ liệu
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rumai_db")

    # Cấu hình Redis (nếu sử dụng)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Thêm các cấu hình khác nếu cần (ví dụ: HOST, PORT, etc.)
    # HOST = os.getenv("HOST", "0.0.0.0")
    # PORT = int(os.getenv("PORT", 8000))


# Instance để sử dụng trong dự án
config = Config()
