#!/usr/bin/env python3
"""
Script para testar se o backend está pronto para deploy
"""
import sys
import subprocess
import requests
import time

def test_requirements():
    """Testa se todas as dependências estão instaladas"""
    print("🔍 Testando dependências...")
    try:
        import fastapi
        import uvicorn
        import sympy
        import scipy
        import numpy
        import matplotlib
        import pydantic
        print("✅ Todas as dependências estão instaladas!")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🔍 Testando imports...")
    try:
        from app.routers import health, area, simbolico, validar, exemplos, grafico
        from app.core.config import settings
        print("✅ Todos os módulos podem ser importados!")
        return True
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False

def start_server():
    """Inicia o servidor para teste"""
    print("🚀 Iniciando servidor de teste...")
    import subprocess
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

def test_endpoints():
    """Testa os endpoints principais"""
    print("🔍 Testando endpoints...")
    base_url = "http://localhost:8000"
    
    # Aguarda servidor inicializar
    time.sleep(3)
    
    endpoints_to_test = [
        "/",
        "/health",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Erro: {e}")
            return False
    
    # Teste específico do cálculo de área
    try:
        response = requests.post(
            f"{base_url}/area",
            json={"funcao": "x^2", "a": -1, "b": 1, "resolucao": 100},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("sucesso"):
                print("✅ Cálculo de área - OK")
            else:
                print(f"❌ Cálculo de área - Erro: {data.get('erro')}")
                return False
        else:
            print(f"❌ Cálculo de área - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cálculo de área - Erro: {e}")
        return False
    
    return True

def main():
    print("🔧 TESTE DE PRONTIDÃO PARA DEPLOY")
    print("=" * 40)
    
    # Teste 1: Dependências
    if not test_requirements():
        print("\n❌ Execute: pip install -r requirements.txt")
        return False
    
    # Teste 2: Imports
    if not test_imports():
        print("\n❌ Verifique se todos os arquivos estão no lugar correto")
        return False
    
    # Teste 3: Servidor e endpoints
    server_process = None
    try:
        server_process = start_server()
        if not test_endpoints():
            print("\n❌ Alguns endpoints não estão funcionando")
            return False
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
    
    print("\n🎉 TUDO PRONTO PARA DEPLOY!")
    print("Agora você pode:")
    print("1. Commitar o código no GitHub")
    print("2. Fazer deploy no Render/Railway")
    print("3. Atualizar a URL no Flutter")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 