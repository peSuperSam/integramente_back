from fastapi import APIRouter
from app.models.requests import DerivadaRequest
from app.models.responses import CalculoDerivadaResponse
from app.services.math_service import MathService
from app.services.enhanced_math_service import EnhancedMathService
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.post("/derivada", response_model=CalculoDerivadaResponse)
async def calcular_derivada(request: DerivadaRequest):
    """
    Realiza cálculo de derivada com análise avançada e otimizações.
    """
    with performance_monitor.measure_calculation("derivada_calculation", request.funcao):
        try:
            # Verificar cache primeiro
            cache_key = cache_manager.generate_cache_key(
                "derivada_calculation", request.funcao, request.tipo_derivada, 
                request.mostrar_passos, request.formato_latex
            )
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                performance_monitor.mark_cache_hit(request.funcao)
                return cached_result
            
            # Validar função com análise avançada
            valida, expr, mensagem, analise = EnhancedMathService.validar_e_processar_funcao_avancada(request.funcao)
            if not valida:
                return CalculoDerivadaResponse(
                    sucesso=False,
                    erro=mensagem
                )
            
            # Calcular derivada com método avançado
            resultado_derivada = EnhancedMathService.calcular_derivada_avancada(
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
                
                # Adicionar análise de pontos críticos se disponível
                if 'analise' in resultado_derivada and 'pontos_criticos' in resultado_derivada['analise']:
                    pontos_criticos = resultado_derivada['analise']['pontos_criticos']
                    if isinstance(pontos_criticos, list) and pontos_criticos:
                        passos_resolucao.append(f"Pontos críticos encontrados: {pontos_criticos[:5]}")
            
            # Criar resposta
            resposta = CalculoDerivadaResponse(
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
            
            # Adicionar informações de análise se disponíveis
            if hasattr(resposta, 'info_adicional'):
                resposta.info_adicional = {
                    'analise_complexidade': analise,
                    'analise_derivada': resultado_derivada.get('analise', {}),
                    'ordem_derivada': resultado_derivada.get('ordem', 1)
                }
            
            # Cachear resultado
            cache_manager.set(cache_key, resposta)
            
            return resposta
            
        except Exception as e:
            return CalculoDerivadaResponse(
                sucesso=False,
                erro=f"Erro no cálculo de derivada: {str(e)}"
            ) 