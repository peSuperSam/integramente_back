#!/usr/bin/env python3
"""
Script de teste para validar os endpoints da API IntegraMente
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Testa o endpoint de health check"""
    print("🔍 Testando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_validar():
    """Testa o endpoint de validação"""
    print("\n🔍 Testando Validação de Função...")
    
    # Teste função válida
    data = {"funcao": "x^2 + 3*x"}
    try:
        response = requests.post(f"{BASE_URL}/validar", json=data)
        print(f"Status: {response.status_code}")
        print(f"Função válida - Resposta: {response.json()}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste função inválida
    data = {"funcao": "x^&invalid"}
    try:
        response = requests.post(f"{BASE_URL}/validar", json=data)
        print(f"Função inválida - Resposta: {response.json()}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_exemplos():
    """Testa o endpoint de exemplos"""
    print("\n🔍 Testando Exemplos...")
    try:
        response = requests.get(f"{BASE_URL}/exemplos")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total de exemplos: {data['total']}")
        print(f"Categorias: {list(data['exemplos'].keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_simbolico():
    """Testa o endpoint de cálculo simbólico"""
    print("\n🔍 Testando Cálculo Simbólico...")
    
    # Integral indefinida
    data = {
        "funcao": "x^2",
        "mostrar_passos": True,
        "formato_latex": True
    }
    try:
        response = requests.post(f"{BASE_URL}/simbolico", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        if result.get("sucesso"):
            print(f"Antiderivada: {result.get('antiderivada')}")
            print(f"LaTeX: {result.get('antiderivada_latex')}")
        else:
            print(f"Erro: {result.get('erro')}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_area():
    """Testa o endpoint de cálculo de área"""
    print("\n🔍 Testando Cálculo de Área...")
    
    data = {
        "funcao": "x^2",
        "a": -2,
        "b": 2,
        "resolucao": 100  # Resolução menor para teste
    }
    try:
        response = requests.post(f"{BASE_URL}/area", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        if result.get("sucesso"):
            print(f"Valor da integral: {result.get('valor_integral')}")
            print(f"Área total: {result.get('area_total')}")
            print(f"Erro estimado: {result.get('erro_estimado')}")
            print(f"Gráfico gerado: {'Sim' if result.get('grafico_base64') else 'Não'}")
        else:
            print(f"Erro: {result.get('erro')}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API IntegraMente")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Lista de testes
    tests = [
        test_health,
        test_exemplos,
        test_validar,
        test_simbolico,
        test_area
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro no teste {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Resumo dos Testes:")
    successful = sum(1 for r in results if r is not False)
    print(f"✅ Sucessos: {successful}/{len(tests)}")
    
    if all(r is not False for r in results):
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main() 