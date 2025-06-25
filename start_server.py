#!/usr/bin/env python3
"""
Script para iniciar o servidor IntegraMente
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando servidor IntegraMente Backend...")
    print("📚 Documentação Swagger: http://localhost:8000/docs")
    print("📖 Documentação ReDoc: http://localhost:8000/redoc")
    print("🔍 Health Check: http://localhost:8000/health")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 