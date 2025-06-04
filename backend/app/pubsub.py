


# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     """Handle Gmail Pub/Sub notifications"""
#     try:
#         body = await request.json()
        
#         if 'message' not in body:
#             raise HTTPException(status_code=400, detail="Invalid Pub/Sub message")
        
#         # Decode the message
#         message_data = body['message']['data']
#         decoded_data = base64.b64decode(message_data).decode('utf-8')
#         notification = json.loads(decoded_data)
        
#         # Extract email address and history ID
#         email_address = notification.get('emailAddress')
#         history_id = notification.get('historyId')
        
#         if not email_address or not history_id:
#             raise HTTPException(status_code=400, detail="Missing required fields")
        
#         # Process the email change in background
#         background_tasks.add_task(
#             process_email_notification,
#             email_address,
#             history_id
#         )
        
#         return {"status": "success", "message": "Notification processed"}
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# async def process_email_notification(email_address: str, history_id: str):
#     """Process Gmail notification and trigger AI response if needed"""
#     try:
#         # Get new emails from Gmail
#         new_emails = await process_new_email(email_address, history_id)
        
#         # For each new email, trigger AI processing
#         for email in new_emails:
#             if should_process_email(email):
#                 # Add to AI processing queue
#                 from .workers.ai_worker import process_email_with_ai
#                 process_email_with_ai.delay(email_address, email['id'])
                
#     except Exception as e:
#         print(f"Error processing email notification: {e}")

# def should_process_email(email):
#     """Determine if email should be processed by AI"""
#     # Process emails that are in inbox and unread
#     return 'INBOX' in email.get('labelIds', []) and 'UNREAD' in email.get('labelIds', [])

# @router.post("/setup-watch")
# async def setup_gmail_watch(user_email: str):
#     """Set up Gmail watch for a user"""
#     try:
#         from .gmail_service import setup_gmail_watch
#         result = await setup_gmail_watch(user_email)
#         return {"status": "success", "watch_response": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
# import json
# import base64
# import os
# from .gmail_service import process_new_email
# from .schemas import PubSubMessage

# router = APIRouter()

# # Pub/Sub configuration
# PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "mock_project_id")
# SUBSCRIPTION_NAME = os.getenv("GOOGLE_PUBSUB_SUBSCRIPTION", "gmail-notifications")

# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     """Handle Gmail Pub/Sub notifications"""
#     try:
#         body = await request.json()
#         message = body.get("message", {})
#         message_data = message.get("data")

#         if not message_data:
#             raise HTTPException(status_code=400, detail="Missing 'data' field in Pub/Sub message")

#         try:
#             decoded_bytes = base64.b64decode(message_data)
#             decoded_str = decoded_bytes.decode("utf-8")
#             notification = json.loads(decoded_str)
#         except (ValueError, json.JSONDecodeError) as decode_error:
#             raise HTTPException(status_code=400, detail=f"Invalid Pub/Sub message data: {decode_error}")

#         # Extract email address and history ID
#         email_address = notification.get('emailAddress')
#         history_id = notification.get('historyId')

#         if not email_address or not history_id:
#             raise HTTPException(status_code=400, detail="Missing required fields in notification")

#         # Process the email change in background
#         background_tasks.add_task(
#             process_email_notification,
#             email_address,
#             history_id
#         )

#         return {"status": "success", "message": "Notification processed"}

#     except Exception as e:
#         # Log raw body for debugging if needed
#         raw_body = await request.body()
#         print(f"Webhook error: {e}\nRaw body: {raw_body}")
#         raise HTTPException(status_code=500, detail=str(e))

# async def process_email_notification(email_address: str, history_id: str):
#     """Process Gmail notification and trigger AI response if needed"""
#     try:
#         # Get new emails from Gmail
#         new_emails = await process_new_email(email_address, history_id)

#         # For each new email, trigger AI processing
#         for email in new_emails:
#             if should_process_email(email):
#                 # Add to AI processing queue
#                 from .workers.ai_worker import process_email_with_ai
#                 process_email_with_ai.delay(email_address, email['id'])

#     except Exception as e:
#         print(f"Error processing email notification: {e}")

# def should_process_email(email):
#     """Determine if email should be processed by AI"""
#     return 'INBOX' in email.get('labelIds', []) and 'UNREAD' in email.get('labelIds', [])

