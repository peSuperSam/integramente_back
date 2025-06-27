import hashlib
import pickle
from typing import Any, Optional, Callable
from cachetools import TTLCache
from functools import wraps
import sympy as sp
import time
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gerenciador de cache inteligente para cálculos matemáticos.
    """
    
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        # Cache em memória com TTL (Time To Live)
        self.memory_cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.hit_count = 0
        self.miss_count = 0
        
    def generate_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """
        Gera uma chave única baseada na função e parâmetros.
        """
        # Serializar argumentos de forma consistente
        cache_data = {
            'function': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        
        # Criar hash MD5 da representação dos dados
        cache_str = str(cache_data)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera valor do cache.
        """
        if key in self.memory_cache:
            self.hit_count += 1
            logger.debug(f"Cache HIT para chave: {key[:8]}...")
            return self.memory_cache[key]
        
        self.miss_count += 1
        logger.debug(f"Cache MISS para chave: {key[:8]}...")
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Armazena valor no cache.
        """
        self.memory_cache[key] = value
        logger.debug(f"Cache SET para chave: {key[:8]}...")
    
    def get_stats(self) -> dict:
        """
        Retorna estatísticas do cache.
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.memory_cache),
            'max_size': self.memory_cache.maxsize,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def clear(self) -> None:
        """
        Limpa o cache.
        """
        self.memory_cache.clear()
        self.hit_count = 0
        self.miss_count = 0

# Instância global do cache
cache_manager = CacheManager()

def cached_calculation(cache_key_func: Optional[Callable] = None):
    """
    Decorator para cache automático de cálculos matemáticos.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = cache_manager.generate_cache_key(func.__name__, *args, **kwargs)
            
            # Tentar recuperar do cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Só cachear se não houver erro e execução foi rápida (< 10s)
            if execution_time < 10 and result is not None:
                cache_manager.set(cache_key, result)
            
            logger.debug(f"Função {func.__name__} executada em {execution_time:.4f}s")
            return result
        
        return wrapper
    return decorator

def expression_cache_key(expr_str: str, *args, **kwargs) -> str:
    """
    Gera chave de cache específica para expressões matemáticas.
    """
    # Normalizar expressão (remover espaços, padronizar formato)
    normalized_expr = expr_str.replace(' ', '').replace('^', '**').lower()
    
    cache_data = {
        'expression': normalized_expr,
        'args': args,
        'kwargs': sorted(kwargs.items()) if kwargs else {}
    }
    
    return hashlib.md5(str(cache_data).encode()).hexdigest() 