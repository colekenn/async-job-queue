from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class JobCreate(BaseModel):
    job_type: str
    payload: Optional[Dict[str, Any]] = {}


class JobOut(BaseModel):
    id: int
    job_type: str
    payload: Optional[Dict[str, Any]] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