# @router.post("/setup-watch")
# async def setup_gmail_watch(user_email: str):
#     """Set up Gmail watch for a user"""
#     try:
#         from .gmail_service import setup_gmail_watch
#         result = await setup_gmail_watch(user_email)
#         return {"status": "success", "watch_response": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
# import json
# import base64
# import os
# from .gmail_service import process_new_email
# from .schemas import PubSubMessage

# router = APIRouter()

# # Pub/Sub configuration
# PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "mock_project_id")
# SUBSCRIPTION_NAME = os.getenv("GOOGLE_PUBSUB_SUBSCRIPTION", "gmail-notifications")

# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     """Handle Gmail Pub/Sub notifications"""
#     try:
#         body = await request.json()
#         message = body.get("message", {})
#         message_data = message.get("data")

#         if not message_data:
#             raise HTTPException(status_code=400, detail="Missing 'data' field in Pub/Sub message")

#         # Attempt to decode and parse
#         try:
#             decoded_bytes = base64.b64decode(message_data)
#             decoded_str = decoded_bytes.decode("utf-8").strip()

#             if not decoded_str:
#                 raise HTTPException(status_code=400, detail="Decoded data is empty")

#             notification = json.loads(decoded_str)
#         except (ValueError, json.JSONDecodeError) as decode_error:
#             print(f"Decoding error: {decode_error}\nDecoded string: {decoded_str}")
#             raise HTTPException(status_code=400, detail=f"Invalid Pub/Sub message data: {decode_error}")

#         # Extract email address and history ID
#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             raise HTTPException(status_code=400, detail="Missing required fields in notification")

#         # Process in background
#         background_tasks.add_task(
#             process_email_notification,
#             email_address,
#             history_id
#         )

#         return {"status": "success", "message": "Notification processed"}

#     except HTTPException as http_err:
#         # Reraise cleanly for FastAPI
#         raise http_err

#     except Exception as e:
#         # Unexpected internal server error
#         raw_body = await request.body()
#         print(f"Webhook internal error: {e}\nRaw request body: {raw_body}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# async def process_email_notification(email_address: str, history_id: str):
#     """Process Gmail notification and trigger AI response if needed"""
#     try:
#         new_emails = await process_new_email(email_address, history_id)
#         for email in new_emails:
#             if should_process_email(email):
#                 from .workers.ai_worker import process_email_with_ai
#                 process_email_with_ai.delay(email_address, email["id"])
#     except Exception as e:
#         print(f"Error processing email notification: {e}")

# def should_process_email(email):
#     """Determine if email should be processed by AI"""
#     return "INBOX" in email.get("labelIds", []) and "UNREAD" in email.get("labelIds", [])

# @router.post("/setup-watch")
# async def setup_gmail_watch(user_email: str):
#     try:
#         from .gmail_service import setup_gmail_watch
#         result = await setup_gmail_watch(user_email)
#         return {"status": "success", "watch_response": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
# import json
# import base64
# import os
# from .gmail_service import process_new_email
# from .schemas import PubSubMessage
# from .workers.ai_worker import process_email_with_ai

# router = APIRouter()

# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     try:
#         body = await request.json()
#         message = body.get("message", {})
#         message_data = message.get("data")

#         if not message_data:
#             raise HTTPException(status_code=400, detail="Missing 'data' field in Pub/Sub message")

#         decoded_bytes = base64.b64decode(message_data)
#         decoded_str = decoded_bytes.decode("utf-8").strip()

#         if not decoded_str:
#             raise HTTPException(status_code=400, detail="Decoded data is empty")

#         notification = json.loads(decoded_str)
#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             raise HTTPException(status_code=400, detail="Missing emailAddress or historyId in notification")

#         background_tasks.add_task(process_email_notification, email_address, history_id)
#         return {"status": "success", "message": "Notification processed"}

#     except Exception as e:
#         raw_body = await request.body()
#         print(f"Webhook internal error: {e}\nRaw request body: {raw_body}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# async def process_email_notification(email_address: str, history_id: str):
#     try:
#         new_emails = await process_new_email(email_address, history_id)
#         for email in new_emails:
#             if should_process_email(email):
#                 process_email_with_ai.delay(email_address, email["id"])
#     except Exception as e:
#         print(f"Error processing email notification: {e}")

# def should_process_email(email):
#     return "INBOX" in email.get("labelIds", []) and "UNREAD" in email.get("labelIds", [])

