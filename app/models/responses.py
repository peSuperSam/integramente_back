from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PontoGrafico(BaseModel):
    x: float
    y: float

class AreaResponse(BaseModel):
    sucesso: bool
    valor_integral: Optional[float] = None
    area_total: Optional[float] = None
    erro_estimado: Optional[float] = None
    grafico_base64: Optional[str] = None
    pontos_grafico: Optional[List[PontoGrafico]] = None
    funcao_formatada: Optional[str] = None
    intervalo: Optional[Dict[str, float]] = None
    calculado_em: Optional[str] = None
    erro: Optional[str] = None

class CalculoSimbolicoResponse(BaseModel):
    sucesso: bool
    antiderivada: Optional[str] = None
    antiderivada_latex: Optional[str] = None
    resultado_simbolico: Optional[float] = None
    passos_resolucao: Optional[List[str]] = None
    funcao_original: Optional[str] = None
    calculado_em: Optional[str] = None
    erro: Optional[str] = None

class ValidarResponse(BaseModel):
    valida: bool
    funcao_simplificada: Optional[str] = None
    mensagem: str
    erro: Optional[str] = None

class ExemplosResponse(BaseModel):
    exemplos: Dict[str, List[str]]
    total: int

class CalculoDerivadaResponse(BaseModel):
    sucesso: bool
    derivada: Optional[str] = None
    derivada_latex: Optional[str] = None
    derivada_simplificada: Optional[str] = None
    passos_resolucao: Optional[List[str]] = None
    funcao_original: Optional[str] = None
    tipo_derivada: Optional[str] = None
    calculado_em: Optional[str] = None
    erro: Optional[str] = None

class CalculoLimiteResponse(BaseModel):
    sucesso: bool
    valor_limite: Optional[float] = None
    limite_latex: Optional[str] = None
    tipo_limite: Optional[str] = None
    existe_limite: Optional[bool] = None
    passos_resolucao: Optional[List[str]] = None
    funcao_original: Optional[str] = None
    ponto_limite: Optional[float] = None
    calculado_em: Optional[str] = None
    erro: Optional[str] = None

class GraficoResponse(BaseModel):
    sucesso: bool
    grafico_base64: Optional[str] = None
    pontos_grafico: Optional[List[PontoGrafico]] = None
    erro: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str 