import time
import psutil
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class CalculationMetrics:
    """
    Métricas de um cálculo individual.
    """
    calculation_type: str
    function_expression: str
    execution_time: float
    memory_used: float  # MB
    cache_hit: bool
    precision_score: Optional[float] = None
    error_estimate: Optional[float] = None
    complexity_score: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'calculation_type': self.calculation_type,
            'function_expression': self.function_expression,
            'execution_time': self.execution_time,
            'memory_used': self.memory_used,
            'cache_hit': self.cache_hit,
            'precision_score': self.precision_score,
            'error_estimate': self.error_estimate,
            'complexity_score': self.complexity_score,
            'timestamp': self.timestamp.isoformat()
        }

class PerformanceMonitor:
    """
    Monitor de performance para cálculos matemáticos.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.calculation_history: List[CalculationMetrics] = []
        self.session_stats = {
            'start_time': datetime.now(),
            'total_calculations': 0,
            'total_execution_time': 0.0,
            'cache_hits': 0,
            'errors': 0,
            'precision_issues': 0
        }
        self._lock = threading.Lock()
        
    @contextmanager
    def measure_calculation(self, calculation_type: str, function_expr: str):
        """
        Context manager para medir métricas de cálculo.
        """
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()
        
        try:
            yield self
            
        finally:
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()
            
            execution_time = end_time - start_time
            memory_used = max(0, end_memory - start_memory)
            
            # Criar métricas
            metrics = CalculationMetrics(
                calculation_type=calculation_type,
                function_expression=function_expr,
                execution_time=execution_time,
                memory_used=memory_used,
                cache_hit=False  # Será atualizado externamente
            )
            
            self.add_calculation(metrics)
    
    def add_calculation(self, metrics: CalculationMetrics):
        """
        Adiciona métricas de um cálculo ao histórico.
        """
        with self._lock:
            self.calculation_history.append(metrics)
            
            # Manter apenas os últimos N cálculos
            if len(self.calculation_history) > self.max_history:
                self.calculation_history = self.calculation_history[-self.max_history:]
            
            # Atualizar estatísticas da sessão
            self.session_stats['total_calculations'] += 1
            self.session_stats['total_execution_time'] += metrics.execution_time
            
            if metrics.cache_hit:
                self.session_stats['cache_hits'] += 1
            
            if metrics.error_estimate and metrics.error_estimate > 1e-6:
                self.session_stats['precision_issues'] += 1
    
    def mark_cache_hit(self, function_expr: str):
        """
        Marca o último cálculo como cache hit.
        """
        with self._lock:
            if self.calculation_history:
                last_calc = self.calculation_history[-1]
                if last_calc.function_expression == function_expr:
                    last_calc.cache_hit = True
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo de performance da sessão atual.
        """
        with self._lock:
            if not self.calculation_history:
                return {'message': 'Nenhum cálculo realizado ainda'}
            
            # Calcular estatísticas
            execution_times = [c.execution_time for c in self.calculation_history]
            memory_usage = [c.memory_used for c in self.calculation_history]
            cache_hits = sum(1 for c in self.calculation_history if c.cache_hit)
            
            # Estatísticas por tipo de cálculo
            calc_types = {}
            for calc in self.calculation_history:
                calc_type = calc.calculation_type
                if calc_type not in calc_types:
                    calc_types[calc_type] = {
                        'count': 0,
                        'total_time': 0.0,
                        'avg_time': 0.0,
                        'cache_hits': 0
                    }
                
                calc_types[calc_type]['count'] += 1
                calc_types[calc_type]['total_time'] += calc.execution_time
                calc_types[calc_type]['avg_time'] = (
                    calc_types[calc_type]['total_time'] / calc_types[calc_type]['count']
                )
                
                if calc.cache_hit:
                    calc_types[calc_type]['cache_hits'] += 1
            
            # Performance recente (últimos 10 cálculos)
            recent_calcs = self.calculation_history[-10:]
            recent_avg_time = sum(c.execution_time for c in recent_calcs) / len(recent_calcs)
            
            return {
                'session_duration': str(datetime.now() - self.session_stats['start_time']),
                'total_calculations': len(self.calculation_history),
                'cache_hit_rate': round((cache_hits / len(self.calculation_history)) * 100, 2),
                'average_execution_time': round(sum(execution_times) / len(execution_times), 4),
                'recent_performance': round(recent_avg_time, 4),
                'peak_execution_time': round(max(execution_times), 4),
                'total_memory_used': round(sum(memory_usage), 2),
                'average_memory_per_calc': round(sum(memory_usage) / len(memory_usage), 2),
                'calculations_by_type': calc_types,
                'system_info': self._get_system_info()
            }
    
    def get_precision_analysis(self) -> Dict[str, Any]:
        """
        Análise de precisão dos cálculos.
        """
        with self._lock:
            precision_data = []
            error_estimates = []
            
            for calc in self.calculation_history:
                if calc.precision_score is not None:
                    precision_data.append(calc.precision_score)
                
                if calc.error_estimate is not None:
                    error_estimates.append(calc.error_estimate)
            
            if not precision_data and not error_estimates:
                return {'message': 'Dados de precisão insuficientes'}
            
            analysis = {
                'precision_samples': len(precision_data),
                'error_samples': len(error_estimates)
            }
            
            if precision_data:
                analysis.update({
                    'average_precision': round(sum(precision_data) / len(precision_data), 6),
                    'min_precision': round(min(precision_data), 6),
                    'max_precision': round(max(precision_data), 6)
                })
            
            if error_estimates:
                analysis.update({
                    'average_error': f"{sum(error_estimates) / len(error_estimates):.2e}",
                    'max_error': f"{max(error_estimates):.2e}",
                    'min_error': f"{min(error_estimates):.2e}",
                    'high_error_count': sum(1 for e in error_estimates if e > 1e-6)
                })
            
            return analysis
    
    def get_slowest_calculations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna os cálculos mais lentos.
        """
        with self._lock:
            sorted_calcs = sorted(
                self.calculation_history, 
                key=lambda x: x.execution_time, 
                reverse=True
            )
            
            return [calc.to_dict() for calc in sorted_calcs[:limit]]
    
    def detect_performance_issues(self) -> List[str]:
        """
        Detecta possíveis problemas de performance.
        """
        issues = []
        
        if not self.calculation_history:
            return ['Dados insuficientes para análise']
        
        # Verificar tempo médio de execução
        avg_time = sum(c.execution_time for c in self.calculation_history) / len(self.calculation_history)
        if avg_time > 5.0:  # 5 segundos
            issues.append(f"Tempo médio de execução alto: {avg_time:.2f}s")
        
        # Verificar taxa de cache
        cache_rate = (self.session_stats['cache_hits'] / self.session_stats['total_calculations']) * 100
        if cache_rate < 30:
            issues.append(f"Taxa de cache baixa: {cache_rate:.1f}%")
        
        # Verificar uso de memória
        avg_memory = sum(c.memory_used for c in self.calculation_history) / len(self.calculation_history)
        if avg_memory > 100:  # 100 MB
            issues.append(f"Alto uso de memória por cálculo: {avg_memory:.1f}MB")
        
        # Verificar cálculos muito lentos recentes
        recent_calcs = self.calculation_history[-10:]
        slow_recent = [c for c in recent_calcs if c.execution_time > 10.0]
        if len(slow_recent) > 2:
            issues.append(f"{len(slow_recent)} cálculos lentos recentes (>10s)")
        
        # Verificar problemas de precisão
        precision_issues = sum(1 for c in self.calculation_history 
                             if c.error_estimate and c.error_estimate > 1e-3)
        if precision_issues > len(self.calculation_history) * 0.1:
            issues.append(f"Muitos problemas de precisão detectados: {precision_issues}")
        
        return issues if issues else ['Nenhum problema detectado']
    
    def export_metrics(self, format: str = 'json') -> str:
        """
        Exporta métricas em formato especificado.
        """
        data = {
            'session_stats': self.session_stats.copy(),
            'performance_summary': self.get_performance_summary(),
            'precision_analysis': self.get_precision_analysis(),
            'calculation_history': [calc.to_dict() for calc in self.calculation_history[-50:]]  # Últimos 50
        }
        
        # Converter datetime para string
        data['session_stats']['start_time'] = data['session_stats']['start_time'].isoformat()
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)
    
    def _get_memory_usage(self) -> float:
        """
        Retorna uso atual de memória em MB.
        """
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Converter para MB
        except:
            return 0.0
    
    def _get_system_info(self) -> Dict[str, Any]:
        """
        Informações do sistema para contexto.
        """
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': round(psutil.cpu_percent(interval=0.1), 2),
                'memory_percent': round(psutil.virtual_memory().percent, 2),
                'available_memory_gb': round(psutil.virtual_memory().available / 1024**3, 2)
            }
        except:
            return {'error': 'Não foi possível obter informações do sistema'}
    
    def reset_stats(self):
        """
        Reinicia estatísticas da sessão.
        """
        with self._lock:
            self.calculation_history.clear()
            self.session_stats = {
                'start_time': datetime.now(),
                'total_calculations': 0,
                'total_execution_time': 0.0,
                'cache_hits': 0,
                'errors': 0,
                'precision_issues': 0
            }

# Instância global do monitor
performance_monitor = PerformanceMonitor() 