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

## API Usage Examples

### Using PowerShell (Windows):

**Create a job:**
```powershell
$body = @{
    job_type = "process_data"
    payload = @{
        data = "example"
        simulate_seconds = 2
    }
    idempotency_key = "unique-key-123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/jobs" `
    -Method Post `
    -Headers @{
        "x-api-key" = "my-demo-key"
        "Content-Type" = "application/json"
    } `
    -Body $body
```

**Get a job by ID:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/jobs/1"
```

**List all jobs:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/jobs"
```

**List jobs by status:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/jobs?status=pending&limit=10"
```

**View worker logs (to see jobs being processed):**
```powershell
docker compose logs worker -f
```

### Using curl (Linux/Mac):

**Create a job:**
```bash
curl -X POST "http://localhost:8000/jobs" \
  -H "Content-Type: application/json" \
  -H "x-api-key: my-demo-key" \
  -d '{
    "job_type": "process_data",
    "payload": {"data": "example", "simulate_seconds": 2},
    "idempotency_key": "unique-key-123"
  }'
```

**Get a job by ID:**
```bash
curl "http://localhost:8000/jobs/1"
```

**List all jobs:**
```bash
curl "http://localhost:8000/jobs"
```

**List jobs by status:**
```bash
curl "http://localhost:8000/jobs?status=pending&limit=10"
```

## Services

- **Web API** (port 8000): FastAPI server for creating and querying jobs
- **Worker**: Background process that processes jobs from the Redis queue
- **PostgreSQL**: Database for storing job records
- **Redis**: Message queue for job processing

## Quick Test Guide

1. **Start the services:**
   ```powershell
   docker compose up --build
   ```

2. **Open the API docs in your browser:**
   - Go to: http://localhost:8000/docs
   - This gives you an interactive UI to test all endpoints

3. **Or test via PowerShell:**
   ```powershell
   # Create a job
   $body = @{job_type='test'; payload=@{simulate_seconds=1}} | ConvertTo-Json
   Invoke-RestMethod -Uri 'http://localhost:8000/jobs' -Method Post -Headers @{'x-api-key'='my-demo-key'; 'Content-Type'='application/json'} -Body $body
   
   # Check job status (replace 1 with your job ID)
   Invoke-RestMethod -Uri 'http://localhost:8000/jobs/1'
   
   # Watch worker process jobs
   docker compose logs worker -f
   ```

## Technologies Used

- **FastAPI**: Modern Python web framework for building APIs
- **PostgreSQL**: Relational database for job persistence
- **Redis**: In-memory data store for job queue and rate limiting
- **SQLAlchemy**: Python ORM for database operations
- **Docker & Docker Compose**: Containerization and orchestration
- **Pydantic**: Data validation using Python type annotations
