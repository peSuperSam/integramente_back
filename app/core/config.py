from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "IntegraMente Backend"
    debug: bool = True
    api_version: str = "v1"
    
    # Configurações matemáticas otimizadas
    default_resolution: int = 400
    max_resolution: int = 2000  # Aumentado para maior precisão
    min_resolution: int = 50
    calculation_timeout: int = 45  # Aumentado para cálculos complexos
    
    # Configurações de precisão numérica
    numerical_precision: int = 15  # Dígitos significativos
    integration_method: str = "adaptive"  # adaptive, fixed, romberg
    max_subdivisions: int = 100  # Para integração adaptativa
    
    # Configurações de gráfico otimizadas
    graph_width: int = 12
    graph_height: int = 8
    graph_dpi: int = 150  # Maior DPI para melhor qualidade
    
    # Configurações de cache
    cache_enabled: bool = True
    cache_size: int = 1000
    cache_ttl: int = 3600  # 1 hora
    
    # Configurações de performance
    enable_numba_jit: bool = False  # Desabilitado para Python 3.13
    parallel_processing: bool = True
    max_workers: int = min(4, (os.cpu_count() or 1))
    
    # Limites de segurança
    max_function_complexity: int = 1000  # Número máximo de nós na árvore
    max_calculation_memory: int = 512  # MB
    
    class Config:
        env_file = ".env"

settings = Settings() 