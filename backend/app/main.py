from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.app.auth import router as auth_router
from backend.app.pubsub import router as pubsub_router
from backend.app.agent import router as agent_router
from backend.app.gmail_service import router as gmail_router
from backend.app.db import init_supabase

app = FastAPI(title="AI Email Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-agent-frontend-utvo.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(pubsub_router, prefix="/pubsub", tags=["pubsub"])
app.include_router(agent_router, prefix="/agent", tags=["agent"])
app.include_router(gmail_router, prefix="/gmail", tags=["gmail"])

@app.on_event("startup")
async def startup_event():
    # Initialize Supabase client
    init_supabase()

@app.get("/")
async def root():
    return {"message": "AI Email Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
