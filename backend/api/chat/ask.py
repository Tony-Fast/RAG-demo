"""
Chat API endpoint for Vercel Serverless Functions
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import json

app = FastAPI()

@app.post("/api/v1/chat/ask")
async def ask_question(request: Request):
    """
    Handle chat question requests
    """
    # Verify password
    password = request.headers.get("X-App-Password")
    if password != os.getenv("APP_PASSWORD", "demo123"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: Invalid or missing password"}
        )
    
    try:
        # Get request body
        body = await request.json()
        question = body.get("question", "")
        document_id = body.get("document_id")
        context = body.get("context", [])
        
        # For now, return a sample response
        # In production, you would integrate with your RAG system
        response = {
            "question": question,
            "answer": f"This is a sample response to: {question}",
            "sources": [],
            "model": "deepseek-chat",
            "response_time": 1.0,
            "tokens_used": None
        }
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )

# Vercel Serverless Functions entry point
def handler(request):
    """
    Vercel Serverless Functions handler
    """
    import uvicorn
    from starlette.middleware.cors import CORSMiddleware
    
    # Add CORS middleware
    origins = os.getenv("CORS_ORIGINS", "https://kef-ragdemo.top").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Handle request
    return app(request)
