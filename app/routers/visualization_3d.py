from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Any, Dict
from app.services.visualization_3d_service import visualization_3d_service
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager
from app.core.input_validator import input_validator

router = APIRouter(prefix="/3d", tags=["Visualização 3D"])

# Modelos de requisição
class SurfacePlotRequest(BaseModel):
    funcao: str = Field(..., description="Função de duas variáveis f(x,y)")
    x_min: float = Field(-5, description="Valor mínimo de x")
    x_max: float = Field(5, description="Valor máximo de x")
    y_min: float = Field(-5, description="Valor mínimo de y")
    y_max: float = Field(5, description="Valor máximo de y")
    resolucao: int = Field(50, ge=10, le=200, description="Resolução da grade")
    esquema_cor: str = Field("viridis", description="Esquema de cores")
    titulo: Optional[str] = Field(None, description="Título personalizado")

class ContourPlotRequest(BaseModel):
    funcao: str = Field(..., description="Função de duas variáveis f(x,y)")
    x_min: float = Field(-5, description="Valor mínimo de x")
    x_max: float = Field(5, description="Valor máximo de x")
    y_min: float = Field(-5, description="Valor mínimo de y")
    y_max: float = Field(5, description="Valor máximo de y")
    niveis: int = Field(20, ge=5, le=50, description="Número de níveis de contorno")
    resolucao: int = Field(100, ge=20, le=300, description="Resolução da grade")

class VectorFieldRequest(BaseModel):
    fx: str = Field(..., description="Componente x do campo vetorial")
    fy: str = Field(..., description="Componente y do campo vetorial")
    fz: str = Field(..., description="Componente z do campo vetorial")
    x_min: float = Field(-3, description="Valor mínimo de x")
    x_max: float = Field(3, description="Valor máximo de x")
    y_min: float = Field(-3, description="Valor mínimo de y")
    y_max: float = Field(3, description="Valor máximo de y")
    z_min: float = Field(-3, description="Valor mínimo de z")
    z_max: float = Field(3, description="Valor máximo de z")
    densidade: int = Field(10, ge=5, le=20, description="Densidade do campo")

class ParametricSurfaceRequest(BaseModel):
    x_func: str = Field(..., description="Função paramétrica x(u,v)")
    y_func: str = Field(..., description="Função paramétrica y(u,v)")
    z_func: str = Field(..., description="Função paramétrica z(u,v)")
    u_min: float = Field(0, description="Valor mínimo do parâmetro u")
    u_max: float = Field(6.28, description="Valor máximo do parâmetro u")
    v_min: float = Field(0, description="Valor mínimo do parâmetro v")
    v_max: float = Field(3.14, description="Valor máximo do parâmetro v")
    resolucao: int = Field(50, ge=10, le=100, description="Resolução da grade")

class IntegrationVolumeRequest(BaseModel):
    funcao: str = Field(..., description="Função f(x,y) para integração")
    x_min: float = Field(..., description="Limite inferior de x")
    x_max: float = Field(..., description="Limite superior de x")
    y_min: float = Field(..., description="Limite inferior de y")
    y_max: float = Field(..., description="Limite superior de y")
    mostrar_volume: bool = Field(True, description="Mostrar visualização do volume")
    resolucao: int = Field(30, ge=10, le=100, description="Resolução da grade")

class GradientFieldRequest(BaseModel):
    funcao: str = Field(..., description="Função escalar f(x,y)")
    x_min: float = Field(-3, description="Valor mínimo de x")
    x_max: float = Field(3, description="Valor máximo de x")
    y_min: float = Field(-3, description="Valor mínimo de y")
    y_max: float = Field(3, description="Valor máximo de y")
    densidade: int = Field(15, ge=5, le=25, description="Densidade do campo")

# Modelo de resposta
class Visualization3DResponse(BaseModel):
    sucesso: bool
    plotly_json: Optional[str] = None
    tipo_grafico: Optional[str] = None
    funcao: Optional[str] = None
    estatisticas: Optional[Dict[str, Any]] = None
    info_adicional: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None

