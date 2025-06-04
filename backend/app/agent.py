from fastapi import APIRouter, HTTPException
import os
import json
import google.generativeai as genai
from .schemas import EmailRequest, AIResponse, AutomationSettings, UpdateAutomationRequest,SendResponseRequest
from .db import (
    save_ai_response, 
    get_email_thread, 
    get_user_automation_settings, 
    update_user_automation_settings,
    update_ai_response_draft_id
)
from .gmail_service import send_email_reply, create_gmail_draft

router = APIRouter()

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "mock_gemini_key")
genai.configure(api_key=GEMINI_API_KEY)

@router.post("/generate-response")
async def generate_ai_response(email_request: EmailRequest):
    """Generate AI response for an email using Gemini"""
    try:
        # Get email thread context
        thread_context = await get_email_thread(email_request.thread_id)
        
        # Prepare prompt for AI
        prompt = create_email_prompt(email_request.email_content, thread_context)
        
        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        ai_response = response.text
        
        # Save AI response to Supabase
        response_id = await save_ai_response(
            user_email=email_request.user_email,
            original_email_id=email_request.email_id,
            ai_response=ai_response,
            thread_id=email_request.thread_id
        )
        
        # Check user automation settings
        automation_settings = await get_user_automation_settings(email_request.user_email)
        draft_id = None
        
        # Create draft if auto_draft is enabled
        if automation_settings.get('auto_draft', False):
            draft_result = await create_gmail_draft(
                user_email=email_request.user_email,
                thread_id=email_request.thread_id,
                response_content=ai_response,
                original_email_id=email_request.email_id
            )
            draft_id = draft_result.get('id')
            
            # Update draft ID in database
            await update_ai_response_draft_id(response_id, draft_id)
            
            # Auto send if enabled
            if automation_settings.get('auto_send', False):
                await send_email_reply(
                    user_email=email_request.user_email,
                    thread_id=email_request.thread_id,
                    response_content=ai_response,
                    original_email_id=email_request.email_id
                )
                
                # Update status in database
                from .db import update_ai_response_status
                await update_ai_response_status(response_id, "sent")
        
        return AIResponse(
            response_id=response_id,
            ai_response=ai_response,
            status="sent" if automation_settings.get('auto_send', False) else "generated",
            draft_id=draft_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate-response")
async def regenerate_ai_response(email_request: EmailRequest):
    """Generate an alternative AI response for an email"""
    try:
        # Get email thread context
        thread_context = await get_email_thread(email_request.thread_id)
        
        # Prepare prompt for AI with variation instruction
        prompt = create_email_prompt(
            email_request.email_content, 
            thread_context,
            is_alternative=True
        )
        
        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        ai_response = response.text
        
        # Save AI response to Supabase
        response_id = await save_ai_response(
            user_email=email_request.user_email,
            original_email_id=email_request.email_id,
            ai_response=ai_response,
            thread_id=email_request.thread_id
        )
        
        # Check user automation settings
        automation_settings = await get_user_automation_settings(email_request.user_email)
        draft_id = None
        
        # Create draft if auto_draft is enabled
        if automation_settings.get('auto_draft', False):
            draft_result = await create_gmail_draft(
                user_email=email_request.user_email,
                thread_id=email_request.thread_id,
                response_content=ai_response,
                original_email_id=email_request.email_id
            )
            draft_id = draft_result.get('id')
            
            # Update draft ID in database
            await update_ai_response_draft_id(response_id, draft_id)
        
        return AIResponse(
            response_id=response_id,
            ai_response=ai_response,
            status="generated",
            draft_id=draft_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-response")
async def send_ai_response(request: SendResponseRequest):
    """Send the AI-generated response"""
    try:

        response_id = request.response_id
        user_email = request.user_email
        # Get AI response from Supabase
        from .db import get_ai_response
        ai_response_data = await get_ai_response(response_id)
        
        if not ai_response_data:
            raise HTTPException(status_code=404, detail="AI response not found")
        
        # Send email using Gmail API
        result = await send_email_reply(
            user_email=user_email,
            thread_id=ai_response_data['thread_id'],
            response_content=ai_response_data['ai_response'],
            original_email_id=ai_response_data['original_email_id']
        )
        
        # Update status in Supabase
        from .db import update_ai_response_status
        await update_ai_response_status(response_id, "sent")
        
        return {"status": "sent", "message_id": result['id']}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-draft")
async def create_draft(request: SendResponseRequest):
    """Create a draft in Gmail with the AI-generated response"""
    try:

        response_id = request.response_id
        user_email = request.user_email
        # Get AI response from Supabase
        from .db import get_ai_response
        ai_response_data = await get_ai_response(response_id)
        
        if not ai_response_data:
            raise HTTPException(status_code=404, detail="AI response not found")
        
        # Create draft using Gmail API
        result = await create_gmail_draft(
            user_email=user_email,
            thread_id=ai_response_data['thread_id'],
            response_content=ai_response_data['ai_response'],
            original_email_id=ai_response_data['original_email_id']
        )
        
        # Update draft ID in database
        await update_ai_response_draft_id(response_id, result.get('id'))
        
        return {"status": "draft_created", "draft_id": result.get('id')}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_email_prompt(email_content: str, thread_context: list, is_alternative: bool = False):
    """Create a prompt for AI email response generation"""
    context = "\n".join([f"Previous: {msg['content']}" for msg in thread_context[-3:]])
    
    variation_instruction = ""
    if is_alternative:
        variation_instruction = "Please provide an ALTERNATIVE response that differs from your typical style. Use a different tone, structure, or approach than you normally would."
    
    prompt = f"""
    You are a helpful email assistant. Your task is to write a professional and appropriate response to the email below.
    
    Email Thread Context:
    {context}
    
    Latest Email to Respond to:
    {email_content}
    
    {variation_instruction}
    
    Please generate a professional and appropriate email response. Keep it concise and helpful.
    Only provide the response text, no additional formatting or explanations.
    """
    
    return prompt

@router.get("/responses/{user_email}")
async def get_user_ai_responses(user_email: str, limit: int = 50):
    """Get AI responses for a user"""
    try:
        from .db import get_user_ai_responses
        responses = await get_user_ai_responses(user_email, limit)
        return {"responses": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automation-settings/{user_email}")
async def get_automation_settings(user_email: str):
    """Get user automation settings"""
    try:
        settings = await get_user_automation_settings(user_email)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation-settings")
async def update_automation_settings(request: UpdateAutomationRequest):
    """Update user automation settings"""
    try:
        await update_user_automation_settings(
            request.user_email,
            request.auto_draft,
            request.auto_send
        )
        return {"status": "success", "message": "Automation settings updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
