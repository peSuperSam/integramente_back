from fastapi import APIRouter
from app.models.requests import LimiteRequest
from app.models.responses import CalculoLimiteResponse
from app.services.math_service import MathService

router = APIRouter()

@router.post("/limite", response_model=CalculoLimiteResponse)
async def calcular_limite(request: LimiteRequest):
    """
    Realiza cálculo de limite de uma função.
    """
    try:
        # Validar função
        valida, expr, mensagem = MathService.validar_e_processar_funcao(request.funcao)
        if not valida:
            return CalculoLimiteResponse(
                sucesso=False,
                erro=mensagem
            )
        
        # Calcular limite
        resultado_limite = MathService.calcular_limite(
            expr, request.ponto_limite, request.tipo_limite
        )
        
        # Gerar passos se solicitado
        passos_resolucao = None
        if request.mostrar_passos:
            passos_resolucao = MathService.gerar_passos_limite(
                request.funcao,
                request.ponto_limite,
                resultado_limite['valor_limite'],
                request.tipo_limite,
                resultado_limite['existe_limite']
            )
        
        return CalculoLimiteResponse(
            sucesso=True,
            valor_limite=resultado_limite['valor_limite'],
            limite_latex=resultado_limite['limite_latex'] if request.formato_latex else None,
            tipo_limite=request.tipo_limite,
            existe_limite=resultado_limite['existe_limite'],
            passos_resolucao=passos_resolucao,
            funcao_original=request.funcao,
            ponto_limite=request.ponto_limite,
            calculado_em=MathService.obter_timestamp(),
            erro=None
        )
        
    except Exception as e:
        return CalculoLimiteResponse(
            sucesso=False,
            erro=f"Erro no cálculo de limite: {str(e)}"
        ) 