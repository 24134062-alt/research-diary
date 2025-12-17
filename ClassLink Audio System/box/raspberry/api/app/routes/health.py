"""
Health Check Routes
Simple endpoints to verify service status
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "ok",
        "service": "ClassLink Audio Manager API",
        "version": "2.0.1"
    }

@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}
