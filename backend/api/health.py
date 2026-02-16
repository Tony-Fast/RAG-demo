"""
Health check API endpoint for Vercel Serverless Functions
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "RAG Knowledge Base"
    }

# Vercel Serverless Functions entry point
def handler(request):
    """
    Vercel Serverless Functions handler
    """
    return app(request)