# @router.post("/setup-watch")
# async def setup_gmail_watch_route(user_email: str):
#     try:
#         from .gmail_service import setup_gmail_watch
#         result = await setup_gmail_watch(user_email)
#         return {"status": "success", "watch_response": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Response
import json
import base64
import os
from .gmail_service import process_new_email
from .schemas import PubSubMessage
from datetime import datetime, timezone
from supabase import create_client
from pydantic import BaseModel
import asyncio


router = APIRouter()

# Pub/Sub configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "mock_project_id")
SUBSCRIPTION_NAME = os.getenv("GOOGLE_PUBSUB_SUBSCRIPTION", "gmail-notifications")


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def datetime_from_millis(millis: int):
    return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc).isoformat()
class WatchRequest(BaseModel):
    user_email: str
@router.post("/setup-watch")
async def setup_gmail_watch_route(watch_request: WatchRequest):
    user_email = watch_request.user_email 
    try:
        from .gmail_service import setup_gmail_watch
        result = await setup_gmail_watch(user_email)

        # ✅ Insert to Supabase
        if result.get("historyId"):
            supabase.table("gmail_watches").upsert({
                "user_email": user_email,
                "history_id": result.get("historyId"),
                "expiration": datetime_from_millis(int(result["expiration"])),
                  "watch_active": True  # ✅ Important!
            }, on_conflict=["user_email"]).execute()
            print(f"✅ Supabase inserted watch info for {user_email}")
        else:
            print("⚠️ No historyId in watch response.")

        return {"status": "success", "watch_response": result}

    except Exception as e:
        print(f"❌ Error setting up watch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-watch")
