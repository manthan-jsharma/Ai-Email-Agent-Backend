
# import json
# import os
# from datetime import datetime
# from typing import Optional, List, Dict
# from supabase import create_client, Client
# from dotenv import load_dotenv
# # Database configuration
# load_dotenv()
# # Supabase configuration
# SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mock-supabase-url.supabase.co")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY", "mock_supabase_key")

# supabase: Client = None

# def init_supabase():
#     """Initialize Supabase client"""
#     global supabase
#     supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
#     return supabase

# def get_supabase():
#     """Get Supabase client"""
#     global supabase
#     if not supabase:
#         supabase = init_supabase()
#     return supabase





# async def save_user_credentials(user_id: str, credentials: dict):
#     """Save user OAuth credentials to Supabase"""
#     client = get_supabase()
    
#     # Check if user exists
#     response = client.table('user_credentials').select('*').eq('user_email', user_id).execute()
    
#     if len(response.data) > 0:
#         # Update existing user
#         client.table('user_credentials').update({
#             'credentials': json.dumps(credentials),
#             'updated_at': datetime.now().isoformat()
#         }).eq('user_email', user_id).execute()
#     else:
#         # Insert new user
#         client.table('user_credentials').insert({
#             'user_email': user_id,
#             'credentials': json.dumps(credentials),
#             'created_at': datetime.now().isoformat(),
#             'updated_at': datetime.now().isoformat()
#         }).execute()
        
#         # Create default settings for new user
#         client.table('user_settings').insert({
#             'user_email': user_id,
#             'auto_draft': False,
#             'auto_send': False,
#             'created_at': datetime.now().isoformat(),
#             'updated_at': datetime.now().isoformat()
#         }).execute()

# async def get_user_credentials(user_email: str) -> Optional[dict]:
#     """Get user OAuth credentials from Supabase"""
#     client = get_supabase()
#     response = client.table('user_credentials').select('credentials').eq('user_email', user_email).execute()
    
#     if len(response.data) > 0:
#         return json.loads(response.data[0]['credentials'])
#     return None

# async def save_email_data(user_email: str, email_data: dict):
#     """Save email data to Supabase"""
#     client = get_supabase()
    
#     # Check if email exists
#     response = client.table('emails').select('id').eq('id', email_data['id']).execute()
    
#     if len(response.data) == 0:
#         # Insert new email
#         client.table('emails').insert({
#             'id': email_data['id'],
#             'user_email': user_email,
#             'thread_id': email_data['thread_id'],
#             'subject': email_data['subject'],
#             'sender': email_data['sender'],
#             'recipient': email_data.get('recipient', ''),
#             'body': email_data['body'],
#             'date_received': datetime.now().isoformat(),
#             'label_ids': email_data['labelIds'],
#             'created_at': datetime.now().isoformat()
#         }).execute()

# async def save_ai_response(user_email: str, original_email_id: str, ai_response: str, thread_id: str) -> str:
#     """Save AI response to Supabase"""
#     client = get_supabase()
    
#     response = client.table('ai_responses').insert({
#         'user_email': user_email,
#         'original_email_id': original_email_id,
#         'thread_id': thread_id,
#         'ai_response': ai_response,
#         'status': 'generated',
#         'created_at': datetime.now().isoformat()
#     }).execute()
    
#     if len(response.data) > 0:
#         return response.data[0]['id']
#     raise Exception("Failed to save AI response")

# async def get_ai_response(response_id: str) -> Optional[dict]:
#     """Get AI response by ID from Supabase"""
#     client = get_supabase()
#     response = client.table('ai_responses').select('*').eq('id', response_id).execute()
    
#     if len(response.data) > 0:
#         return response.data[0]
#     return None

# async def update_ai_response_status(response_id: str, status: str):
#     """Update AI response status in Supabase"""
#     client = get_supabase()
    
#     update_data = {
#         'status': status,
#     }
    
#     if status == 'sent':
#         update_data['sent_at'] = datetime.now().isoformat()
    
#     client.table('ai_responses').update(update_data).eq('id', response_id).execute()

# async def update_ai_response_draft_id(response_id: str, draft_id: str):
#     """Update AI response draft ID in Supabase"""
#     client = get_supabase()
    
#     client.table('ai_responses').update({
#         'draft_id': draft_id
#     }).eq('id', response_id).execute()

# async def get_user_ai_responses(user_email: str, limit: int = 50) -> List[dict]:
#     """Get AI responses for a user from Supabase"""
#     client = get_supabase()
    
#     # Get AI responses with email details
#     response = client.table('ai_responses').select(
#         'id, original_email_id, thread_id, ai_response, status, created_at, sent_at, draft_id'
#     ).eq('user_email', user_email).order('created_at', desc=True).limit(limit).execute()
    