@router.post("/surface", response_model=Visualization3DResponse)
async def criar_superficie_3d(request: SurfacePlotRequest):
    """
    Cria gráfico de superfície 3D para função de duas variáveis.
    """
    with performance_monitor.measure_calculation("surface_3d", request.funcao):
        # Validar entrada
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "surface_3d", request.funcao, request.x_min, request.x_max,
            request.y_min, request.y_max, request.resolucao, request.esquema_cor
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            # Gerar superfície 3D
            result = visualization_3d_service.create_surface_plot(
                function_str=validation.cleaned_input,
                x_range=(request.x_min, request.x_max),
                y_range=(request.y_min, request.y_max),
                resolution=request.resolucao,
                colorscale=request.esquema_cor,
                title=request.titulo
            )
            
            if result['success']:
                response = Visualization3DResponse(
                    sucesso=True,
                    plotly_json=result['plotly_json'],
                    tipo_grafico=result['plot_type'],
                    funcao=result['function'],
                    estatisticas=result.get('statistics'),
                    info_adicional={
                        'interactive': result.get('interactive', True),
                        'colorscale': request.esquema_cor,
                        'resolution': request.resolucao
                    }
                )
            else:
                response = Visualization3DResponse(
                    sucesso=False,
                    erro=result['error']
                )
            
            # Cachear resultado
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Erro interno: {str(e)}"
            )

@router.post("/contour", response_model=Visualization3DResponse)
async def criar_contorno_3d(request: ContourPlotRequest):
    """
    Cria gráfico de contorno 3D com linhas de nível.
    """
    with performance_monitor.measure_calculation("contour_3d", request.funcao):
        # Validar entrada
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "contour_3d", request.funcao, request.x_min, request.x_max,
            request.y_min, request.y_max, request.niveis, request.resolucao
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            result = visualization_3d_service.create_contour_3d(
                function_str=validation.cleaned_input,
                x_range=(request.x_min, request.x_max),
                y_range=(request.y_min, request.y_max),
                z_levels=request.niveis,
                resolution=request.resolucao
            )
            
            if result['success']:
                response = Visualization3DResponse(
                    sucesso=True,
                    plotly_json=result['plotly_json'],
                    tipo_grafico=result['plot_type'],
                    funcao=result['function'],
                    info_adicional={
                        'levels': result.get('levels'),
                        'resolution': request.resolucao
                    }
                )
            else:
                response = Visualization3DResponse(
                    sucesso=False,
                    erro=result['error']
                )
            
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Erro interno: {str(e)}"
            )

@router.post("/vector-field", response_model=Visualization3DResponse)
async def criar_campo_vetorial_3d(request: VectorFieldRequest):
    """
    Cria visualização de campo vetorial 3D.
    """
    with performance_monitor.measure_calculation("vector_field_3d", f"{request.fx},{request.fy},{request.fz}"):
        # Validar todas as componentes
        validations = []
        for func_str in [request.fx, request.fy, request.fz]:
            validation = input_validator.validate_function_input(func_str)
            if not validation.is_valid:
                return Visualization3DResponse(
                    sucesso=False,
                    erro=f"Função inválida '{func_str}': {', '.join(validation.issues)}"
                )
            validations.append(validation.cleaned_input)
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "vector_field_3d", *validations, request.x_min, request.x_max,
            request.y_min, request.y_max, request.z_min, request.z_max, request.densidade
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(f"{request.fx},{request.fy},{request.fz}")
            return cached_result
        
        try:
            result = visualization_3d_service.create_vector_field_3d(
                fx_str=validations[0],
                fy_str=validations[1],
                fz_str=validations[2],
                x_range=(request.x_min, request.x_max),
                y_range=(request.y_min, request.y_max),
                z_range=(request.z_min, request.z_max),
                density=request.densidade
            )
            
            if result['success']:
                response = Visualization3DResponse(
                    sucesso=True,
                    plotly_json=result['plotly_json'],
                    tipo_grafico=result['plot_type'],
                    info_adicional={
                        'functions': result.get('functions'),
                        'density': request.densidade
                    }
                )
            else:
                response = Visualization3DResponse(
                    sucesso=False,
                    erro=result['error']
                )
            
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Erro interno: {str(e)}"
            )

