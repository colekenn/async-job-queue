# Async Job Queue - Demo

Lightweight async job queue with FastAPI + Redis + Postgres.

## Quick start (Docker)

The easiest way to run the app is using Docker Compose, which will start all services (PostgreSQL, Redis, FastAPI web server, and worker) together.

1. **Build and run all services:**
```bash
docker compose up --build
```

2. **Access the API:**
   - API will be available at: http://localhost:8000
   - API documentation (Swagger UI): http://localhost:8000/docs
   - Alternative API docs (ReDoc): http://localhost:8000/redoc

3. **Stop the services:**
```bash
docker compose down
```

4. **Run in detached mode (background):**
```bash
docker compose up -d --build
```

## Running Locally (without Docker)

If you prefer to run the app locally without Docker:

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (running locally)
- Redis 7+ (running locally)

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/jobsdb"
$env:REDIS_URL="redis://localhost:6379/0"
$env:API_KEY="my-demo-key"
$env:RATE_LIMIT_PER_MIN="30"

# Linux/Mac
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/jobsdb"
export REDIS_URL="redis://localhost:6379/0"
export API_KEY="my-demo-key"
export RATE_LIMIT_PER_MIN="30"
```

3. **Start the web server:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. **In a separate terminal, start the worker:**
```bash
python -m app.worker
```

## Services

- **Web API** (port 8000): FastAPI server for creating and querying jobs
- **Worker**: Background process that processes jobs from the Redis queue
- **PostgreSQL**: Database for storing job records
- **Redis**: Message queue for job processing