#     responses = response.data
    
#     # Get email details for each response
#     for resp in responses:
#         email_response = client.table('emails').select(
#             'subject, sender'
#         ).eq('id', resp['original_email_id']).execute()
        
#         if len(email_response.data) > 0:
#             resp['subject'] = email_response.data[0]['subject']
#             resp['sender'] = email_response.data[0]['sender']
#         else:
#             resp['subject'] = '(No Subject)'
#             resp['sender'] = '(Unknown Sender)'
    
#     return responses

# async def get_email_thread(thread_id: str) -> List[dict]:
#     """Get email thread for context from Supabase"""
#     client = get_supabase()
    
#     response = client.table('emails').select(
#         'subject, sender, body, date_received'
#     ).eq('thread_id', thread_id).order('date_received', desc=False).execute()
    
#     return [{'content': f"From: {row['sender']}\nSubject: {row['subject']}\n{row['body']}"} for row in response.data]

# async def get_user_emails(user_email: str, limit: int = 50) -> List[dict]:
#     """Get emails for a user from Supabase"""
#     client = get_supabase()
    
#     response = client.table('emails').select('*').eq('user_email', user_email).order('date_received', desc=True).limit(limit).execute()
    
#     return response.data

# async def get_user_automation_settings(user_email: str) -> dict:
#     """Get user automation settings from Supabase"""
#     client = get_supabase()
    
#     response = client.table('user_settings').select('auto_draft, auto_send').eq('user_email', user_email).execute()
    
#     if len(response.data) > 0:
#         return response.data[0]
    
#     # Create default settings if not exist
#     default_settings = {
#         'auto_draft': False,
#         'auto_send': False
#     }
    
#     client.table('user_settings').insert({
#         'user_email': user_email,
#         **default_settings,
#         'created_at': datetime.now().isoformat(),
#         'updated_at': datetime.now().isoformat()
#     }).execute()
    
#     return default_settings

# async def update_user_automation_settings(user_email: str, auto_draft: bool, auto_send: bool):
#     """Update user automation settings in Supabase"""
#     client = get_supabase()
    
#     response = client.table('user_settings').select('user_email').eq('user_email', user_email).execute()
    
#     if len(response.data) > 0:
#         # Update existing settings
#         client.table('user_settings').update({
#             'auto_draft': auto_draft,
#             'auto_send': auto_send,
#             'updated_at': datetime.now().isoformat()
#         }).eq('user_email', user_email).execute()
#     else:
#         # Create new settings
#         client.table('user_settings').insert({
#             'user_email': user_email,
#             'auto_draft': auto_draft,
#             'auto_send': auto_send,
#             'created_at': datetime.now().isoformat(),
#             'updated_at': datetime.now().isoformat()
#         }).execute()

import asyncpg
import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mock-supabase-url.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "mock_supabase_key")

supabase: Client = None

def init_supabase():
    """Initialize Supabase client"""
    global supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def get_supabase():
    """Get Supabase client"""
    global supabase
    if not supabase:
        supabase = init_supabase()
    return supabase



