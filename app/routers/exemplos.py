from fastapi import APIRouter
from app.models.responses import ExemplosResponse
from app.services.exemplos_service import ExemplosService

router = APIRouter()

@router.get("/exemplos", response_model=ExemplosResponse)
async def obter_exemplos():
    """
    Retorna exemplos organizados de funções matemáticas por categoria.
    """
    exemplos = ExemplosService.obter_exemplos()
    total = ExemplosService.contar_total_exemplos(exemplos)
    
    return ExemplosResponse(
        exemplos=exemplos,
        total=total
    ) 