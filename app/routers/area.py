from fastapi import APIRouter, HTTPException
from app.models.requests import AreaRequest
from app.models.responses import AreaResponse
from app.services.math_service import MathService
from app.services.enhanced_math_service import EnhancedMathService
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.post("/area", response_model=AreaResponse)
async def calcular_area(request: AreaRequest):
    """
    Calcula a área sob a curva de uma função em um intervalo dado com otimizações avançadas.
    """
    with performance_monitor.measure_calculation("area_calculation", request.funcao):
        try:
            # Validar função com serviço aprimorado
            valida, expr, mensagem, analise = EnhancedMathService.validar_e_processar_funcao_avancada(request.funcao)
            if not valida:
                return AreaResponse(
                    sucesso=False,
                    erro=mensagem
                )
            
            # Verificar se resultado está em cache
            cache_key = cache_manager.generate_cache_key(
                "area_calculation", request.funcao, request.a, request.b, request.resolucao
            )
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                performance_monitor.mark_cache_hit(request.funcao)
                return cached_result
            
            # Calcular integral numérica com método avançado
            valor_integral, erro_estimado, info_calculo = EnhancedMathService.calcular_integral_numerica_avancada(
                expr, request.a, request.b, tolerancia=1e-10
            )
            
            # Gerar gráfico otimizado
            grafico_base64, pontos_grafico, info_grafico = EnhancedMathService.gerar_grafico_otimizado(
                expr, request.a, request.b, request.resolucao
            )
            
            # Criar resposta
            resposta = AreaResponse(
                sucesso=True,
                valor_integral=valor_integral,
                area_total=abs(valor_integral),  # Área sempre positiva
                erro_estimado=erro_estimado,
                grafico_base64=grafico_base64,
                pontos_grafico=pontos_grafico,
                funcao_formatada=str(expr),
                intervalo={"a": request.a, "b": request.b},
                calculado_em=MathService.obter_timestamp(),
                erro=None
            )
            
            # Adicionar informações de análise se disponíveis
            if hasattr(resposta, 'info_adicional'):
                resposta.info_adicional = {
                    'analise_complexidade': analise,
                    'metodo_integracao': info_calculo,
                    'info_grafico': info_grafico
                }
            
            # Cachear resultado para futuras consultas
            cache_manager.set(cache_key, resposta)
            
            return resposta
            
        except Exception as e:
            return AreaResponse(
                sucesso=False,
                erro=f"Erro no cálculo da área: {str(e)}"
            ) 