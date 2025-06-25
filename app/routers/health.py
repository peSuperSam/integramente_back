from fastapi import APIRouter
from datetime import datetime

from app.models.responses import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de health check para verificar se o backend está online.
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat()
    ) 