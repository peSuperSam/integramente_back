from fastapi import APIRouter, Query
from typing import Optional
from app.core.performance_monitor import performance_monitor
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.get("/performance/summary")
async def get_performance_summary():
    """
    Retorna resumo de performance da sessão atual.
    """
    return {
        "performance": performance_monitor.get_performance_summary(),
        "cache_stats": cache_manager.get_stats()
    }

@router.get("/performance/precision")
async def get_precision_analysis():
    """
    Análise detalhada de precisão dos cálculos.
    """
    return performance_monitor.get_precision_analysis()

@router.get("/performance/slowest")
async def get_slowest_calculations(limit: int = Query(5, ge=1, le=20)):
    """
    Retorna os cálculos mais lentos registrados.
    """
    return {
        "slowest_calculations": performance_monitor.get_slowest_calculations(limit)
    }

@router.get("/performance/issues")
async def detect_performance_issues():
    """
    Detecta possíveis problemas de performance.
    """
    return {
        "issues": performance_monitor.detect_performance_issues(),
        "recommendations": _get_performance_recommendations()
    }

@router.get("/performance/export")
async def export_performance_metrics(format: str = Query("json", regex="^(json)$")):
    """
    Exporta métricas de performance.
    """
    return {
        "metrics": performance_monitor.export_metrics(format)
    }

@router.post("/performance/reset")
async def reset_performance_stats():
    """
    Reinicia estatísticas de performance.
    """
    performance_monitor.reset_stats()
    cache_manager.clear()
    
    return {
        "message": "Estatísticas de performance reiniciadas",
        "timestamp": performance_monitor.session_stats['start_time'].isoformat()
    }

@router.get("/performance/cache")
async def get_cache_details():
    """
    Detalhes específicos do cache.
    """
    stats = cache_manager.get_stats()
    
    # Calcular eficiência do cache
    efficiency_score = "N/A"
    if stats['total_requests'] > 0:
        efficiency = stats['hit_rate']
        if efficiency >= 80:
            efficiency_score = "Excelente"
        elif efficiency >= 60:
            efficiency_score = "Boa"
        elif efficiency >= 40:
            efficiency_score = "Regular"
        else:
            efficiency_score = "Baixa"
    
    return {
        "cache_stats": stats,
        "efficiency_score": efficiency_score,
        "recommendations": _get_cache_recommendations(stats)
    }

def _get_performance_recommendations() -> list:
    """
    Gera recomendações baseadas na performance atual.
    """
    recommendations = []
    issues = performance_monitor.detect_performance_issues()
    
    for issue in issues:
        if "tempo médio alto" in issue.lower():
            recommendations.append("Considere ativar cache para funções repetidas")
            recommendations.append("Verifique a complexidade das funções sendo calculadas")
            
        elif "cache baixa" in issue.lower():
            recommendations.append("Aumente o TTL do cache se apropriado")
            recommendations.append("Revise estratégia de cache para padrões de uso")
            
        elif "memória" in issue.lower():
            recommendations.append("Monitore vazamentos de memória")
            recommendations.append("Considere limitar resolução de gráficos")
            
        elif "precisão" in issue.lower():
            recommendations.append("Aumente precisão numérica para cálculos críticos")
            recommendations.append("Use métodos de integração mais robustos")
    
    if not recommendations:
        recommendations.append("Performance está dentro dos parâmetros normais")
    
    return recommendations

def _get_cache_recommendations(stats: dict) -> list:
    """
    Recomendações específicas para cache.
    """
    recommendations = []
    
    if stats['hit_rate'] < 30:
        recommendations.append("Taxa de cache muito baixa - verifique padrões de uso")
        recommendations.append("Considere aumentar tamanho do cache")
    
    elif stats['hit_rate'] < 60:
        recommendations.append("Taxa de cache pode ser melhorada")
        recommendations.append("Analise quais funções são mais utilizadas")
    
    cache_usage = (stats['cache_size'] / stats['max_size']) * 100
    
    if cache_usage > 90:
        recommendations.append("Cache quase cheio - considere aumentar tamanho")
    elif cache_usage < 20:
        recommendations.append("Cache subutilizado - pode reduzir tamanho")
    
    if not recommendations:
        recommendations.append("Cache funcionando eficientemente")
    
    return recommendations 