@router.post("/parametric-surface", response_model=Visualization3DResponse)
async def criar_superficie_parametrica(request: ParametricSurfaceRequest):
    """
    Cria superfície paramétrica 3D.
    """
    functions_str = f"{request.x_func},{request.y_func},{request.z_func}"
    
    with performance_monitor.measure_calculation("parametric_surface", functions_str):
        # Validar todas as funções paramétricas
        validations = []
        for func_str in [request.x_func, request.y_func, request.z_func]:
            validation = input_validator.validate_function_input(func_str)
            if not validation.is_valid:
                return Visualization3DResponse(
                    sucesso=False,
                    erro=f"Função paramétrica inválida '{func_str}': {', '.join(validation.issues)}"
                )
            validations.append(validation.cleaned_input)
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "parametric_surface", *validations, request.u_min, request.u_max,
            request.v_min, request.v_max, request.resolucao
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(functions_str)
            return cached_result
        
        try:
            result = visualization_3d_service.create_parametric_surface(
                x_func=validations[0],
                y_func=validations[1],
                z_func=validations[2],
                u_range=(request.u_min, request.u_max),
                v_range=(request.v_min, request.v_max),
                resolution=request.resolucao
            )
            
            if result['success']:
                response = Visualization3DResponse(
                    sucesso=True,
                    plotly_json=result['plotly_json'],
                    tipo_grafico=result['plot_type'],
                    info_adicional={
                        'functions': result.get('functions'),
                        'parameters': result.get('parameters'),
                        'resolution': request.resolucao
                    }
                )
            else:
                response = Visualization3DResponse(
                    sucesso=False,
                    erro=result['error']
                )
            
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Erro interno: {str(e)}"
            )

@router.post("/integration-volume", response_model=Visualization3DResponse)
async def criar_volume_integracao(request: IntegrationVolumeRequest):
    """
    Visualiza volume sob uma superfície (integral dupla).
    """
    with performance_monitor.measure_calculation("integration_volume", request.funcao):
        # Validar função
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Validar limites de integração
        if request.x_min >= request.x_max or request.y_min >= request.y_max:
            return Visualization3DResponse(
                sucesso=False,
                erro="Limites de integração inválidos"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "integration_volume", request.funcao, request.x_min, request.x_max,
            request.y_min, request.y_max, request.mostrar_volume, request.resolucao
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            result = visualization_3d_service.create_integration_volume_3d(
                function_str=validation.cleaned_input,
                x_range=(request.x_min, request.x_max),
                y_range=(request.y_min, request.y_max),
                show_volume=request.mostrar_volume,
                resolution=request.resolucao
            )
            
            if result['success']:
                response = Visualization3DResponse(
                    sucesso=True,
                    plotly_json=result['plotly_json'],
                    tipo_grafico=result['plot_type'],
                    funcao=result['function'],
                    info_adicional={
                        'volume_approximation': result.get('volume_approximation'),
                        'integration_bounds': result.get('integration_bounds'),
                        'resolution': request.resolucao
                    }
                )
            else:
                response = Visualization3DResponse(
                    sucesso=False,
                    erro=result['error']
                )
            
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Erro interno: {str(e)}"
            )

@router.post("/gradient-field", response_model=Visualization3DResponse)
async def criar_campo_gradiente(request: GradientFieldRequest):
    """
    Visualiza campo gradiente de uma função escalar.
    """
    with performance_monitor.measure_calculation("gradient_field", request.funcao):
        # Validar função
        validation = input_validator.validate_function_input(request.funcao)
        if not validation.is_valid:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Função inválida: {', '.join(validation.issues)}"
            )
        
        # Verificar cache
        cache_key = cache_manager.generate_cache_key(
            "gradient_field", request.funcao, request.x_min, request.x_max,
            request.y_min, request.y_max, request.densidade
        )
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            performance_monitor.mark_cache_hit(request.funcao)
            return cached_result
        
        try:
            result = visualization_3d_service.create_gradient_field(
                function_str=validation.cleaned_input,
                x_range=(request.x_min, request.x_max),
                y_range=(request.y_min, request.y_max),
                density=request.densidade
            )
            
            if result['success']:
                response = Visualization3DResponse(
                    sucesso=True,
                    plotly_json=result['plotly_json'],
                    tipo_grafico=result['plot_type'],
                    funcao=result['function'],
                    info_adicional={
                        'gradient': result.get('gradient'),
                        'density': request.densidade
                    }
                )
            else:
                response = Visualization3DResponse(
                    sucesso=False,
                    erro=result['error']
                )
            
            cache_manager.set(cache_key, response)
            return response
            
        except Exception as e:
            return Visualization3DResponse(
                sucesso=False,
                erro=f"Erro interno: {str(e)}"
            ) 