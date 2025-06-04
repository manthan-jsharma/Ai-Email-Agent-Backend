from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from .db import get_user_credentials, save_email_data
from .schemas import EmailData, SendEmailRequest
from google.auth.transport.requests import Request
import re
from supabase import create_client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/userinfo.profile"
]

router = APIRouter()
@router.get("/inbox/{user_email}")
async def get_user_inbox(user_email: str, max_results: int = 50):
    """Get inbox emails for a user and save them to Supabase"""
    try:
        service = await get_gmail_service(user_email)

        # Get email list
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q='in:inbox'
        ).execute()

        messages = results.get('messages', [])
        emails = []

        for message in messages:
            email_data = service.users().messages().get(
                userId='me',
                id=message['id']
            ).execute()

            parsed = parse_email_data(email_data)
            emails.append(parsed)

            # ✅ Save to Supabase
            await save_email_data(user_email, parsed)

        return {"emails": emails}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_email(send_request: SendEmailRequest):
    """Send an email"""
    try:
        service = await get_gmail_service(send_request.user_email)
        
        # Create message
        message = create_message(
            to=send_request.to,
            subject=send_request.subject,
            body=send_request.body,
            thread_id=send_request.thread_id
        )
        
        # Send message
        result = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        return {"message_id": result['id'], "status": "sent"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# async def get_gmail_service(user_email: str):
    """Get authenticated Gmail service"""
    credentials_dict = await get_user_credentials(user_email)
    if not credentials_dict:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    credentials = Credentials.from_authorized_user_info(credentials_dict, scopes=SCOPES)
    if not credentials.valid and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    service = build('gmail', 'v1', credentials=credentials)
    return service

async def get_gmail_service(user_email: str):
    user_data = await get_user_credentials(user_email)
    if not user_data:
        raise HTTPException(status_code=401, detail="User not authenticated")

    print("🔍 Raw credentials_dict from Supabase:\n", user_data)

    credentials_dict = user_data.get("credentials", {})  # 👈 extract nested

    required_keys = ["refresh_token", "client_id", "client_secret", "token_uri"]
    missing_keys = [key for key in required_keys if not credentials_dict.get(key)]

    if missing_keys:
        print("❌ Missing keys in credentials_dict:", missing_keys)
        raise HTTPException(status_code=500, detail=f"Missing required fields: {missing_keys}")

    credentials = Credentials(
        token=credentials_dict["token"],
        refresh_token=credentials_dict["refresh_token"],
        token_uri=credentials_dict["token_uri"],
        client_id=credentials_dict["client_id"],
        client_secret=credentials_dict["client_secret"],
        scopes=SCOPES
    )

    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                print("❌ Failed to refresh token:", e)
                raise HTTPException(status_code=401, detail="Token refresh failed")
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired credentials")

    service = build('gmail', 'v1', credentials=credentials)
    return service



# async def process_new_email(user_email: str, history_id: str):
#     """Process new emails from Gmail"""
#     try:
#         service = await get_gmail_service(user_email)
        
#         # Get history
#         history = service.users().history().list(
#             userId='me',
#             startHistoryId=history_id
#         ).execute()
        
#         new_emails = []
#         for change in history.get('history', []):
#             if 'messagesAdded' in change:
#                 for message_added in change['messagesAdded']:
#                     message_id = message_added['message']['id']
                    
#                     # Get full message
#                     email_data = service.users().messages().get(
#                         userId='me',
#                         id=message_id
#                     ).execute()
                    
#                     parsed_email = parse_email_data(email_data)
#                     new_emails.append(parsed_email)
                    
#                     # Save to Supabase
#                     await save_email_data(user_email, parsed_email)
        
#         return new_emails
        
#     except Exception as e:
#         print(f"Error processing new emails: {e}")
#         return []


async def process_new_email(user_email: str, history_id: str):
    """Process new emails from Gmail"""
    try:
        service = await get_gmail_service(user_email)
 
        # Fetch previous history_id
        resp = supabase.table("gmail_watches").select("history_id").eq("user_email", user_email).execute()
        if not resp.data:
            print("⚠️ No previous historyId found for", user_email)
            return []

        saved_history_id = resp.data[0]["history_id"]

        # Get history from the saved checkpoint
        history = service.users().history().list(
            userId='me',
            startHistoryId=saved_history_id,
            historyTypes=['messageAdded']
        ).execute()

        new_emails = []
        for change in history.get('history', []):
            if 'messagesAdded' in change:
                for message_added in change['messagesAdded']:
                    message_id = message_added['message']['id']

                    # Get full message
                    email_data = service.users().messages().get(
                        userId='me',
                        id=message_id
                    ).execute()

                    parsed_email = parse_email_data(email_data)
                    new_emails.append(parsed_email)

                    # Save to Supabase
                    await save_email_data(user_email, parsed_email)

        # Update history_id in Supabase
        supabase.table("gmail_watches").update({
            "history_id": history_id
        }).eq("user_email", user_email).execute()

        return new_emails

    except Exception as e:
        print(f"❌ Error processing new emails: {e}")
        return []


async def setup_gmail_watch(user_email: str):
    """Set up Gmail watch for push notifications"""
    try:
        service = await get_gmail_service(user_email)
        
        request_body = {
            'labelIds': ['INBOX'],
            'topicName': f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'mock_project')}/topics/{os.getenv('GOOGLE_PUBSUB_TOPIC', 'gmail-notifications')}"
        }
        
        result = service.users().watch(userId='me', body=request_body).execute()
        return result
        
    except Exception as e:
        raise Exception(f"Failed to setup Gmail watch: {e}")


