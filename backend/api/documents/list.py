"""
Document list API endpoint for Vercel Serverless Functions
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import json

app = FastAPI()

@app.get("/api/v1/documents/list")
async def list_documents(request: Request):
    """
    Handle document list requests
    """
    # Verify password
    password = request.headers.get("X-App-Password")
    if password != os.getenv("APP_PASSWORD", "demo123"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: Invalid or missing password"}
        )
    
    try:
        # For now, return sample documents
        # In production, you would retrieve actual documents
        sample_documents = [
            {
                "id": "1",
                "title": "Sample Document 1",
                "filename": "sample1.txt",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "2",
                "title": "Sample Document 2",
                "filename": "sample2.pdf",
                "created_at": "2024-01-02T00:00:00Z"
            }
        ]
        
        response = {
            "documents": sample_documents
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
    return app(request)
