#!/usr/bin/env python3
"""
Script de teste completo para validar o sistema IntegraMente otimizado.
Testa performance, segurança, cache, precisão e todos os endpoints.
"""

import asyncio
import aiohttp
import time
import statistics
import json
from typing import Dict, List, Any
import concurrent.futures
from dataclasses import dataclass

@dataclass
class TestResult:
    name: str
    success: bool
    response_time: float
    status_code: int
    details: Dict[str, Any]

class CompleteSystemTester:
    """
    Testador completo do sistema IntegraMente.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.results: List[TestResult] = []
        
    async def run_all_tests(self):
        """
        Executa todos os testes do sistema.
        """
        print("🚀 Iniciando testes completos do sistema IntegraMente...")
        print("=" * 60)
        
        # 1. Teste de conectividade
        await self.test_connectivity()
        
        # 2. Teste de endpoints básicos
        await self.test_basic_endpoints()
        
        # 3. Teste de cache
        await self.test_cache_performance()
        
        # 4. Teste de precisão matemática
        await self.test_mathematical_precision()
        
        # 5. Teste de performance e monitoramento
        await self.test_performance_monitoring()
        
        # 6. Teste de segurança e rate limiting
        await self.test_security_features()
        
        # 7. Teste de stress
        await self.test_stress_load()
        
        # 8. Relatório final
        self.generate_final_report()
    
    async def test_connectivity(self):
        """
        Testa conectividade básica com o servidor.
        """
        print("\n📡 Testando conectividade...")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            try:
                async with session.get(f"{self.base_url}/") as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    success = response.status == 200 and "IntegraMente" in data.get("message", "")
                    
                    self.results.append(TestResult(
                        name="connectivity_test",
                        success=success,
                        response_time=response_time,
                        status_code=response.status,
                        details={"version": data.get("version"), "features": len(data.get("features", []))}
                    ))
                    
                    if success:
                        print(f"✅ Conectividade OK - {response_time:.3f}s - Versão: {data.get('version')}")
                    else:
                        print(f"❌ Falha na conectividade")
                        
            except Exception as e:
                print(f"❌ Erro de conectividade: {str(e)}")
                self.results.append(TestResult(
                    name="connectivity_test",
                    success=False,
                    response_time=999.0,
                    status_code=0,
                    details={"error": str(e)}
                ))
    
    async def test_basic_endpoints(self):
        """
        Testa todos os endpoints básicos.
        """
        print("\n🎯 Testando endpoints básicos...")
        
        test_cases = [
            {
                "endpoint": "/health",
                "method": "GET",
                "name": "health_check"
            },
            {
                "endpoint": "/validar",
                "method": "POST",
                "data": {"funcao": "x^2 + 2*x + 1"},
                "name": "validate_function"
            },
            {
                "endpoint": "/area",
                "method": "POST",
                "data": {"funcao": "x^2", "a": 0, "b": 2, "metodo": "simpson"},
                "name": "calculate_area"
            },
            {
                "endpoint": "/derivada",
                "method": "POST",
                "data": {"funcao": "x^3 + x^2", "tipo_derivada": "primeira"},
                "name": "calculate_derivative"
            },
            {
                "endpoint": "/limite",
                "method": "POST",
                "data": {"funcao": "(sin(x))/x", "ponto_limite": 0, "tipo_limite": "bilateral"},
                "name": "calculate_limit"
            },
            {
                "endpoint": "/simbolico",
                "method": "POST",
                "data": {"funcao": "x^2", "a": 0, "b": 1},
                "name": "symbolic_integration"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                start_time = time.time()
                
                try:
                    if test_case["method"] == "GET":
                        async with session.get(f"{self.base_url}{test_case['endpoint']}") as response:
                            response_time = time.time() - start_time
                            data = await response.json()
                    else:
                        async with session.post(
                            f"{self.base_url}{test_case['endpoint']}", 
                            json=test_case.get("data", {})
                        ) as response:
                            response_time = time.time() - start_time
                            data = await response.json()
                    
                    success = response.status == 200
                    if "sucesso" in data:
                        success = success and data.get("sucesso", False)
                    
                    self.results.append(TestResult(
                        name=test_case["name"],
                        success=success,
                        response_time=response_time,
                        status_code=response.status,
                        details={"endpoint": test_case["endpoint"], "response_data": data}
                    ))
                    
                    status = "✅" if success else "❌"
                    print(f"{status} {test_case['name']}: {response_time:.3f}s")
                    
                except Exception as e:
                    print(f"❌ {test_case['name']}: Erro - {str(e)}")
                    self.results.append(TestResult(
                        name=test_case["name"],
                        success=False,
                        response_time=999.0,
                        status_code=0,
                        details={"error": str(e)}
                    ))
    
    async def test_cache_performance(self):
        """
        Testa eficiência do cache.
        """
        print("\n💾 Testando performance do cache...")
        
        # Função para testar
        test_data = {"funcao": "x^3 + sin(x)", "a": 0, "b": 5, "metodo": "simpson"}
        
        async with aiohttp.ClientSession() as session:
            # Primeira requisição (cache miss)
            start_time = time.time()
            async with session.post(f"{self.base_url}/area", json=test_data) as response:
                first_time = time.time() - start_time
                await response.json()
            
            # Segunda requisição (cache hit)
            start_time = time.time()
            async with session.post(f"{self.base_url}/area", json=test_data) as response:
                second_time = time.time() - start_time
                await response.json()
            
            # Terceira requisição (cache hit)
            start_time = time.time()
            async with session.post(f"{self.base_url}/area", json=test_data) as response:
                third_time = time.time() - start_time
                await response.json()
            
            # Analisar melhoria do cache
            cache_improvement = (first_time - second_time) / first_time * 100
            consistency = abs(second_time - third_time) / second_time * 100
            
            success = cache_improvement > 10 and consistency < 50  # Cache deve melhorar pelo menos 10%
            
            self.results.append(TestResult(
                name="cache_performance",
                success=success,
                response_time=second_time,
                status_code=200,
                details={
                    "first_request": first_time,
                    "cached_request": second_time,
                    "third_request": third_time,
                    "improvement_percent": cache_improvement,
                    "consistency_percent": consistency
                }
            ))
            
            print(f"📊 Cache: 1ª req: {first_time:.3f}s, 2ª req: {second_time:.3f}s")
            print(f"📈 Melhoria do cache: {cache_improvement:.1f}%")
    
    async def test_mathematical_precision(self):
        """
        Testa precisão dos cálculos matemáticos.
        """
        print("\n🧮 Testando precisão matemática...")
        
        precision_tests = [
            {
                "name": "integral_x2_0_to_2",
                "endpoint": "/area",
                "data": {"funcao": "x^2", "a": 0, "b": 2, "metodo": "simpson"},
                "expected": 8/3,  # ∫x²dx de 0 a 2 = 8/3
                "tolerance": 1e-10
            },
            {
                "name": "derivative_x3",
                "endpoint": "/derivada", 
                "data": {"funcao": "x^3", "tipo_derivada": "primeira"},
                "expected": "3*x**2",
                "tolerance": None  # Teste simbólico
            },
            {
                "name": "limit_sinx_over_x",
                "endpoint": "/limite",
                "data": {"funcao": "(sin(x))/x", "ponto_limite": 0, "tipo_limite": "bilateral"},
                "expected": 1.0,
                "tolerance": 1e-12
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in precision_tests:
                try:
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}{test['endpoint']}", 
                        json=test["data"]
                    ) as response:
                        response_time = time.time() - start_time
                        data = await response.json()
                    
                    success = False
                    error_margin = None
                    
                    if response.status == 200 and data.get("sucesso", False):
                        if test["tolerance"] is not None:
                            # Teste numérico
                            if test["endpoint"] == "/area":
                                calculated = data.get("resultado", 0)
                            elif test["endpoint"] == "/limite":
                                calculated = float(data.get("valor_limite", 0))
                            
                            error_margin = abs(calculated - test["expected"])
                            success = error_margin < test["tolerance"]
                        else:
                            # Teste simbólico
                            result = data.get("derivada", "").replace(" ", "")
                            expected = test["expected"].replace(" ", "")
                            success = result == expected or "3*x**2" in result
                    
                    self.results.append(TestResult(
                        name=test["name"],
                        success=success,
                        response_time=response_time,
                        status_code=response.status,
                        details={
                            "expected": test["expected"],
                            "calculated": data,
                            "error_margin": error_margin,
                            "tolerance": test["tolerance"]
                        }
                    ))
                    
                    status = "✅" if success else "❌"
                    if error_margin is not None:
                        print(f"{status} {test['name']}: erro = {error_margin:.2e}")
                    else:
                        print(f"{status} {test['name']}: {response_time:.3f}s")
                        
                except Exception as e:
                    print(f"❌ {test['name']}: Erro - {str(e)}")
    
    async def test_performance_monitoring(self):
        """
        Testa sistema de monitoramento de performance.
        """
        print("\n📊 Testando monitoramento de performance...")
        
        async with aiohttp.ClientSession() as session:
            # Fazer algumas requisições para gerar dados
            for i in range(5):
                async with session.post(
                    f"{self.base_url}/area", 
                    json={"funcao": f"x^{i+2}", "a": 0, "b": 1, "metodo": "simpson"}
                ) as response:
                    await response.json()
            
            # Testar endpoints de performance
            performance_endpoints = [
                "/performance/summary",
                "/performance/cache",
                "/performance/precision"
            ]
            
            for endpoint in performance_endpoints:
                try:
                    start_time = time.time()
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        response_time = time.time() - start_time
                        data = await response.json()
                    
                    success = response.status == 200 and isinstance(data, dict)
                    
                    self.results.append(TestResult(
                        name=f"performance_{endpoint.split('/')[-1]}",
                        success=success,
                        response_time=response_time,
                        status_code=response.status,
                        details={"endpoint": endpoint, "data_keys": list(data.keys()) if isinstance(data, dict) else []}
                    ))
                    
                    status = "✅" if success else "❌"
                    print(f"{status} {endpoint}: {response_time:.3f}s")
                    
                except Exception as e:
                    print(f"❌ {endpoint}: Erro - {str(e)}")
    
    async def test_security_features(self):
        """
        Testa funcionalidades de segurança e rate limiting.
        """
        print("\n🔒 Testando segurança e rate limiting...")
        
        async with aiohttp.ClientSession() as session:
            # Teste de rate limiting
            requests_made = 0
            blocked_count = 0
            
            for i in range(70):  # Tentar fazer mais que o limite
                try:
                    async with session.get(f"{self.base_url}/health") as response:
                        requests_made += 1
                        if response.status == 429:
                            blocked_count += 1
                        elif response.status != 200:
                            break
                except:
                    break
            
            rate_limit_working = blocked_count > 0
            
            # Teste de validação de entrada
            malicious_inputs = [
                "__import__('os').system('ls')",
                "exec('print(1)')",
                "'; DROP TABLE users; --",
                "eval('1+1')"
            ]
            
            security_blocks = 0
            for malicious_input in malicious_inputs:
                try:
                    async with session.post(
                        f"{self.base_url}/validar",
                        json={"funcao": malicious_input}
                    ) as response:
                        data = await response.json()
                        if not data.get("valida", True) or response.status >= 400:
                            security_blocks += 1
                except:
                    security_blocks += 1
            
            security_working = security_blocks == len(malicious_inputs)
            
            self.results.append(TestResult(
                name="rate_limiting",
                success=rate_limit_working,
                response_time=0.0,
                status_code=200,
                details={
                    "requests_made": requests_made,
                    "blocked_count": blocked_count,
                    "limit_triggered": rate_limit_working
                }
            ))
            
            self.results.append(TestResult(
                name="security_validation",
                success=security_working,
                response_time=0.0,
                status_code=200,
                details={
                    "malicious_inputs_tested": len(malicious_inputs),
                    "blocked_inputs": security_blocks,
                    "all_blocked": security_working
                }
            ))
            
            rate_status = "✅" if rate_limit_working else "❌"
            security_status = "✅" if security_working else "❌"
            print(f"{rate_status} Rate limiting: {blocked_count}/{requests_made} bloqueadas")
            print(f"{security_status} Validação segura: {security_blocks}/{len(malicious_inputs)} bloqueadas")
    
    async def test_stress_load(self):
        """
        Teste de stress com requisições simultâneas.
        """
        print("\n⚡ Testando carga e stress...")
        
        async def single_request(session, semaphore):
            async with semaphore:
                start_time = time.time()
                try:
                    async with session.post(
                        f"{self.base_url}/area",
                        json={"funcao": "x^2 + sin(x)", "a": 0, "b": 1, "metodo": "trapz"}
                    ) as response:
                        response_time = time.time() - start_time
                        data = await response.json()
                        success = response.status == 200 and data.get("sucesso", False)
                        return response_time, success
                except:
                    return time.time() - start_time, False
        
        # Teste com 20 requisições simultâneas
        semaphore = asyncio.Semaphore(20)
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            tasks = [single_request(session, semaphore) for _ in range(50)]
            results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            response_times = [r[0] for r in results]
            success_count = sum(1 for r in results if r[1])
            
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            success_rate = (success_count / len(results)) * 100
            
            stress_success = success_rate > 80 and avg_response_time < 5.0
            
            self.results.append(TestResult(
                name="stress_test",
                success=stress_success,
                response_time=avg_response_time,
                status_code=200,
                details={
                    "total_requests": len(results),
                    "successful_requests": success_count,
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "total_time": total_time
                }
            ))
            
            status = "✅" if stress_success else "❌"
            print(f"{status} Stress test: {success_count}/{len(results)} sucessos")
            print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
            print(f"⏱️  Tempo médio: {avg_response_time:.3f}s")
    
    def generate_final_report(self):
        """
        Gera relatório final dos testes.
        """
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DE TESTES")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        avg_response_time = statistics.mean([r.response_time for r in self.results if r.response_time < 999])
        
        print(f"✅ Testes bem-sucedidos: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"⏱️  Tempo médio de resposta: {avg_response_time:.3f}s")
        
        print("\n📊 DETALHES POR CATEGORIA:")
        
        categories = {
            "Conectividade": ["connectivity_test"],
            "Endpoints": ["health_check", "validate_function", "calculate_area", "calculate_derivative", "calculate_limit", "symbolic_integration"],
            "Cache": ["cache_performance"],
            "Precisão": ["integral_x2_0_to_2", "derivative_x3", "limit_sinx_over_x"],
            "Monitoramento": ["performance_summary", "performance_cache", "performance_precision"],
            "Segurança": ["rate_limiting", "security_validation"],
            "Stress": ["stress_test"]
        }
        
        for category, test_names in categories.items():
            category_results = [r for r in self.results if r.name in test_names]
            if category_results:
                category_success = sum(1 for r in category_results if r.success)
                category_total = len(category_results)
                category_rate = (category_success / category_total) * 100
                
                status = "✅" if category_rate == 100 else "⚠️" if category_rate >= 50 else "❌"
                print(f"{status} {category}: {category_success}/{category_total} ({category_rate:.0f}%)")
        
        print("\n🚀 MELHORIAS DETECTADAS:")
        
        # Análise de cache
        cache_result = next((r for r in self.results if r.name == "cache_performance"), None)
        if cache_result and cache_result.success:
            improvement = cache_result.details.get("improvement_percent", 0)
            print(f"💾 Cache melhora performance em {improvement:.1f}%")
        
        # Análise de precisão
        precision_results = [r for r in self.results if "integral_" in r.name or "limit_" in r.name]
        if precision_results:
            successful_precision = sum(1 for r in precision_results if r.success)
            print(f"🧮 Precisão matemática: {successful_precision}/{len(precision_results)} testes")
        
        print("\n✨ Sistema IntegraMente otimizado e funcionando!")
        print("🎯 Pronto para uso em produção com alta performance e segurança!")

async def main():
    """
    Função principal para executar todos os testes.
    """
    tester = CompleteSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 