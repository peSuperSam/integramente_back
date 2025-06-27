from fastapi import APIRouter
from app.models.requests import DerivadaRequest
from app.models.responses import CalculoDerivadaResponse
from app.services.math_service import MathService

router = APIRouter()

@router.post("/derivada", response_model=CalculoDerivadaResponse)
async def calcular_derivada(request: DerivadaRequest):
    """
    Realiza cálculo de derivada de uma função.
    """
    try:
        # Validar função
        valida, expr, mensagem = MathService.validar_e_processar_funcao(request.funcao)
        if not valida:
            return CalculoDerivadaResponse(
                sucesso=False,
                erro=mensagem
            )
        
        # Calcular derivada
        resultado_derivada = MathService.calcular_derivada(
            expr, request.tipo_derivada
        )
        
        # Gerar passos se solicitado
        passos_resolucao = None
        if request.mostrar_passos:
            passos_resolucao = MathService.gerar_passos_derivada(
                request.funcao,
                resultado_derivada['derivada'],
                request.tipo_derivada
            )
        
        return CalculoDerivadaResponse(
            sucesso=True,
            derivada=resultado_derivada['derivada'],
            derivada_latex=resultado_derivada['derivada_latex'] if request.formato_latex else None,
            derivada_simplificada=resultado_derivada['derivada_simplificada'],
            passos_resolucao=passos_resolucao,
            funcao_original=request.funcao,
            tipo_derivada=request.tipo_derivada,
            calculado_em=MathService.obter_timestamp(),
            erro=None
        )
        
    except Exception as e:
        return CalculoDerivadaResponse(
            sucesso=False,
            erro=f"Erro no cálculo de derivada: {str(e)}"
        ) 