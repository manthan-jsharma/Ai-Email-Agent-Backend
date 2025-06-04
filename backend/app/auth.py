# from fastapi import APIRouter, HTTPException, Depends, Request as FastAPIRequest
# from google.auth.transport.requests import Request as GoogleAuthRequest
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# import os
# import json
# from .schemas import AuthResponse, TokenRequest
# from .db import save_user_credentials, get_user_credentials

# router = APIRouter()

# # OAuth 2.0 configuration
# SCOPES = [
#     'https://www.googleapis.com/auth/gmail.readonly',
#     'https://www.googleapis.com/auth/gmail.send',
#     'https://www.googleapis.com/auth/gmail.modify',
#     'https://www.googleapis.com/auth/gmail.compose'  # Added for draft creation
# ]

# CLIENT_CONFIG = {
#     "web": {
#         "client_id": os.getenv("GOOGLE_CLIENT_ID", "mock_client_id"),
#         "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", "mock_client_secret"),
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/token",
#         "redirect_uris": ["http://localhost:8000/auth/callback"]
#     }
# }

# @router.get("/login")
# async def login():
#     """Initiate OAuth flow"""
#     flow = Flow.from_client_config(
#         CLIENT_CONFIG,
#         scopes=SCOPES,
#         redirect_uri="http://localhost:8000/auth/callback"
#     )
    
#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true'
#     )
    
#     return {"authorization_url": authorization_url, "state": state}

# @router.get("/callback")
# async def auth_callback(code: str, state: str):
#     """Handle OAuth callback"""
#     try:
#         flow = Flow.from_client_config(
#             CLIENT_CONFIG,
#             scopes=SCOPES,
#             redirect_uri="http://localhost:8000/auth/callback"
#         )
        
#         flow.fetch_token(code=code)
#         credentials = flow.credentials
        
#         # Get user info
#         service = build('gmail', 'v1', credentials=credentials)
#         profile = service.users().getProfile(userId='me').execute()
        
#         # Save credentials to Supabase
#         await save_user_credentials(
#             user_id=profile['emailAddress'],
#             credentials=credentials_to_dict(credentials)
#         )
        
#         return AuthResponse(
#             success=True,
#             user_email=profile['emailAddress'],
#             message="Authentication successful"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.post("/refresh")
# async def refresh_token(token_request: TokenRequest):
#     """Refresh access token"""
#     try:
#         credentials_dict = await get_user_credentials(token_request.user_email)
#         if not credentials_dict:
#             raise HTTPException(status_code=404, detail="User credentials not found")
        
#         credentials = Credentials.from_authorized_user_info(credentials_dict)
        
#         if credentials.expired and credentials.refresh_token:
#             credentials.refresh(GoogleAuthRequest())
            
#             # Update credentials in Supabase
#             await save_user_credentials(
#                 user_id=token_request.user_email,
#                 credentials=credentials_to_dict(credentials)
#             )
        
#         return {"access_token": credentials.token}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/status")
# async def auth_status(request: FastAPIRequest):
#     """Check authentication status"""
#     # This would typically check a session or token
#     # For now, we'll return a mock response
#     return {"isAuthenticated": False, "email": None}

# def credentials_to_dict(credentials):
#     """Convert credentials to dictionary"""
#     return {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }
from fastapi import APIRouter, HTTPException, Depends, Request as FastAPIRequest
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import json
from .schemas import AuthResponse, TokenRequest
from .db import save_user_credentials, get_user_credentials
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
# from app.gmail_service import setup_gmail_watch
import httpx
router = APIRouter()

# OAuth 2.0 configuration
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',  # Added for draft creation
    'https://www.googleapis.com/auth/userinfo.profile'  # Added for user profile info
]

CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", "mock_client_id"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", "mock_client_secret"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8000/auth/callback"]
    }
}
SECRET_KEY = os.getenv("JWT_SECRET", "dev_secret")
ALGORITHM = "HS256"

def create_jwt_token(email: str):
    expire = datetime.utcnow() + timedelta(days=1)
    payload = {
        "sub": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

@router.get("/login")
async def login():
    """Initiate OAuth flow"""
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/auth/callback"
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
          prompt='consent' 
        
    )
    
    return {"authorization_url": authorization_url, "state": state}

@router.get("/callback")
async def auth_callback(code: str, state: str):
    """Handle OAuth callback"""
    try:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri="http://localhost:8000/auth/callback"
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        
        # Get user profile info
        people_service = build('people', 'v1', credentials=credentials)
        profile_info = people_service.people().get(
            resourceName='people/me',
            personFields='names'
        ).execute()
        
        # Extract name from profile info
        name = None
        if 'names' in profile_info and profile_info['names']:
            name = profile_info['names'][0].get('displayName')
        
        # Save credentials to Supabase
        await save_user_credentials(
            user_id=profile['emailAddress'],
            credentials=credentials_to_dict(credentials),
            name=name
        )
        print("✅ Callback reached. Email:", profile['emailAddress'])
      

        # ✅ Trigger your own POST /setup-watch route (backend calling itself)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8000/pubsub/setup-watch",
                json={"user_email": profile['emailAddress']}
            )
            print("📡 Triggered /setup-watch, status:", resp.status_code)
            print("🛰️ Response from /setup-watch:", resp.json())

        token = create_jwt_token(profile['emailAddress'])
        
        # Redirect to frontend after successful authentication
        return  RedirectResponse(url=f"http://localhost:3000/dashboard?token={token}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/refresh")
async def refresh_token(token_request: TokenRequest):
    try:
        credentials_dict = await get_user_credentials(token_request.user_email)

        if not credentials_dict:
            raise HTTPException(status_code=404, detail="User credentials not found")

        # If it's nested or stringified, fix it
        if isinstance(credentials_dict, str):
            credentials_dict = json.loads(credentials_dict)
        elif isinstance(credentials_dict.get("credentials"), str):
            credentials_dict = json.loads(credentials_dict["credentials"])

        credentials = Credentials.from_authorized_user_info(info=credentials_dict["credentials"])

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(GoogleAuthRequest())

            await save_user_credentials(
                user_id=token_request.user_email,
                credentials=credentials_to_dict(credentials)
            )

        return {"access_token": credentials.token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def auth_status(request: FastAPIRequest):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {
            "isAuthenticated": False,
            "email": None,
            "name": None
        }

    token = auth_header.split(" ")[1]
    email = decode_jwt_token(token)
    if email is None:
        return {
            "isAuthenticated": False,
            "email": None,
            "name": None
        }

    credentials_dict = await get_user_credentials(email)
    name = credentials_dict.get("name") if credentials_dict else None

    return {
        "isAuthenticated": True,
        "email": email,
        "name": name
    }



def credentials_to_dict(credentials):
    """Convert credentials to dictionary"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
