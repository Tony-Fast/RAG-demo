"""
Document upload API endpoint for Vercel Serverless Functions
"""

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
import os
import json

app = FastAPI()

@app.post("/api/v1/documents/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    """
    Handle document upload requests
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
        # In production, you would process and store the document
        response = {
            "status": "success",
            "filename": file.filename,
            "message": f"Document {file.filename} uploaded successfully"
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
