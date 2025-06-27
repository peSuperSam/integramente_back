from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import os

from app.routers import health, area, simbolico, derivada, limite, validar, exemplos, grafico
from app.core.config import settings

app = FastAPI(
    title="IntegraMente Backend API",
    description="Backend matemático para cálculos simbólicos, numéricos e gráficos",
    version="1.0.0"
)

# Configuração CORS para Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router)
app.include_router(area.router)
app.include_router(simbolico.router)
app.include_router(derivada.router)
app.include_router(limite.router)
app.include_router(validar.router)
app.include_router(exemplos.router)
app.include_router(grafico.router)

# Root endpoint para verificação rápida
@app.get("/")
async def root():
    return {
        "message": "IntegraMente Backend API está funcionando!",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/health",
            "/area",
            "/simbolico",
            "/derivada",
            "/limite",
            "/validar",
            "/exemplos",
            "/grafico"
        ]
    }

if __name__ == "__main__":
    # Usar PORT do ambiente (para Render, Railway, etc.) ou 8000 como fallback
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Desabilitar reload em produção
    ) 