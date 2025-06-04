import asyncio
import redis
from celery import Celery
import os
import sys
from celery import Celery
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import generate_ai_response
from app.schemas import EmailRequest
from app.db import get_supabase, get_user_automation_settings

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "rediss://:AbREAAIjcDE4YzdkM2E5M2I1ZWQ0NGFiOTRmNGIwODE1ZWU2NzgxMnAxMA@wondrous-mite-46148.upstash.io:6379")

# Celery configuration
celery = Celery(
    'ai_worker',
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery.task(name="workers.ai_worker.process_email_with_ai")
def process_email_with_ai(user_email: str, email_id: str):
    """Process email with AI in background"""
    try:
        # This would be called asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            _process_email_async(user_email, email_id)
        )
        
        return result
    except Exception as e:
        print(f"Error processing email with AI: {e}")
        return {"error": str(e)}

async def _process_email_async(user_email: str, email_id: str):
    """Async function to process email with AI"""
    try:
        # Get email data from Supabase
        client = get_supabase()
        response = client.table('emails').select('*').eq('id', email_id).eq('user_email', user_email).execute()
        
        if len(response.data) == 0:
            return {"error": "Email not found"}
        
        email_row = response.data[0]
        
        # Create email request
        email_request = EmailRequest(
            user_email=user_email,
            email_id=email_id,
            thread_id=email_row['thread_id'],
            email_content=email_row['body']
        )
        
        # Generate AI response
        ai_response = await generate_ai_response(email_request)
        
        return {
            "success": True,
            "response_id": ai_response.response_id,
            "ai_response": ai_response.ai_response,
            "draft_id": ai_response.draft_id
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    celery.start()
