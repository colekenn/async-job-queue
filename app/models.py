from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base

# use JSONB if Postgres; the dialect import above will only apply on Postgres
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(100), index=True, nullable=False)
    payload = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=5)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    idempotency_key = Column(String(200), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now())
