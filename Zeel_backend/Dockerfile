
FROM python:3.11-slim AS builder

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt



FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local


COPY . .

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
