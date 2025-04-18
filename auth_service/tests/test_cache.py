# tests/test_cache.py
import pytest
from utils.cache import redis_client


async def test_cache():
    # Set giá trị vào cache
    await redis_client.set("test_key", "test_value", ex=60)

    # Lấy giá trị từ cache
    value = await redis_client.get("test_key")
    assert value == "test_value"

    # Xóa cache
    await redis_client.delete("test_key")
    value = await redis_client.get("test_key")
    assert value is None