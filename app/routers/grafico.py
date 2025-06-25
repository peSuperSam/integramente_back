from fastapi import APIRouter
from app.models.requests import GraficoRequest
from app.models.responses import GraficoResponse
from app.services.math_service import MathService

router = APIRouter()

@router.post("/grafico", response_model=GraficoResponse)
async def gerar_grafico(request: GraficoRequest):
    """
    Gera gráfico de uma função matemática em base64.
    """
    try:
        # Validar função
        valida, expr, mensagem = MathService.validar_e_processar_funcao(request.funcao)
        if not valida:
            return GraficoResponse(
                sucesso=False,
                erro=mensagem
            )
        
        # Gerar gráfico
        grafico_base64 = MathService.gerar_grafico_base64(
            expr, request.a, request.b, request.resolucao
        )
        
        # Gerar pontos do gráfico
        pontos_grafico = MathService.gerar_pontos_grafico(
            expr, request.a, request.b, request.resolucao
        )
        
        return GraficoResponse(
            sucesso=True,
            grafico_base64=grafico_base64,
            pontos_grafico=pontos_grafico,
            erro=None
        )
        
    except Exception as e:
        return GraficoResponse(
            sucesso=False,
            erro=f"Erro ao gerar gráfico: {str(e)}"
        ) 