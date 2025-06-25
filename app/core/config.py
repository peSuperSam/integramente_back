from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "IntegraMente Backend"
    debug: bool = True
    api_version: str = "v1"
    
    # Configurações matemáticas
    default_resolution: int = 400
    max_resolution: int = 1000
    calculation_timeout: int = 30  # segundos
    
    # Configurações de gráfico
    graph_width: int = 10
    graph_height: int = 6
    graph_dpi: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings() 