async def save_user_credentials(user_id: str, credentials: dict, name: str = None):
    """Save user OAuth credentials to Supabase"""
    client = get_supabase()
    
    # Check if user exists
    response = client.table('user_credentials').select('*').eq('user_email', user_id).execute()
    
    if len(response.data) > 0:
        # Update existing user
        update_data = {
            'credentials': credentials,
            'updated_at': datetime.now().isoformat()
        }
        
        if name:
            update_data['display_name'] = name
            
        client.table('user_credentials').update(update_data).eq('user_email', user_id).execute()
    else:
        # Insert new user
        insert_data = {
            'user_email': user_id,
            'credentials': credentials,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if name:
            insert_data['display_name'] = name
            
        client.table('user_credentials').insert(insert_data).execute()
        
        # Create default settings for new user
        client.table('user_settings').insert({
            'user_email': user_id,
            'auto_draft': False,
            'auto_send': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }).execute()

async def get_user_credentials(user_email: str) -> Optional[dict]:
    """Get user OAuth credentials from Supabase"""
    client = get_supabase()
    response = client.table('user_credentials').select('credentials, display_name').eq('user_email', user_email).execute()
    
    if len(response.data) > 0:
        return {
            'credentials':  response.data[0]['credentials'], 
            'name': response.data[0].get('display_name')
        }
    return None

async def save_email_data(user_email: str, email_data: dict):
    """Save email data to Supabase"""
    client = get_supabase()
    
    # Check if email exists
    response = client.table('emails').select('id').eq('id', email_data['id']).execute()
    
    if len(response.data) == 0:
        # Insert new email
        client.table('emails').insert({
            'id': email_data['id'],
            'user_email': user_email,
            'thread_id': email_data['thread_id'],
            'subject': email_data['subject'],
            'sender': email_data['sender'],
            'recipient': email_data.get('recipient', ''),
            'body': email_data['body'],
            'date_received': datetime.now().isoformat(),
            'label_ids': email_data['labelIds'],
            'created_at': datetime.now().isoformat()
        }).execute()

async def save_ai_response(user_email: str, original_email_id: str, ai_response: str, thread_id: str) -> str:
    """Save AI response to Supabase"""
    client = get_supabase()
    
    response = client.table('ai_responses').insert({
        'user_email': user_email,
        'original_email_id': original_email_id,
        'thread_id': thread_id,
        'ai_response': ai_response,
        'status': 'generated',
        'created_at': datetime.now().isoformat()
    }).execute()
    
    if len(response.data) > 0:
        return response.data[0]['id']
    raise Exception("Failed to save AI response")

async def get_ai_response(response_id: str) -> Optional[dict]:
    """Get AI response by ID from Supabase"""
    client = get_supabase()
    response = client.table('ai_responses').select('*').eq('id', response_id).execute()
    
    if len(response.data) > 0:
        return response.data[0]
    return None

async def update_ai_response_status(response_id: str, status: str):
    """Update AI response status in Supabase"""
    client = get_supabase()
    
    update_data = {
        'status': status,
    }
    
    if status == 'sent':
        update_data['sent_at'] = datetime.now().isoformat()
    
    client.table('ai_responses').update(update_data).eq('id', response_id).execute()

async def update_ai_response_draft_id(response_id: str, draft_id: str):
    """Update AI response draft ID in Supabase"""
    client = get_supabase()
    
    client.table('ai_responses').update({
        'draft_id': draft_id
    }).eq('id', response_id).execute()

async def get_user_ai_responses(user_email: str, limit: int = 50) -> List[dict]:
    """Get AI responses for a user from Supabase"""
    client = get_supabase()
    
    # Get AI responses with email details
    response = client.table('ai_responses').select(
        'id, original_email_id, thread_id, ai_response, status, created_at, sent_at, draft_id'
    ).eq('user_email', user_email).order('created_at', desc=True).limit(limit).execute()
    
    responses = response.data
    
    # Get email details for each response
    for resp in responses:
        email_response = client.table('emails').select(
            'subject, sender'
        ).eq('id', resp['original_email_id']).execute()
        
        if len(email_response.data) > 0:
            resp['subject'] = email_response.data[0]['subject']
            resp['sender'] = email_response.data[0]['sender']
        else:
            resp['subject'] = '(No Subject)'
            resp['sender'] = '(Unknown Sender)'
    
    return responses

async def get_email_thread(thread_id: str) -> List[dict]:
    """Get email thread for context from Supabase"""
    client = get_supabase()
    
    response = client.table('emails').select(
        'subject, sender, body, date_received'
    ).eq('thread_id', thread_id).order('date_received', desc=False).execute()
    
    return [{'content': f"From: {row['sender']}\nSubject: {row['subject']}\n{row['body']}"} for row in response.data]

async def get_user_emails(user_email: str, limit: int = 50) -> List[dict]:
    """Get emails for a user from Supabase"""
    client = get_supabase()
    
    response = client.table('emails').select('*').eq('user_email', user_email).order('date_received', desc=True).limit(limit).execute()
    
    return response.data

async def get_user_automation_settings(user_email: str) -> dict:
    """Get user automation settings from Supabase"""
    client = get_supabase()
    
    response = client.table('user_settings').select('auto_draft, auto_send').eq('user_email', user_email).execute()
    
    if len(response.data) > 0:
        return response.data[0]
    
    # Create default settings if not exist
    default_settings = {
        'auto_draft': False,
        'auto_send': False
    }
    
    client.table('user_settings').insert({
        'user_email': user_email,
        **default_settings,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }).execute()
    
    return default_settings

async def update_user_automation_settings(user_email: str, auto_draft: bool, auto_send: bool):
    """Update user automation settings in Supabase"""
    client = get_supabase()
    
    response = client.table('user_settings').select('user_email').eq('user_email', user_email).execute()
    
    if len(response.data) > 0:
        # Update existing settings
        client.table('user_settings').update({
            'auto_draft': auto_draft,
            'auto_send': auto_send,
            'updated_at': datetime.now().isoformat()
        }).eq('user_email', user_email).execute()
    else:
        # Create new settings
        client.table('user_settings').insert({
            'user_email': user_email,
            'auto_draft': auto_draft,
            'auto_send': auto_send,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }).execute()
