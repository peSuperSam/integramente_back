from fastapi import APIRouter
from app.models.requests import SimbolicoRequest
from app.models.responses import CalculoSimbolicoResponse
from app.services.math_service import MathService
from app.services.enhanced_math_service import EnhancedMathService
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.post("/simbolico", response_model=CalculoSimbolicoResponse)
async def calcular_simbolico(request: SimbolicoRequest):
    """
    Realiza cálculo simbólico de integral com múltiplas abordagens e alta precisão.
    """
    with performance_monitor.measure_calculation("simbolico_calculation", request.funcao):
        try:
            # Verificar cache primeiro
            cache_key = cache_manager.generate_cache_key(
                "simbolico_calculation", request.funcao, request.a, request.b,
                request.mostrar_passos, request.formato_latex
            )
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                performance_monitor.mark_cache_hit(request.funcao)
                return cached_result
            
            # Validar função com análise avançada
            valida, expr, mensagem, analise = EnhancedMathService.validar_e_processar_funcao_avancada(request.funcao)
            if not valida:
                return CalculoSimbolicoResponse(
                    sucesso=False,
                    erro=mensagem
                )
            
            # Calcular integral simbólica com método avançado
            resultado_simbolico = EnhancedMathService.calcular_integral_simbolica_avancada(
                expr, request.a, request.b
            )
            
            # Verificar se cálculo foi bem-sucedido
            if not resultado_simbolico.get('sucesso', True):
                return CalculoSimbolicoResponse(
                    sucesso=False,
                    erro=resultado_simbolico.get('erro', 'Erro desconhecido no cálculo simbólico')
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
                
                # Adicionar informação sobre método usado
                metodo_integracao = resultado_simbolico.get('metodo_integracao', 'integração_direta')
                if metodo_integracao != 'integração_direta':
                    passos_resolucao.append(f"Método utilizado: {metodo_integracao}")
                
                # Adicionar nota sobre fallback numérico se aplicável
                if 'nota' in resultado_simbolico:
                    passos_resolucao.append(f"Observação: {resultado_simbolico['nota']}")
            
            # Criar resposta
            resposta = CalculoSimbolicoResponse(
                sucesso=True,
                antiderivada=resultado_simbolico['antiderivada'],
                antiderivada_latex=resultado_simbolico['antiderivada_latex'] if request.formato_latex else None,
                resultado_simbolico=resultado_simbolico['resultado_simbolico'],
                passos_resolucao=passos_resolucao,
                funcao_original=request.funcao,
                calculado_em=MathService.obter_timestamp(),
                erro=None
            )
            
            # Adicionar informações de análise se disponíveis
            if hasattr(resposta, 'info_adicional'):
                resposta.info_adicional = {
                    'analise_complexidade': analise,
                    'metodo_integracao': resultado_simbolico.get('metodo_integracao', 'integração_direta'),
                    'integral_definida': request.a is not None and request.b is not None
                }
            
            # Cachear resultado
            cache_manager.set(cache_key, resposta)
            
            return resposta
            
        except Exception as e:
            return CalculoSimbolicoResponse(
                sucesso=False,
                erro=f"Erro no cálculo simbólico: {str(e)}"
            ) 