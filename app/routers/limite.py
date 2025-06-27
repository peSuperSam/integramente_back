from fastapi import APIRouter
from app.models.requests import LimiteRequest
from app.models.responses import CalculoLimiteResponse
from app.services.math_service import MathService
from app.services.enhanced_math_service import EnhancedMathService
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.post("/limite", response_model=CalculoLimiteResponse)
async def calcular_limite(request: LimiteRequest):
    """
    Realiza cálculo de limite com múltiplas abordagens e análise de convergência.
    """
    with performance_monitor.measure_calculation("limite_calculation", request.funcao):
        try:
            # Verificar cache primeiro
            cache_key = cache_manager.generate_cache_key(
                "limite_calculation", request.funcao, request.ponto_limite, 
                request.tipo_limite, request.mostrar_passos, request.formato_latex
            )
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                performance_monitor.mark_cache_hit(request.funcao)
                return cached_result
            
            # Validar função com análise avançada
            valida, expr, mensagem, analise = EnhancedMathService.validar_e_processar_funcao_avancada(request.funcao)
            if not valida:
                return CalculoLimiteResponse(
                    sucesso=False,
                    erro=mensagem
                )
            
            # Calcular limite com método avançado
            resultado_limite = EnhancedMathService.calcular_limite_avancado(
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
                
                # Adicionar informações sobre método usado
                metodo_usado = resultado_limite.get('metodo_usado', 'direto')
                if metodo_usado != 'direto':
                    passos_resolucao.append(f"Método utilizado: {metodo_usado}")
                
                # Adicionar análise de convergência
                tipo_convergencia = resultado_limite.get('tipo_convergencia', '')
                if tipo_convergencia:
                    passos_resolucao.append(f"Tipo de convergência: {tipo_convergencia}")
            
            # Criar resposta
            resposta = CalculoLimiteResponse(
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
            
            # Adicionar informações de análise se disponíveis
            if hasattr(resposta, 'info_adicional'):
                resposta.info_adicional = {
                    'analise_complexidade': analise,
                    'metodo_usado': resultado_limite.get('metodo_usado', 'direto'),
                    'todos_calculos': resultado_limite.get('todos_calculos', {}),
                    'tipo_convergencia': resultado_limite.get('tipo_convergencia', '')
                }
            
            # Cachear resultado
            cache_manager.set(cache_key, resposta)
            
            return resposta
            
        except Exception as e:
            return CalculoLimiteResponse(
                sucesso=False,
                erro=f"Erro no cálculo de limite: {str(e)}"
            ) 