async def stop_gmail_watch_route(watch_request: WatchRequest):
    user_email = watch_request.user_email
    try:
        from .gmail_service import stop_gmail_watch

        await stop_gmail_watch(user_email)

        # ❌ Mark watch as inactive in Supabase
        supabase.table("gmail_watches").upsert({
            "user_email": user_email,
            "watch_active": False,  # You’ll need to add this column
        }, on_conflict=["user_email"]).execute()
        print(f"🔕 Watch deactivated in Supabase for {user_email}")

        return {"status": "success", "message": "Watch stopped"}

    except Exception as e:
        print(f"❌ Error stopping watch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        raw_body = await request.body()
        if not raw_body:
            print("⚠️ Webhook received empty body")
            return Response(status_code=200, content="OK", media_type="text/plain")

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return Response(status_code=200, content="OK", media_type="text/plain")

        print(f"📥 Webhook body: {body}")

        message = body.get("message", {})
        data_encoded = message.get("data")
        if not data_encoded:
            print("⚠️ 'data' missing")
            return Response(status_code=200, content="OK", media_type="text/plain")

        try:
            decoded_str = base64.b64decode(data_encoded).decode("utf-8")
            print(f"📨 Decoded data: {decoded_str!r}")
            notification = json.loads(decoded_str)
        except Exception as e:
            print(f"❌ Failed to decode or parse data: {e}")
            return Response(status_code=200, content="OK", media_type="text/plain")

        email_address = notification.get("emailAddress")
        history_id = notification.get("historyId")

        if not email_address or not history_id:
            print("⚠️ Missing fields in decoded payload")
            return Response(status_code=200, content="OK", media_type="text/plain")

        # 🔐 Check if user has active watch before processing
        watch_data = supabase.table("gmail_watches").select("*").eq("user_email", email_address).execute()
        watch_rows = watch_data.data
        print("🔎 Watch rows from Supabase:", watch_rows)
        if  not watch_rows or not watch_rows[0].get("watch_active", True):
            print(f"🔕 Watch is off for {email_address}, skipping processing.")
            return Response(status_code=200, content="OK", media_type="text/plain")

            

        # ✅ Schedule background task safely
        # background_tasks.add_task(lambda: asyncio.create_task(process_new_email(email_address, history_id)))
        background_tasks.add_task(process_email_notification, email_address, history_id)
        return Response(status_code=200, content="OK", media_type="text/plain")

    except Exception as e:
        print(f"❌ Unexpected webhook error: {e}")
        return Response(status_code=200, content="OK", media_type="text/plain")





# @router.api_route("/webhook", methods=["POST", "GET"])

# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     """Handle Gmail Pub/Sub notifications"""
#     try:
#         raw_body = await request.body()
#         if not raw_body:
#             print("⚠️ Webhook received empty body")
#             raise HTTPException(status_code=400, detail="Empty request body")

#         try:
#             body = await request.json()
#         except Exception as e:
#             print(f"❌ Failed to parse JSON: {e}")
#             raise HTTPException(status_code=400, detail="Invalid JSON payload")

#         message = body.get("message", {})
#         message_data = message.get("data")

#         if not message_data:
#             raise HTTPException(status_code=400, detail="Missing 'data' field in Pub/Sub message")

#         # Attempt to decode and parse
#         try:
#             decoded_bytes = base64.b64decode(message_data)
#             decoded_str = decoded_bytes.decode("utf-8").strip()

#             if not decoded_str:
#                 raise HTTPException(status_code=400, detail="Decoded data is empty")

#             notification = json.loads(decoded_str)
#         except (ValueError, json.JSONDecodeError) as decode_error:
#             print(f"Decoding error: {decode_error}\nDecoded string: {decoded_str}")
#             raise HTTPException(status_code=400, detail=f"Invalid Pub/Sub message data: {decode_error}")

#         # Extract email address and history ID
#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             raise HTTPException(status_code=400, detail="Missing required fields in notification")

#         # Process in background
#         background_tasks.add_task(
#             process_email_notification,
#             email_address,
#             history_id
#         )

#         return {"status": "success", "message": "Notification processed"}

#     except HTTPException as http_err:
#         raise http_err
#     except Exception as e:
#         print(f"Webhook internal error: {e}\nRaw request body: {raw_body}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
# import base64
# import json
# from .gmail_service import process_new_email

# router = APIRouter()

# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     try:
#         # Read the body once
#         raw_body = await request.body()
#         if not raw_body:
#             print("⚠️ Webhook received empty body")
#             raise HTTPException(status_code=400, detail="Empty request body")

#         body = json.loads(raw_body)
#         print(f"📥 Raw webhook body: {body}")

#         message = body.get("message", {})
#         data_encoded = message.get("data")
#         if not data_encoded:
#             raise HTTPException(status_code=400, detail="Missing 'data' field")

#         decoded_bytes = base64.b64decode(data_encoded)
#         decoded_str = decoded_bytes.decode("utf-8")
#         print(f"📨 Decoded Pub/Sub payload: {decoded_str}")

#         notification = json.loads(decoded_str)
#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             raise HTTPException(status_code=400, detail="Missing required fields")

#         background_tasks.add_task(process_new_email, email_address, history_id)

#         return {"status": "ok", "message": "Notification received"}

#     except Exception as e:
#         print(f"❌ Webhook error: {e}")
#         raise HTTPException(status_code=400, detail=str(e))



# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     try:
#         raw_body = await request.body()
#         if not raw_body:
#             print("⚠️ Webhook received empty body")
#             return Response(status_code=200, content="")

#         try:
#             body = json.loads(raw_body)
#         except json.JSONDecodeError as e:
#             print(f"❌ Invalid JSON: {e}")
#             return Response(status_code=200, content="")

#         print(f"📥 Webhook body: {body}")

#         message = body.get("message", {})
#         data_encoded = message.get("data")
#         if not data_encoded:
#             print("⚠️ 'data' missing")
#             return Response(status_code=200, content="")

#         try:
#             decoded_str = base64.b64decode(data_encoded).decode("utf-8")
#             print(f"📨 Decoded data: {decoded_str!r}")
#             notification = json.loads(decoded_str)
#         except Exception as e:
#             print(f"❌ Failed to decode or parse data: {e}")
#             return Response(status_code=200, content="")

#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             print("⚠️ Missing fields in decoded payload")
#             return Response(status_code=200, content="")

#         background_tasks.add_task(process_new_email, email_address, history_id)
#         return Response(status_code=200, content="")

#     except Exception as e:
#         print(f"❌ Unexpected webhook error: {e}")
#         return Response(status_code=200, content="")



# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     try:
#         # Read the raw body
#         raw_body = await request.body()
#         if not raw_body:
#             print("⚠️ Webhook received empty body")
#             return Response(status_code=204)  # Let Pub/Sub know it's fine

#         try:
#             body = json.loads(raw_body)
#         except json.JSONDecodeError:
#             print("❌ Invalid JSON received")
#             return Response(status_code=204)

#         print(f"📥 Raw webhook body: {body}")

#         # Return early if 'message' is missing (not a real notification)
#         if "message" not in body:
#             print("ℹ️ No 'message' field in body — probably a test ping from Pub/Sub")
#             return Response(status_code=204)

#         message = body["message"]
#         data_encoded = message.get("data")
#         if not data_encoded:
#             print("⚠️ 'data' field missing in message")
#             return Response(status_code=204)

#         # Decode and parse actual email notification
#         decoded_bytes = base64.b64decode(data_encoded)
#         decoded_str = decoded_bytes.decode("utf-8")
#         print(f"📨 Decoded Pub/Sub payload: {decoded_str}")

#         notification = json.loads(decoded_str)
#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             print("⚠️ Missing emailAddress or historyId")
#             return Response(status_code=204)

#         # Add to background tasks
#         background_tasks.add_task(process_new_email, email_address, history_id)

#         # return {"status": "ok", "message": "Notification received"}
#         return Response(status_code=200, content="")
#     except Exception as e:
#         print(f"❌ Webhook error: {e}")
#         raise HTTPException(status_code=400, detail="Webhook processing failed")

# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     try:
#         raw_body = await request.body()
#         if not raw_body:
#             return Response(status_code=204)

#         body = json.loads(raw_body)
#         if "message" not in body:
#             return Response(status_code=204)

#         message = body["message"]
#         data_encoded = message.get("data")
#         if not data_encoded:
#             return Response(status_code=204)

#         decoded_bytes = base64.b64decode(data_encoded)
#         decoded_str = decoded_bytes.decode("utf-8")
#         notification = json.loads(decoded_str)
#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             return Response(status_code=204)

#         # Add background task *after* sending response
#         background_tasks.add_task(process_new_email, email_address, history_id)

#         # Return 200 OK with empty body immediately
#         return Response(status_code=200, content="", media_type="text/plain")

#     except Exception as e:
#         print(f"Webhook error: {e}")
#         raise HTTPException(status_code=400, detail="Webhook processing failed")






# @router.post("/webhook")
# async def pubsub_webhook(request: Request, background_tasks: BackgroundTasks):
#     try:
#         raw_body = await request.body()
#         if not raw_body:
#             return Response(status_code=204)

#         body = json.loads(raw_body)
#         message = body.get("message")
#         if not message:
#             return Response(status_code=204)

#         data_encoded = message.get("data")
#         if not data_encoded:
#             return Response(status_code=204)

#         try:
#             decoded_str = base64.b64decode(data_encoded).decode("utf-8")
#             notification = json.loads(decoded_str)
#         except Exception as decode_error:
#             print("❌ Failed to decode Pub/Sub message:", decode_error)
#             return Response(status_code=204)

#         # 🔍 Skip Google's test messages like {"event": "GMM_Event"}
#         if notification.get("event") == "GMM_Event":
#             print("⚠️ Skipping test notification from Google Pub/Sub")
#             return Response(status_code=200)

#         email_address = notification.get("emailAddress")
#         history_id = notification.get("historyId")

#         if not email_address or not history_id:
#             print("⚠️ Missing email or history_id — skipping")
#             return Response(status_code=204)

#         # ✅ Add background task to process real Gmail event
#         background_tasks.add_task(process_new_email, email_address, history_id)

#         print(f"📥 New email event for: {email_address}, historyId: {history_id}")

#         return Response(status_code=200, content="", media_type="text/plain")

#     except Exception as e:
#         print(f"❌ Webhook error: {e}")
#         raise HTTPException(status_code=400, detail="Webhook processing failed")





async def process_email_notification(email_address: str, history_id: str):
    """Process Gmail notification and trigger AI response if needed"""
    try:
        new_emails = await process_new_email(email_address, history_id)
        for email in new_emails:
            if should_process_email(email):
                from backend.workers.ai_worker import process_email_with_ai
                process_email_with_ai.delay(email_address, email["id"])
    except Exception as e:
        print(f"Error processing email notification: {e}")

def should_process_email(email):
    """Determine if email should be processed by AI"""
    return "INBOX" in email.get("labelIds", []) and "UNREAD" in email.get("labelIds", [])

# @router.post("/setup-watch")
# async def setup_gmail_watch(user_email: str):
#     try:
#         from .gmail_service import setup_gmail_watch
#         result = await setup_gmail_watch(user_email)
#         return {"status": "success", "watch_response": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


