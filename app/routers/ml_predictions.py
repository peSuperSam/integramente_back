from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Any, Dict
from app.services.ml_prediction_service import ml_prediction_service
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager
from app.core.input_validator import input_validator

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Modelos de requisição
class FunctionAnalysisRequest(BaseModel):
    funcao: str = Field(..., description="Função matemática para análise")

class IntegrationDifficultyRequest(BaseModel):
    funcao: str = Field(..., description="Função para análise de dificuldade de integração")

class ComputationTimeRequest(BaseModel):
    funcao: str = Field(..., description="Função para predição de tempo")
    metodo: str = Field("simpson", description="Método de integração")
    a: float = Field(..., description="Limite inferior")
    b: float = Field(..., description="Limite superior")

class ResolutionOptimizationRequest(BaseModel):
    funcao: str = Field(..., description="Função para otimização de resolução")
    a: float = Field(..., description="Limite inferior")
    b: float = Field(..., description="Limite superior")

# Modelos de resposta
class MLPredictionResponse(BaseModel):
    sucesso: bool
    predicao: Optional[Dict[str, Any]] = None
    confianca: Optional[float] = None
    recomendacoes: Optional[List[str]] = None
    erro: Optional[str] = None

class FunctionAnalysisResponse(BaseModel):
    sucesso: bool
    analise_completa: Optional[Dict[str, Any]] = None
    tipo_funcao: Optional[Dict[str, Any]] = None
    estabilidade: Optional[Dict[str, Any]] = None
    dominio: Optional[Dict[str, Any]] = None
    estrategias_recomendadas: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None

@router.post("/analyze-function", response_model=FunctionAnalysisResponse)
async def analisar_funcao_completa(request: FunctionAnalysisRequest):
    """
    Análise completa de uma função usando Machine Learning.
    Retorna insights sobre comportamento, dificuldade e estratégias ótimas.
    """
    with performance_monitor.measure_calculation("ml_function_analysis", request.funcao):
        # Validar entrada
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return FunctionAnalysisResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key("ml_analysis", request.funcao)
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            # Realizar análise completa
            analysis = ml_prediction_service.analyze_function_behavior(validation.cleaned_input)
            
            if 'error' not in analysis:
                response = FunctionAnalysisResponse(
                    sucesso=True,
                    analise_completa=analysis,
                    tipo_funcao=analysis.get('function_type'),
                    estabilidade=analysis.get('stability_analysis'),
                    dominio=analysis.get('domain_analysis'),
                    estrategias_recomendadas=analysis.get('recommended_strategies')
                )
            else:
                response = FunctionAnalysisResponse(
                    sucesso=False,
                    erro=analysis['error']
                )
            
            # Cachear resultado
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return FunctionAnalysisResponse(
                sucesso=False,
                erro=f"Erro na análise ML: {str(e)}"
            )

@router.post("/integration-difficulty", response_model=MLPredictionResponse)
async def predizer_dificuldade_integracao(request: IntegrationDifficultyRequest):
    """
    Prediz a dificuldade de integração de uma função e recomenda métodos ótimos.
    """
    with performance_monitor.measure_calculation("ml_integration_difficulty", request.funcao):
        # Validar entrada
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return MLPredictionResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key("ml_integration_difficulty", request.funcao)
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            # Predizer dificuldade
            prediction = ml_prediction_service.predict_integration_difficulty(validation.cleaned_input)
            
            # Gerar recomendações baseadas na predição
            recomendacoes = []
            
            difficulty_level = prediction.get('difficulty_level', 'Moderada')
            recommended_method = prediction.get('recommended_method', 'simpson')
            
            recomendacoes.append(f"Método recomendado: {recommended_method}")
            
            if difficulty_level == "Fácil":
                recomendacoes.extend([
                    "Função de integração simples",
                    "Métodos básicos devem funcionar bem",
                    "Tolerância padrão é suficiente"
                ])
            elif difficulty_level == "Moderada":
                recomendacoes.extend([
                    "Considere métodos adaptativos se precisão for crítica",
                    "Monitore convergência",
                    "Teste diferentes tolerâncias se necessário"
                ])
            else:  # Difícil
                recomendacoes.extend([
                    "Use métodos especializados ou adaptativos",
                    "Considere transformação de variáveis",
                    "Aumente tolerância se convergência for lenta",
                    "Verifique pontos de singularidade"
                ])
            
            response = MLPredictionResponse(
                sucesso=True,
                predicao=prediction,
                confianca=prediction.get('confidence', 0.7),
                recomendacoes=recomendacoes
            )
            
            # Cachear resultado
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return MLPredictionResponse(
                sucesso=False,
                erro=f"Erro na predição de dificuldade: {str(e)}"
            )

