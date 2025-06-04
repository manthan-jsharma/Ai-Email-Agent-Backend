# #!/usr/bin/env python3
# """
# Script to set up Gmail watch notifications for all authenticated users.
# This script should be run after deploying the application to register
# Gmail push notifications with Google Pub/Sub.
# """

# import asyncio
# import os
# import sys
# from pathlib import Path

# # Add the backend directory to the Python path
# backend_dir = Path(__file__).parent.parent / "backend"
# sys.path.insert(0, str(backend_dir))

# from app.db import get_db_connection
# from app.gmail_service import setup_gmail_watch

# async def setup_watches_for_all_users():
#     """Set up Gmail watch for all authenticated users"""
#     conn = await get_db_connection()
    
#     try:
#         # Get all users with credentials
#         users = await conn.fetch("""
#             SELECT user_email FROM user_credentials
#         """)
        
#         print(f"Found {len(users)} authenticated users")
        
#         for user in users:
#             user_email = user['user_email']
#             print(f"Setting up Gmail watch for {user_email}...")
            
#             try:
#                 result = await setup_gmail_watch(user_email)
#                 print(f"✓ Successfully set up watch for {user_email}")
#                 print(f"  History ID: {result.get('historyId')}")
#                 print(f"  Expiration: {result.get('expiration')}")
                
#                 # Save watch info to database
#                 await conn.execute("""
#                     INSERT INTO gmail_watches (user_email, history_id, expiration)
#                     VALUES ($1, $2, to_timestamp($3::bigint / 1000))
#                     ON CONFLICT (user_email) 
#                     DO UPDATE SET 
#                         history_id = $2,
#                         expiration = to_timestamp($3::bigint / 1000),
#                         created_at = NOW()
#                 """, user_email, result.get('historyId'), int(result.get('expiration', 0)))
                
#             except Exception as e:
#                 print(f"✗ Failed to set up watch for {user_email}: {e}")
        
#     finally:
#         await conn.close()

# async def check_pubsub_setup():
#     """Check if Pub/Sub topic and subscription are properly configured"""
#     try:
#         from google.cloud import pubsub_v1
        
#         project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
#         topic_name = os.getenv("GOOGLE_PUBSUB_TOPIC")
#         subscription_name = os.getenv("GOOGLE_PUBSUB_SUBSCRIPTION")
        
#         if not all([project_id, topic_name, subscription_name]):
#             print("✗ Missing Pub/Sub environment variables")
#             return False
        
#         publisher = pubsub_v1.PublisherClient()
#         subscriber = pubsub_v1.SubscriberClient()
        
#         topic_path = publisher.topic_path(project_id, topic_name)
#         subscription_path = subscriber.subscription_path(project_id, subscription_name)
        
#         # Check if topic exists
#         try:
#             publisher.get_topic(request={"topic": topic_path})
#             print(f"✓ Pub/Sub topic '{topic_name}' exists")
#         except Exception as e:
#             print(f"✗ Pub/Sub topic '{topic_name}' not found: {e}")
#             return False
        
#         # Check if subscription exists
#         try:
#             subscriber.get_subscription(request={"subscription": subscription_path})
#             print(f"✓ Pub/Sub subscription '{subscription_name}' exists")
#         except Exception as e:
#             print(f"✗ Pub/Sub subscription '{subscription_name}' not found: {e}")
#             return False
        
#         return True
        
#     except ImportError:
#         print("✗ Google Cloud Pub/Sub library not installed")
#         return False
#     except Exception as e:
#         print(f"✗ Error checking Pub/Sub setup: {e}")
#         return False

# async def main():
#     """Main function"""
#     print("AI Email Agent - Gmail Watch Setup")
#     print("=" * 40)
    
#     # Check environment variables
#     required_vars = [
#         "GOOGLE_CLIENT_ID",
#         "GOOGLE_CLIENT_SECRET", 
#         "GOOGLE_CLOUD_PROJECT_ID",
#         "GOOGLE_PUBSUB_TOPIC",
#         "DATABASE_URL"
#     ]
    
#     missing_vars = [var for var in required_vars if not os.getenv(var)]
#     if missing_vars:
#         print(f"✗ Missing required environment variables: {', '.join(missing_vars)}")
#         return
    
#     print("✓ All required environment variables are set")
    
#     # Check Pub/Sub setup
#     print("\nChecking Pub/Sub configuration...")
#     if not await check_pubsub_setup():
#         print("Please set up Pub/Sub topic and subscription first")
#         return
    
#     # Set up Gmail watches
#     print("\nSetting up Gmail watches...")
#     await setup_watches_for_all_users()
    
#     print("\n✓ Gmail watch setup completed!")
#     print("\nNext steps:")
#     print("1. Ensure your webhook endpoint is publicly accessible")
#     print("2. Test by sending an email to a watched account")
#     print("3. Check the logs for incoming Pub/Sub notifications")

# if __name__ == "__main__":
#     asyncio.run(main())

# !/usr/bin/env python3

import asyncio
import os
from supabase import create_client, Client
from backend.app.gmail_service import setup_gmail_watch



SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mock-supabase-url.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "mock_supabase_key")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase environment variables.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def setup_watches_for_all_users():
    response = supabase.table("user_credentials").select("user_email").execute()
    users = response.data or []

    print(f"Found {len(users)} authenticated users")

    for user in users:
        user_email = user["user_email"]
        print(f"Setting up Gmail watch for {user_email}...")

        try:
            result = await setup_gmail_watch(user_email)
            print(f"✓ Watch setup for {user_email}")
            print(f"  History ID: {result.get('historyId')}")
            print(f"  Expiration: {result.get('expiration')}")

            # Store in Supabase
            supabase.table("gmail_watches").upsert({
                "user_email": user_email,
                "history_id": result.get("historyId"),
               "expiration": result.get("expiration") and datetime_from_millis(int(result["expiration"]))
            }, on_conflict=["user_email"]).execute()

        except Exception as e:
            print(f"✗ Failed for {user_email}: {e}")

def datetime_from_millis(millis: int):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc).isoformat()

async def main():
    print("AI Email Agent - Gmail Watch Setup")
    await setup_watches_for_all_users()

if __name__ == "__main__":
    asyncio.run(main())
