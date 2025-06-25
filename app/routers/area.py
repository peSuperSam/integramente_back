from fastapi import APIRouter, HTTPException
from app.models.requests import AreaRequest
from app.models.responses import AreaResponse
from app.services.math_service import MathService

router = APIRouter()

@router.post("/area", response_model=AreaResponse)
async def calcular_area(request: AreaRequest):
    """
    Calcula a área sob a curva de uma função em um intervalo dado.
    """
    try:
        # Validar função
        valida, expr, mensagem = MathService.validar_e_processar_funcao(request.funcao)
        if not valida:
            return AreaResponse(
                sucesso=False,
                erro=mensagem
            )
        
        # Calcular integral numérica
        valor_integral, erro_estimado = MathService.calcular_integral_numerica(
            expr, request.a, request.b
        )
        
        # Gerar gráfico
        grafico_base64 = MathService.gerar_grafico_base64(
            expr, request.a, request.b, request.resolucao
        )
        
        # Gerar pontos do gráfico
        pontos_grafico = MathService.gerar_pontos_grafico(
            expr, request.a, request.b, request.resolucao
        )
        
        return AreaResponse(
            sucesso=True,
            valor_integral=valor_integral,
            area_total=abs(valor_integral),  # Área sempre positiva
            erro_estimado=erro_estimado,
            grafico_base64=grafico_base64,
            pontos_grafico=pontos_grafico,
            funcao_formatada=str(expr),
            intervalo={"a": request.a, "b": request.b},
            calculado_em=MathService.obter_timestamp(),
            erro=None
        )
        
    except Exception as e:
        return AreaResponse(
            sucesso=False,
            erro=f"Erro no cálculo da área: {str(e)}"
        ) 