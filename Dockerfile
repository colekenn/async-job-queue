FROM python:3.11-slim

WORKDIR /app

# install system deps for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# copy only what's needed
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# default command (used by web service)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
