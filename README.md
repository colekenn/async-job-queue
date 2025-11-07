# Async Job Queue - Demo

Lightweight async job queue with FastAPI + Redis + Postgres.

## Quick start (Docker)

The easiest way to run the app is using Docker Compose, which will start PostgreSQL, Redis, and the FastAPI web server together.

1. **Build and run all services:**
```bash
docker compose up --build
```

2. **Access the API:**
   - API will be available at: http://localhost:8000
   - API documentation (Swagger UI): http://localhost:8000/docs

3. **Stop the services:**
```bash
docker compose down
```

## Services

- **Web API** (port 8000): FastAPI server for creating and querying jobs
- **PostgreSQL**: Database for storing job records
- **Redis**: Message queue for job processing
