# schemas/health.py
from pydantic import BaseModel
from typing import Optional, Literal


class ServiceHealth(BaseModel):
    status: Literal["healthy", "unhealthy"]
    details: str


class ServicesStatus(BaseModel):
    database: ServiceHealth
    redis: ServiceHealth


class HealthCheck(BaseModel):
    status: Literal["healthy", "unhealthy"]
    services: ServicesStatus
    version: str
