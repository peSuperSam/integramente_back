from fastapi import APIRouter
from app.models.requests import SimbolicoRequest
from app.models.responses import SimbolicoResponse
from app.services.math_service import MathService

router = APIRouter()

@router.post("/simbolico", response_model=SimbolicoResponse)
async def calcular_simbolico(request: SimbolicoRequest):
    """
    Realiza cálculo simbólico de integral (indefinida ou definida).
    """
    try:
        # Validar função
        valida, expr, mensagem = MathService.validar_e_processar_funcao(request.funcao)
        if not valida:
            return SimbolicoResponse(
                sucesso=False,
                erro=mensagem
            )
        
        # Calcular integral simbólica
        resultado_simbolico = MathService.calcular_integral_simbolica(
            expr, request.a, request.b
        )
        
        # Gerar passos se solicitado
        passos_resolucao = None
        if request.mostrar_passos:
            passos_resolucao = MathService.gerar_passos_resolucao(
                request.funcao,
                resultado_simbolico['antiderivada'],
                request.a,
                request.b
            )
        
        return SimbolicoResponse(
            sucesso=True,
            antiderivada=resultado_simbolico['antiderivada'],
            antiderivada_latex=resultado_simbolico['antiderivada_latex'] if request.formato_latex else None,
            resultado_simbolico=resultado_simbolico['resultado_simbolico'],
            passos_resolucao=passos_resolucao,
            funcao_original=request.funcao,
            calculado_em=MathService.obter_timestamp(),
            erro=None
        )
        
    except Exception as e:
        return SimbolicoResponse(
            sucesso=False,
            erro=f"Erro no cálculo simbólico: {str(e)}"
        ) 