# main.py

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from routers import auth, exam_time
from database import engine, Base, SessionLocal
from config import config
from sqlalchemy.sql import text

from schemas.health import ServiceHealth, HealthCheck, ServicesStatus
from utils.cache import cache_response, redis_client


VERSION = config.VERSION

app = FastAPI(
    title="Hyper OCR API",
    description="API Documentation for Hyper OCR",
    version="0.1.0",
    # root_path="/auth",  # Thêm dòng này
    # servers=[
    #     {"url": "/auth", "description": "API Gateway"},
    #     {"url": "http://localhost:8800", "description": "Direct Access"}
    # ]
)

# # Cấu hình CORS cho production
# origins = [
#     "https://your-frontend-domain.com",  # Domain chính thức của frontend
#     "http://localhost:3000",  # Development frontend
# ]


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')


# @app.get("/")
# async def root():
#     return {
#         "message": "Chào mừng đến với Hyper OCR API Authentication",
#         "docs": "docs",
#         "health": "health"
#     }


async def check_database() -> ServiceHealth:
    """Kiểm tra kết nối database"""
    try:
        db = SessionLocal()
        db.execute(text('SELECT 1'))
        db.close()
        return ServiceHealth(
            status="healthy",
            details="connected"
        )
    except Exception as e:
        return ServiceHealth(
            status="unhealthy",
            details=str(e)
        )


async def check_redis() -> ServiceHealth:
    """Kiểm tra kết nối Redis"""
    try:
        await redis_client.ping()
        return ServiceHealth(
            status="healthy",
            details="connected"
        )
    except Exception as e:
        return ServiceHealth(
            status="unhealthy",
            details=str(e)
        )


@app.get(
    "/health",
    tags=["Health Check"],
    response_model=HealthCheck,
    description="Kiểm tra trạng thái hoạt động của các services trong hệ thống"
)
@cache_response(expire_time_seconds=60)
async def health_check() -> HealthCheck:
    # Kiểm tra các services
    db_health = await check_database()
    redis_health = await check_redis()

    # Tổng hợp trạng thái
    services = ServicesStatus(
        database=db_health,
        redis=redis_health
    )

    # Xác định trạng thái tổng thể
    overall_status = "healthy"
    if db_health.status == "unhealthy" or redis_health.status == "unhealthy":
        overall_status = "unhealthy"

    return HealthCheck(
        status=overall_status,
        services=services,
        version=VERSION  # Thêm VERSION vào config.py
    )


# Tạo bảng khi khởi động
Base.metadata.create_all(bind=engine)

# Đăng ký các router
app.include_router(auth.router, prefix="/auth", tags=["Authentication Services"])
app.include_router(exam_time.router, prefix="/exam-time", tags=["Exam Time Management"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
