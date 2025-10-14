import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Job, Base
from app.database import DATABASE_URL
import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = "job_queue"
r = redis.from_url(REDIS_URL, decode_responses=True)

engine = create_engine(os.getenv("DATABASE_URL", DATABASE_URL), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def process_job(job_id: int, db):
    job = db.query(Job).filter(Job.id == job_id).with_for_update().first()
    if not job:
        print(f"[worker] job {job_id} not found")
        return

    if job.status == "succeeded":
        return

    print(f"[worker] processing job {job.id} type={job.job_type}")
    job.status = "processing"
    db.commit()

    simulated = job.payload.get("simulate_seconds", 1) if job.payload else 1
    time.sleep(float(simulated))

    job.status = "succeeded"
    db.commit()
    print(f"[worker] job {job.id} succeeded")


def main_loop():
    print("[worker] starting main loop, listening for jobs")
    while True:
        item = r.blpop(QUEUE_NAME, timeout=5)
        if not item:
            continue
        _, job_id_raw = item
        try:
            job_id = int(job_id_raw)
        except (ValueError, TypeError):
            print("[worker] invalid job id in queue:", job_id_raw)
            continue

        with SessionLocal() as db:
            process_job(job_id, db)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    main_loop()
