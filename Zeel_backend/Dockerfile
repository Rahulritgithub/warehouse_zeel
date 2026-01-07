FROM python:3.11-slim

WORKDIR /app

# 👇 Adjusted path since requirements.txt is inside Zeel_backend/
COPY Zeel_backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY Zeel_backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