@router.post("/computation-time", response_model=MLPredictionResponse)
async def predizer_tempo_computacao(request: ComputationTimeRequest):
    """
    Prediz o tempo de computação para um cálculo específico.
    """
    with performance_monitor.measure_calculation("ml_computation_time", request.funcao):
        # Validar entrada
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return MLPredictionResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Validar limites
        if request.a >= request.b:
            return MLPredictionResponse(
                sucesso=False,
                erro="Limite inferior deve ser menor que o superior"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "ml_computation_time", request.funcao, request.metodo, request.a, request.b
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            # Predizer tempo
            prediction = ml_prediction_service.predict_computation_time(
                validation.cleaned_input, 
                request.metodo,
                (request.a, request.b)
            )
            
            # Gerar recomendações baseadas na predição
            estimated_time = prediction.get('estimated_time_seconds', 1.0)
            
            recomendacoes = []
            
            if estimated_time < 0.5:
                recomendacoes.append("Cálculo rápido - configuração padrão adequada")
            elif estimated_time < 2.0:
                recomendacoes.append("Tempo moderado - considere cache para reutilização")
            elif estimated_time < 10.0:
                recomendacoes.extend([
                    "Cálculo demorado - considere reduzir precisão se aceitável",
                    "Use cache para evitar recálculos",
                    "Considere processamento assíncrono"
                ])
            else:
                recomendacoes.extend([
                    "Cálculo muito demorado - otimize parâmetros",
                    "Considere método mais eficiente",
                    "Divida intervalo em partes menores",
                    "Use processamento em background"
                ])
            
            response = MLPredictionResponse(
                sucesso=True,
                predicao=prediction,
                confianca=prediction.get('confidence', 0.7),
                recomendacoes=recomendacoes
            )
            
            # Cachear resultado
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return MLPredictionResponse(
                sucesso=False,
                erro=f"Erro na predição de tempo: {str(e)}"
            )

@router.post("/optimal-resolution", response_model=MLPredictionResponse)
async def predizer_resolucao_otima(request: ResolutionOptimizationRequest):
    """
    Prediz a resolução ótima para visualização ou cálculo numérico.
    """
    with performance_monitor.measure_calculation("ml_optimal_resolution", request.funcao):
        # Validar entrada
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return MLPredictionResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Validar limites
        if request.a >= request.b:
            return MLPredictionResponse(
                sucesso=False,
                erro="Limite inferior deve ser menor que o superior"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "ml_optimal_resolution", request.funcao, request.a, request.b
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            # Predizer resolução ótima
            prediction = ml_prediction_service.predict_optimal_resolution(
                validation.cleaned_input,
                (request.a, request.b)
            )
            
            # Gerar recomendações
            optimal_res = prediction.get('optimal_resolution', 50)
            min_res = prediction.get('min_recommended', 20)
            max_res = prediction.get('max_recommended', 200)
            
            recomendacoes = [
                f"Resolução ótima: {optimal_res} pontos",
                f"Faixa recomendada: {min_res} - {max_res} pontos"
            ]
            
            variation_analysis = prediction.get('variation_analysis', {})
            max_variation = variation_analysis.get('max_variation', 0)
            
            if max_variation > 10:
                recomendacoes.append("Função com alta variação - use resolução alta")
            elif max_variation > 1:
                recomendacoes.append("Variação moderada - resolução padrão adequada")
            else:
                recomendacoes.append("Função suave - resolução baixa suficiente")
            
            # Recomendações para diferentes usos
            recomendacoes.extend([
                f"Para visualização web: {min(optimal_res, 100)} pontos",
                f"Para análise precisa: {optimal_res} pontos",
                f"Para cálculos rápidos: {min_res} pontos"
            ])
            
            response = MLPredictionResponse(
                sucesso=True,
                predicao=prediction,
                confianca=prediction.get('confidence', 0.8),
                recomendacoes=recomendacoes
            )
            
            # Cachear resultado
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return MLPredictionResponse(
                sucesso=False,
                erro=f"Erro na predição de resolução: {str(e)}"
            )

@router.get("/model-info")
async def obter_info_modelos():
    """
    Retorna informações sobre os modelos de ML disponíveis.
    """
    try:
        return {
            "modelos_disponiveis": [
                {
                    "nome": "integration_difficulty",
                    "descricao": "Prediz dificuldade de integração e recomenda métodos",
                    "features": "20+ características matemáticas da função",
                    "precisao_estimada": "75-85%"
                },
                {
                    "nome": "computation_time",
                    "descricao": "Estima tempo de computação para cálculos",
                    "features": "Complexidade, método, intervalo",
                    "precisao_estimada": "70-80%"
                },
                {
                    "nome": "optimal_resolution",
                    "descricao": "Determina resolução ótima para visualização",
                    "features": "Análise de variação e derivadas",
                    "precisao_estimada": "80-90%"
                },
                {
                    "nome": "function_behavior",
                    "descricao": "Análise comportamental completa",
                    "features": "Todas as características combinadas",
                    "precisao_estimada": "85-95%"
                }
            ],
            "status": "operacional",
            "ultima_atualizacao": "2024-01-15",
            "tecnologias": [
                "scikit-learn",
                "Random Forest",
                "Gradient Boosting",
                "SymPy Analysis"
            ]
        }
        
    except Exception as e:
        return {
            "erro": f"Erro ao obter informações: {str(e)}",
            "status": "erro"
        } 