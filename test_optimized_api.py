#!/usr/bin/env python3
"""
Script de teste para validar otimizações do backend IntegraMente
"""

import requests
import json
import time
from datetime import datetime
import statistics

BASE_URL = "http://localhost:8000"

def test_performance_monitoring():
    """Testa o sistema de monitoramento de performance"""
    print("🔍 Testando Sistema de Monitoramento...")
    
    try:
        response = requests.get(f"{BASE_URL}/performance/summary")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📊 Resumo de Performance:")
            performance = data.get('performance', {})
            cache_stats = data.get('cache_stats', {})
            
            print(f"  • Total de cálculos: {performance.get('total_calculations', 0)}")
            print(f"  • Taxa de cache: {cache_stats.get('hit_rate', 0)}%")
            print(f"  • Tempo médio: {performance.get('average_execution_time', 0):.4f}s")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_cache_efficiency():
    """Testa a eficiência do cache"""
    print("\n🔍 Testando Eficiência do Cache...")
    
    # Função para testar
    test_function = "x^2 + 2*x + 1"
    
    # Primeira chamada (cache miss)
    start_time = time.time()
    response1 = requests.post(f"{BASE_URL}/area", json={
        "funcao": test_function,
        "a": -1,
        "b": 1,
        "resolucao": 200
    })
    first_call_time = time.time() - start_time
    
    # Segunda chamada (cache hit esperado)
    start_time = time.time()
    response2 = requests.post(f"{BASE_URL}/area", json={
        "funcao": test_function,
        "a": -1,
        "b": 1,
        "resolucao": 200
    })
    second_call_time = time.time() - start_time
    
    if response1.status_code == 200 and response2.status_code == 200:
        speedup = first_call_time / second_call_time if second_call_time > 0 else 1
        print(f"  • Primeira chamada: {first_call_time:.4f}s")
        print(f"  • Segunda chamada: {second_call_time:.4f}s")
        print(f"  • Speedup do cache: {speedup:.2f}x")
        
        return speedup > 1.5  # Cache deve acelerar significativamente
    
    return False

