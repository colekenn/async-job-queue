from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class JobCreate(BaseModel):
    job_type: str
    payload: Optional[Dict[str, Any]] = {}
    idempotency_key: Optional[str] = None

class JobOut(BaseModel):
    id: int
    job_type: str
    payload: Optional[Dict[str, Any]] = None
    status: str
    attempts: int
    max_attempts: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    idempotency_key: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
