import os
import json
import time
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from . import models, schemas
import redis

# Create DB tables
Base.metadata.create_all(bind=engine)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

QUEUE_NAME = "job_queue"

app = FastAPI(title="Async Job Queue Demo")

API_KEY = os.getenv("API_KEY", "my-demo-key")
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# simple rate limiter: allow RATE_LIMIT_PER_MIN per minute per API key
def allow_request(api_key: str) -> bool:
    key = f"rate:{api_key}"
    # increment, set ttl if new
    cur = r.incr(key)
    if cur == 1:
        r.expire(key, 60)
    return cur <= RATE_LIMIT_PER_MIN

@app.middleware("http")
async def check_rate_limit(request: Request, call_next):
    api_key = request.headers.get("x-api-key", API_KEY)
    if not allow_request(api_key):
        return JSONResponse(status_code=429, content={"detail": "rate limit exceeded"})
    response = await call_next(request)
    return response

@app.post("/jobs", response_model=schemas.JobOut)
def create_job(job_in: schemas.JobCreate, x_api_key: str = Header(None)):
    api_key = x_api_key or API_KEY

    # idempotency: if key provided and exists, return existing job
    with SessionLocal() as db:
        if job_in.idempotency_key:
            existing = db.query(models.Job).filter(models.Job.idempotency_key == job_in.idempotency_key).first()
            if existing:
                return existing

        job = models.Job(
            job_type=job_in.job_type,
            payload=job_in.payload,
            status="pending",
            idempotency_key=job_in.idempotency_key,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

    # push job id into redis queue
    r.rpush(QUEUE_NAME, job.id)
    return job

@app.get("/jobs/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int):
    with SessionLocal() as db:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        return job

@app.get("/jobs", response_model=list[schemas.JobOut])
def list_jobs(status: str = None, limit: int = 50):
    with SessionLocal() as db:
        q = db.query(models.Job).order_by(models.Job.created_at.desc())
        if status:
            q = q.filter(models.Job.status == status)
        return q.limit(limit).all()
