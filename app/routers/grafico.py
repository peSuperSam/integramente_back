from fastapi import APIRouter
from app.models.requests import GraficoRequest
from app.models.responses import GraficoResponse
from app.services.math_service import MathService
from app.services.enhanced_math_service import EnhancedMathService
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.post("/grafico", response_model=GraficoResponse)
async def gerar_grafico(request: GraficoRequest):
    """
    Gera gráfico otimizado com detecção de singularidades e renderização adaptativa.
    """
    with performance_monitor.measure_calculation("grafico_generation", request.funcao):
        try:
            # Verificar cache primeiro
            cache_key = cache_manager.generate_cache_key(
                "grafico_generation", request.funcao, request.a, request.b, request.resolucao
            )
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                performance_monitor.mark_cache_hit(request.funcao)
                return cached_result
            
            # Validar função com análise avançada
            valida, expr, mensagem, analise = EnhancedMathService.validar_e_processar_funcao_avancada(request.funcao)
            if not valida:
                return GraficoResponse(
                    sucesso=False,
                    erro=mensagem
                )
            
            # Gerar gráfico otimizado
            grafico_base64, pontos_grafico, info_grafico = EnhancedMathService.gerar_grafico_otimizado(
                expr, request.a, request.b, request.resolucao
            )
            
            # Criar resposta
            resposta = GraficoResponse(
                sucesso=True,
                grafico_base64=grafico_base64,
                pontos_grafico=pontos_grafico,
                erro=None
            )
            
            # Adicionar informações de análise se disponíveis
            if hasattr(resposta, 'info_adicional'):
                resposta.info_adicional = {
                    'analise_complexidade': analise,
                    'info_grafico': info_grafico,
                    'intervalo': [request.a, request.b],
                    'resolucao_solicitada': request.resolucao
                }
            
            # Cachear resultado
            cache_manager.set(cache_key, resposta)
            
            return resposta
            
        except Exception as e:
            return GraficoResponse(
                sucesso=False,
                erro=f"Erro ao gerar gráfico: {str(e)}"
            ) 