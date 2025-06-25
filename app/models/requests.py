from pydantic import BaseModel, Field, validator
from typing import Optional

class AreaRequest(BaseModel):
    funcao: str = Field(..., description="Função matemática em formato string")
    a: float = Field(..., description="Limite inferior de integração")
    b: float = Field(..., description="Limite superior de integração")
    resolucao: Optional[int] = Field(400, description="Resolução do gráfico", ge=50, le=1000)
    
    @validator('funcao')
    def validar_funcao_nao_vazia(cls, v):
        if not v.strip():
            raise ValueError('Função não pode estar vazia')
        return v.strip()

class SimbolicoRequest(BaseModel):
    funcao: str = Field(..., description="Função matemática em formato string")
    a: Optional[float] = Field(None, description="Limite inferior (opcional para integral definida)")
    b: Optional[float] = Field(None, description="Limite superior (opcional para integral definida)")
    mostrar_passos: Optional[bool] = Field(True, description="Incluir passos da resolução")
    formato_latex: Optional[bool] = Field(True, description="Incluir formato LaTeX")
    
    @validator('funcao')
    def validar_funcao_nao_vazia(cls, v):
        if not v.strip():
            raise ValueError('Função não pode estar vazia')
        return v.strip()

class ValidarRequest(BaseModel):
    funcao: str = Field(..., description="Função matemática para validar")
    
    @validator('funcao')
    def validar_funcao_nao_vazia(cls, v):
        if not v.strip():
            raise ValueError('Função não pode estar vazia')
        return v.strip()

class GraficoRequest(BaseModel):
    funcao: str = Field(..., description="Função matemática em formato string")
    a: float = Field(..., description="Limite inferior do intervalo")
    b: float = Field(..., description="Limite superior do intervalo")
    resolucao: Optional[int] = Field(400, description="Resolução do gráfico", ge=50, le=1000)
    
    @validator('funcao')
    def validar_funcao_nao_vazia(cls, v):
        if not v.strip():
            raise ValueError('Função não pode estar vazia')
        return v.strip() 