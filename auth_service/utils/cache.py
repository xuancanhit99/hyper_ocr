# utils/cache.py
import json

from fastapi.encoders import jsonable_encoder
from redis import asyncio as aioredis
from functools import wraps
from datetime import timedelta
from config import config
import logging

logger = logging.getLogger(__name__)

# Cấu hình Redis
REDIS_URL = config.REDIS_URL

# Khởi tạo Redis client
redis_client = aioredis.from_url(REDIS_URL, encoding='utf-8', decode_responses=True)


def cache_response(expire_time_seconds: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Tạo cache key
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                logger.info(f"Attempting to get from cache: {cache_key}")

                # Thử lấy từ cache
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit for health check - key: {cache_key}")
                    return json.loads(cached)

                # Nếu không có trong cache, gọi hàm gốc
                logger.debug(f"Cache miss for health check - key: {cache_key}")
                response = await func(*args, **kwargs)

                # Chuyển đổi response thành JSON trước khi cache
                cache_data = jsonable_encoder(response)

                # Lưu vào cache
                await redis_client.setex(
                    cache_key,
                    expire_time_seconds,
                    json.dumps(cache_data)
                )

                logger.debug(f"Cached health check result - key: {cache_key}")

                return response

            except Exception as e:
                logger.error(f"Cache error in health check: {str(e)}")
                # Fallback to original function if cache fails
                return await func(*args, **kwargs)

        return wrapper

    return decorator



async def invalidate_cache(pattern: str):
    """Xóa cache theo pattern"""
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
