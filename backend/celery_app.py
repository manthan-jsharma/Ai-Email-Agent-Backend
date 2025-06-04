from backend.workers.ai_worker import celery
from backend.workers import ai_worker  # 👈 This registers the task

app = celery