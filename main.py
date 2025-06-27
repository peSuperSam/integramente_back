from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import os

from app.routers import health, area, simbolico, derivada, limite, validar, exemplos, grafico, performance, visualization_3d, ml_predictions
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.security_middleware import security_middleware

# Configurar logging
setup_logging(debug=settings.debug, log_file="logs/integramente.log" if not settings.debug else None)

app = FastAPI(
    title="IntegraMente Backend API Otimizado",
    description="Backend matemático avançado com cache, monitoramento, alta precisão e segurança",
    version="2.0.0"
)

# Configuração CORS para Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middleware de segurança
app.middleware("http")(security_middleware)

# Incluir routers
app.include_router(health.router)
app.include_router(area.router)
app.include_router(simbolico.router)
app.include_router(derivada.router)
app.include_router(limite.router)
app.include_router(validar.router)
app.include_router(exemplos.router)
app.include_router(grafico.router)
app.include_router(performance.router)
app.include_router(visualization_3d.router)
app.include_router(ml_predictions.router)

# Root endpoint para verificação rápida
@app.get("/")
async def root():
    return {
        "message": "IntegraMente Backend API está funcionando!",
        "version": "2.0.0",
        "status": "online",
        "features": [
            "Cálculos de alta precisão",
            "Cache inteligente",
            "Monitoramento de performance", 
            "Rate limiting",
            "Análise de segurança",
            "Validação avançada"
        ],
        "endpoints": [
            "/health",
            "/area",
            "/simbolico", 
            "/derivada",
            "/limite",
            "/validar",
            "/exemplos",
            "/grafico",
            "/performance",
            "/3d",
            "/ml"
        ]
    }

# Endpoint de estatísticas de segurança (admin only)
@app.get("/security/stats")
async def get_security_stats():
    return security_middleware.get_security_stats()

if __name__ == "__main__":
    # Usar PORT do ambiente (para Render, Railway, etc.) ou 8000 como fallback
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Desabilitar reload em produção
    ) 