async def stop_gmail_watch(user_email: str):
    """Stop Gmail push notifications (unsubscribe watch)"""
    try:
        service = await get_gmail_service(user_email)

        service.users().stop(userId='me').execute()
        print(f"⛔ Watch stopped for {user_email}")
        return True

    except Exception as e:
        raise Exception(f"Failed to stop Gmail watch: {e}")


def parse_email_data(email_data):
    """Parse Gmail API email data"""
    headers = email_data['payload'].get('headers', [])
    
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
    recipient = next((h['value'] for h in headers if h['name'] == 'To'), '')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
    
    # Get email body
    body = extract_email_body(email_data['payload'])
    
    return {
        'id': email_data['id'],
        'thread_id': email_data['threadId'],
        'subject': subject,
        'sender': sender,
        'recipient': recipient,
        'date': date,
        'body': body,
        'labelIds': email_data.get('labelIds', [])
    }
def clean_text(text: str) -> str:
    """Remove URLs and extra whitespace from preview text"""
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\s+', ' ', text)     # Collapse whitespace
    return text.strip()

def extract_email_body(payload):
    """Extract email body from payload"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                break
    elif payload['mimeType'] == 'text/plain':
        data = payload['body']['data']
        body = base64.urlsafe_b64decode(data).decode('utf-8')
    
    return body

def create_message(to, subject, body, thread_id=None):
    """Create email message"""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    email_message = {'raw': raw_message}
    if thread_id:
        email_message['threadId'] = thread_id
    
    return email_message

async def send_email_reply(user_email: str, thread_id: str, response_content: str, original_email_id: str):
    """Send AI-generated email reply"""
    try:
        service = await get_gmail_service(user_email)
        
        # Get original email for context
        original_email = service.users().messages().get(
            userId='me',
            id=original_email_id
        ).execute()
        
        headers = original_email['payload'].get('headers', [])
        original_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        original_sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        
        # Create reply
        reply_subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
        
        message = create_message(
            to=original_sender,
            subject=reply_subject,
            body=response_content,
            thread_id=thread_id
        )
        
        result = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to send email reply: {e}")

async def create_gmail_draft(user_email: str, thread_id: str, response_content: str, original_email_id: str):
    """Create a draft in Gmail with AI-generated response"""
    try:
        service = await get_gmail_service(user_email)
        
        # Get original email for context
        original_email = service.users().messages().get(
            userId='me',
            id=original_email_id
        ).execute()
        
        headers = original_email['payload'].get('headers', [])
        original_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        original_sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        
        # Create reply
        reply_subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
        
        message = create_message(
            to=original_sender,
            subject=reply_subject,
            body=response_content,
            thread_id=thread_id
        )
        
        # Create draft
        draft = {'message': message}
        result = service.users().drafts().create(
            userId='me',
            body=draft
        ).execute()
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to create Gmail draft: {e}")
