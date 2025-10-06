import os
import redis
from fastapi import FastAPI, HTTPException
from .database import engine, SessionLocal, Base
from . import models, schemas


Base.metadata.create_all(bind=engine)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

QUEUE_NAME = "job_queue"

app = FastAPI(title="Async Job Queue Demo")


@app.post("/jobs", response_model=schemas.JobOut)
def create_job(job_in: schemas.JobCreate):
    with SessionLocal() as db:
        job = models.Job(
            job_type=job_in.job_type,
            payload=job_in.payload,
            status="pending",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

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
