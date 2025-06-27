import logging
import logging.handlers
import os
from datetime import datetime
import sys

def setup_logging(debug: bool = True, log_file: str = None):
    """
    Configura sistema de logging para o backend.
    """
    # Configurar nível base
    level = logging.DEBUG if debug else logging.INFO
    
    # Formato de log detalhado
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Handler para arquivo (se especificado)
    file_handler = None
    if log_file:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Usar rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpar handlers existentes
    root_logger.handlers.clear()
    
    # Adicionar handlers
    root_logger.addHandler(console_handler)
    if file_handler:
        root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    loggers_config = {
        'app.services.enhanced_math_service': logging.INFO,
        'app.core.cache_manager': logging.INFO,
        'app.core.performance_monitor': logging.INFO,
        'uvicorn.access': logging.WARNING,
        'matplotlib': logging.WARNING,
        'numba': logging.WARNING
    }
    
    for logger_name, logger_level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)
    
    # Log inicial
    logging.info("Sistema de logging configurado")
    logging.info(f"Nível de log: {level}")
    if log_file:
        logging.info(f"Arquivo de log: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """
    Retorna logger configurado para um módulo específico.
    """
    return logging.getLogger(name) 