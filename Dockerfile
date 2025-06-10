# Dockerfile
FROM python:3.11.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend


# CMD ["sh", "-c", "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers"]
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
