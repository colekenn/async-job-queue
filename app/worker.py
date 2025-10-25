import os
import time
import json
import signal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Job, Base
from app.database import DATABASE_URL
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = "job_queue"
r = redis.from_url(REDIS_URL, decode_responses=True)

# SQLAlchemy session (worker process)
engine = create_engine(os.getenv("DATABASE_URL", DATABASE_URL), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

STOP = False
def handle_sigterm(*args):
    global STOP
    STOP = True

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

def process_job(job_id: int, db):
    job = db.query(Job).filter(Job.id == job_id).with_for_update().first()
    if not job:
        print(f"[worker] job {job_id} not found")
        return

    # If job already succeeded do nothing
    if job.status == "succeeded":
        return

    print(f"[worker] processing job {job.id} type={job.job_type} attempts={job.attempts}")
    job.status = "processing"
    db.commit()
    try:
        # Here implement actual job handling logic by job.job_type.
        # For demo, we'll simulate work and echo payload.
        # Simulate variable runtime
        simulated = job.payload.get("simulate_seconds", 1) if job.payload else 1
        time.sleep(float(simulated))

        # sample "processing result"
        result = {"echo": job.payload, "processed_at": time.time()}

        job.result = result
        job.status = "succeeded"
        job.error = None
        job.attempts = job.attempts + 1
        db.commit()
        print(f"[worker] job {job.id} succeeded")
    except Exception as exc:
        # on failure: increment attempts and requeue if attempts < max_attempts
        job.attempts = job.attempts + 1
        job.error = str(exc)
        if job.attempts < job.max_attempts:
            backoff = min(2 ** job.attempts, 60)
            job.status = "pending"
            db.commit()
            # schedule requeue after backoff by sleeping in this worker (simple)
            print(f"[worker] job {job.id} failed, retrying after {backoff}s (attempt {job.attempts})")
            time.sleep(backoff)
            r.rpush(QUEUE_NAME, job.id)
        else:
            job.status = "failed"
            db.commit()
            print(f"[worker] job {job.id} failed permanently after {job.attempts} attempts")

def main_loop():
    print("[worker] starting main loop, listening for jobs")
    while not STOP:
        try:
            # BLPOP blocks until an item is available (timeout 5 to allow clean shutdown)
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
        except Exception as exc:
            print("[worker] exception in loop:", exc)
            time.sleep(1)

if __name__ == "__main__":
    # ensure tables exist (if not created by web)
    Base.metadata.create_all(bind=engine)
    main_loop()
