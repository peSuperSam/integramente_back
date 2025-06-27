from fastapi import APIRouter
from app.models.requests import ValidarRequest
from app.models.responses import ValidarResponse
from app.services.math_service import MathService
from app.services.enhanced_math_service import EnhancedMathService
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.post("/validar", response_model=ValidarResponse)
async def validar_funcao(request: ValidarRequest):
    """
    Valida uma função matemática com análise de complexidade e otimizações avançadas.
    """
    with performance_monitor.measure_calculation("validation", request.funcao):
        try:
            # Verificar cache primeiro
            cache_key = cache_manager.generate_cache_key("validation", request.funcao)
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                performance_monitor.mark_cache_hit(request.funcao)
                return cached_result
            
            # Validar e processar função com método avançado
            valida, expr, mensagem, analise = EnhancedMathService.validar_e_processar_funcao_avancada(request.funcao)
            
            if valida:
                # Criar mensagem detalhada com análise
                mensagem_detalhada = "Função válida"
                
                if analise:
                    nivel_complexidade = analise.get('nivel_complexidade', 'desconhecido')
                    nos_totais = analise.get('nos_totais', 0)
                    
                    mensagem_detalhada += f" (Complexidade: {nivel_complexidade}, Nós: {nos_totais})"
                    
                    # Adicionar informações sobre tipos de operações
                    operacoes = analise.get('operacoes', {})
                    if any(operacoes.values()):
                        tipos_ops = [k for k, v in operacoes.items() if v > 0]
                        if tipos_ops:
                            mensagem_detalhada += f", Operações: {', '.join(tipos_ops)}"
                
                resposta = ValidarResponse(
                    valida=True,
                    funcao_simplificada=str(expr),
                    mensagem=mensagem_detalhada,
                    erro=None
                )
                
                # Adicionar informações de análise se disponíveis
                if hasattr(resposta, 'info_adicional'):
                    resposta.info_adicional = {
                        'analise_complexidade': analise,
                        'funcao_original': request.funcao,
                        'recomendacoes': _gerar_recomendacoes_validacao(analise)
                    }
            else:
                resposta = ValidarResponse(
                    valida=False,
                    funcao_simplificada=None,
                    mensagem="Função inválida",
                    erro=mensagem
                )
            
            # Cachear resultado
            cache_manager.set(cache_key, resposta)
            
            return resposta
            
        except Exception as e:
            return ValidarResponse(
                valida=False,
                funcao_simplificada=None,
                mensagem="Função inválida",
                erro=f"Erro na validação: {str(e)}"
            )

def _gerar_recomendacoes_validacao(analise: dict) -> list:
    """
    Gera recomendações baseadas na análise da função.
    """
    recomendacoes = []
    
    if not analise:
        return recomendacoes
    
    complexidade = analise.get('complexidade', 0)
    operacoes = analise.get('operacoes', {})
    
    # Recomendações baseadas na complexidade
    if complexidade > 500:
        recomendacoes.append("Função muito complexa - considere simplificar para melhor performance")
    elif complexidade > 200:
        recomendacoes.append("Função moderadamente complexa - pode impactar performance")
    
    # Recomendações baseadas em tipos de operações
    if operacoes.get('trigonometricas', 0) > 5:
        recomendacoes.append("Muitas funções trigonométricas - verifique se há simplificações possíveis")
    
    if operacoes.get('exponenciais', 0) > 3:
        recomendacoes.append("Funções exponenciais podem ser numericamente instáveis")
    
    if operacoes.get('logaritmicas', 0) > 3:
        recomendacoes.append("Cuidado com domínio de funções logarítmicas")
    
    if not recomendacoes:
        recomendacoes.append("Função bem estruturada para cálculos")
    
    return recomendacoes 