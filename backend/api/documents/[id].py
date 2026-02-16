"""
Document delete API endpoint for Vercel Serverless Functions
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import json

app = FastAPI()

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(request: Request, document_id: str):
    """
    Handle document delete requests
    """
    # Verify password
    password = request.headers.get("X-App-Password")
    if password != os.getenv("APP_PASSWORD", "demo123"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: Invalid or missing password"}
        )
    
    try:
        # For now, return a sample response
        # In production, you would delete the actual document
        response = {
            "status": "success",
            "message": f"Document {document_id} deleted successfully"
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
