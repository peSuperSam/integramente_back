from fastapi import APIRouter
from app.models.requests import ValidarRequest
from app.models.responses import ValidarResponse
from app.services.math_service import MathService

router = APIRouter()

@router.post("/validar", response_model=ValidarResponse)
async def validar_funcao(request: ValidarRequest):
    """
    Valida uma função matemática e retorna sua forma simplificada.
    """
    try:
        # Validar e processar função
        valida, expr, mensagem = MathService.validar_e_processar_funcao(request.funcao)
        
        if valida:
            return ValidarResponse(
                valida=True,
                funcao_simplificada=str(expr),
                mensagem="Função válida",
                erro=None
            )
        else:
            return ValidarResponse(
                valida=False,
                funcao_simplificada=None,
                mensagem="Função inválida",
                erro=mensagem
            )
            
    except Exception as e:
        return ValidarResponse(
            valida=False,
            funcao_simplificada=None,
            mensagem="Função inválida",
            erro=f"Erro na validação: {str(e)}"
        ) 