def test_precision_improvements():
    """Testa melhorias de precisão"""
    print("\n🔍 Testando Melhorias de Precisão...")
    
    # Teste com função que requer alta precisão
    functions_to_test = [
        "sin(x)",
        "exp(x)",
        "1/(1+x^2)",
        "x^3 - 2*x^2 + x - 1"
    ]
    
    precision_results = []
    
    for func in functions_to_test:
        try:
            response = requests.post(f"{BASE_URL}/area", json={
                "funcao": func,
                "a": 0,
                "b": 1,
                "resolucao": 500
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('sucesso'):
                    erro_estimado = data.get('erro_estimado', 1e-3)
                    precision_results.append(erro_estimado)
                    print(f"  • {func}: erro estimado = {erro_estimado:.2e}")
        
        except Exception as e:
            print(f"  • Erro testando {func}: {e}")
    
    if precision_results:
        avg_error = statistics.mean(precision_results)
        print(f"  • Erro médio: {avg_error:.2e}")
        return avg_error < 1e-6  # Erro deve ser muito baixo
    
    return False

def test_complex_calculations():
    """Testa cálculos complexos"""
    print("\n🔍 Testando Cálculos Complexos...")
    
    complex_tests = [
        {
            'type': 'derivada',
            'endpoint': '/derivada',
            'data': {
                'funcao': 'x^4 - 3*x^3 + 2*x^2 - x + 5',
                'tipo_derivada': 'segunda',
                'mostrar_passos': True
            }
        },
        {
            'type': 'limite',
            'endpoint': '/limite',
            'data': {
                'funcao': '(sin(x))/x',
                'ponto_limite': 0,
                'tipo_limite': 'bilateral'
            }
        },
        {
            'type': 'simbolico',
            'endpoint': '/simbolico',
            'data': {
                'funcao': 'x*exp(x)',
                'mostrar_passos': True
            }
        }
    ]
    
    success_count = 0
    
    for test in complex_tests:
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test['data'])
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('sucesso'):
                    success_count += 1
                    print(f"  • {test['type']}: ✅ ({execution_time:.3f}s)")
                else:
                    print(f"  • {test['type']}: ❌ {data.get('erro', 'Erro desconhecido')}")
            else:
                print(f"  • {test['type']}: ❌ Status {response.status_code}")
                
        except Exception as e:
            print(f"  • {test['type']}: ❌ Exceção: {e}")
    
    success_rate = (success_count / len(complex_tests)) * 100
    print(f"  • Taxa de sucesso: {success_rate:.1f}%")
    
    return success_rate >= 80

def test_performance_analysis():
    """Testa análise de performance"""
    print("\n🔍 Testando Análise de Performance...")
    
    try:
        # Fazer algumas chamadas para gerar dados
        for i in range(5):
            requests.post(f"{BASE_URL}/area", json={
                "funcao": f"x^{i+1}",
                "a": 0,
                "b": 1,
                "resolucao": 100
            })
        
        # Testar endpoints de análise
        endpoints_to_test = [
            "/performance/precision",
            "/performance/slowest",
            "/performance/issues",
            "/performance/cache"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                results[endpoint] = response.json()
                print(f"  • {endpoint}: ✅")
            else:
                print(f"  • {endpoint}: ❌ Status {response.status_code}")
        
        # Verificar se detectou algum problema ou recomendação
        issues_response = results.get("/performance/issues", {})
        if issues_response:
            issues = issues_response.get("issues", [])
            recommendations = issues_response.get("recommendations", [])
            print(f"  • Problemas detectados: {len(issues)}")
            print(f"  • Recomendações: {len(recommendations)}")
        
        return len(results) >= 3
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def benchmark_comparison():
    """Comparação de benchmark com múltiplas funções"""
    print("\n🔍 Benchmark de Performance...")
    
    test_functions = [
        "x^2",
        "sin(x) + cos(x)",
        "exp(-x^2)",
        "log(1+x^2)",
        "x^3 - 2*x^2 + x"
    ]
    
    times = []
    
    for func in test_functions:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/area", json={
            "funcao": func,
            "a": -2,
            "b": 2,
            "resolucao": 400
        })
        
        execution_time = time.time() - start_time
        times.append(execution_time)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('sucesso'):
                print(f"  • {func}: {execution_time:.3f}s ✅")
            else:
                print(f"  • {func}: {execution_time:.3f}s ❌")
        else:
            print(f"  • {func}: {execution_time:.3f}s ❌ Status {response.status_code}")
    
    if times:
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\n📊 Estatísticas do Benchmark:")
        print(f"  • Tempo médio: {avg_time:.3f}s")
        print(f"  • Tempo máximo: {max_time:.3f}s")
        print(f"  • Tempo mínimo: {min_time:.3f}s")
        
        return avg_time < 2.0  # Tempo médio deve ser razoável
    
    return False

def main():
    """Executa todos os testes de otimização"""
    print("🚀 Iniciando Testes de Otimização do IntegraMente Backend")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Monitoramento de Performance", test_performance_monitoring),
        ("Eficiência do Cache", test_cache_efficiency),
        ("Melhorias de Precisão", test_precision_improvements),
        ("Cálculos Complexos", test_complex_calculations),
        ("Análise de Performance", test_performance_analysis),
        ("Benchmark Comparativo", benchmark_comparison)
    ]
    
    results = []
    start_total = time.time()
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
            results.append((test_name, False))
    
    total_time = time.time() - start_total
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES DE OTIMIZAÇÃO")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<30} {status}")
    
    print(f"\n📈 Taxa de Sucesso: {success_rate:.1f}% ({passed}/{total})")
    print(f"⏱️  Tempo Total: {total_time:.2f}s")
    
    if success_rate >= 80:
        print("\n🎉 OTIMIZAÇÕES FUNCIONANDO CORRETAMENTE!")
    else:
        print("\n⚠️  ALGUMAS OTIMIZAÇÕES PRECISAM DE ATENÇÃO")
    
    # Obter estatísticas finais de performance
    try:
        response = requests.get(f"{BASE_URL}/performance/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Estatísticas da Sessão:")
            perf = data.get('performance', {})
            cache = data.get('cache_stats', {})
            
            print(f"  • Cálculos realizados: {perf.get('total_calculations', 0)}")
            print(f"  • Taxa de cache: {cache.get('hit_rate', 0):.1f}%")
            print(f"  • Tempo médio: {perf.get('average_execution_time', 0):.4f}s")
    except:
        pass

if __name__ == "__main__":
    main() 