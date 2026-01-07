
FROM python:3.11-slim AS builder

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip


COPY WAREHOUSE_ZEEL/Zeel_backend/requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt




