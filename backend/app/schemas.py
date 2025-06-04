from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AuthResponse(BaseModel):
    success: bool
    user_email: str
    message: str

class TokenRequest(BaseModel):
    user_email: str

class EmailRequest(BaseModel):
    user_email: str
    email_id: str
    thread_id: str
    email_content: str

class AIResponse(BaseModel):
    response_id: str
    ai_response: str
    status: str
    draft_id: Optional[str] = None

class EmailData(BaseModel):
    id: str
    thread_id: str
    subject: str
    sender: str
    body: str
    date: str
    labelIds: List[str]

class SendEmailRequest(BaseModel):
    user_email: str
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None

class PubSubMessage(BaseModel):
    message: dict
    subscription: str

class AutomationSettings(BaseModel):
    user_email: str
    auto_draft: bool = False
    auto_send: bool = False

class UpdateAutomationRequest(BaseModel):
    user_email: str
    auto_draft: bool
    auto_send: bool

class SendResponseRequest(BaseModel):
    response_id: str
    user_email: str