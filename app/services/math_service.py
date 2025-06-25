import sympy as sp
import numpy as np
from scipy import integrate
from typing import Tuple, List, Optional, Dict, Any
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo
import matplotlib.pyplot as plt
from datetime import datetime

from app.models.responses import PontoGrafico
from app.core.config import settings

class MathService:
    
    @staticmethod
    def validar_e_processar_funcao(funcao_str: str) -> Tuple[bool, Optional[sp.Expr], str]:
        """
        Valida e processa uma função matemática string.
        Retorna: (é_válida, expressao_sympy, mensagem_erro)
        """
        try:
            # Limpar e preparar a string
            funcao_limpa = funcao_str.replace('^', '**')
            
            # Definir variável simbólica
            x = sp.Symbol('x', real=True)
            
            # Tentar parsear a função
            expr = sp.sympify(funcao_limpa, locals={'x': x})
            
            # Verificar se é uma expressão válida
            if not isinstance(expr, (sp.Expr, sp.Number)):
                return False, None, "Expressão matemática inválida"
            
            return True, expr, "Função válida"
            
        except Exception as e:
            return False, None, f"Erro de sintaxe: {str(e)}"
    
    @staticmethod
    def calcular_integral_numerica(expr: sp.Expr, a: float, b: float) -> Tuple[float, float]:
        """
        Calcula integral numérica e estima erro.
        Retorna: (valor_integral, erro_estimado)
        """
        try:
            # Converter expressão SymPy para função numérica
            x = sp.Symbol('x')
            func_numerica = sp.lambdify(x, expr, 'numpy')
            
            # Calcular integral numérica com estimativa de erro
            resultado, erro = integrate.quad(func_numerica, a, b)
            
            return resultado, abs(erro)
            
        except Exception as e:
            raise ValueError(f"Erro no cálculo numérico: {str(e)}")
    
    @staticmethod
    def calcular_integral_simbolica(expr: sp.Expr, a: Optional[float] = None, b: Optional[float] = None) -> Dict[str, Any]:
        """
        Calcula integral simbólica (indefinida ou definida).
        """
        try:
            x = sp.Symbol('x')
            
            # Calcular antiderivada
            antiderivada = sp.integrate(expr, x)
            antiderivada_simplificada = sp.simplify(antiderivada)
            
            resultado = {
                'antiderivada': str(antiderivada_simplificada),
                'antiderivada_latex': sp.latex(antiderivada_simplificada),
                'resultado_simbolico': None
            }
            
            # Se há limites, calcular integral definida
            if a is not None and b is not None:
                integral_definida = sp.integrate(expr, (x, a, b))
                resultado['resultado_simbolico'] = float(integral_definida.evalf())
            
            return resultado
            
        except Exception as e:
            raise ValueError(f"Erro no cálculo simbólico: {str(e)}")
    
    @staticmethod
    def gerar_passos_resolucao(funcao_original: str, antiderivada: str, a: Optional[float] = None, b: Optional[float] = None) -> List[str]:
        """
        Gera passos detalhados da resolução.
        """
        passos = [
            f"Função original: {funcao_original}",
            f"Aplicando integração: ∫({funcao_original})dx",
            f"Antiderivada: {antiderivada}"
        ]
        
        if a is not None and b is not None:
            passos.extend([
                f"Aplicando limites de integração: [{a}, {b}]",
                f"Calculando: F({b}) - F({a})"
            ])
        else:
            passos.append("Resultado: " + antiderivada + " + C")
        
        return passos
    
    @staticmethod
    def gerar_pontos_grafico(expr: sp.Expr, a: float, b: float, resolucao: int = 400) -> List[PontoGrafico]:
        """
        Gera pontos para plotagem do gráfico.
        """
        try:
            x = sp.Symbol('x')
            func_numerica = sp.lambdify(x, expr, 'numpy')
            
            # Gerar pontos
            x_vals = np.linspace(a, b, resolucao)
            y_vals = func_numerica(x_vals)
            
            # Filtrar valores inválidos (inf, nan)
            mask = np.isfinite(y_vals)
            x_vals = x_vals[mask]
            y_vals = y_vals[mask]
            
            return [PontoGrafico(x=float(x), y=float(y)) for x, y in zip(x_vals, y_vals)]
            
        except Exception as e:
            raise ValueError(f"Erro ao gerar pontos do gráfico: {str(e)}")
    
    @staticmethod
    def gerar_grafico_base64(expr: sp.Expr, a: float, b: float, resolucao: int = 400) -> str:
        """
        Gera gráfico da função em formato base64.
        """
        try:
            x = sp.Symbol('x')
            func_numerica = sp.lambdify(x, expr, 'numpy')
            
            # Configurar matplotlib
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(settings.graph_width, settings.graph_height), dpi=settings.graph_dpi)
            
            # Gerar pontos
            x_vals = np.linspace(a, b, resolucao)
            y_vals = func_numerica(x_vals)
            
            # Plotar função
            ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x) = {str(expr)}')
            ax.fill_between(x_vals, y_vals, alpha=0.3, color='lightblue')
            
            # Configurar gráfico
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('x', fontsize=12)
            ax.set_ylabel('f(x)', fontsize=12)
            ax.set_title(f'Gráfico da função f(x) = {str(expr)}', fontsize=14)
            ax.legend()
            
            # Salvar em base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=settings.graph_dpi)
            buffer.seek(0)
            
            # Converter para base64
            grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Limpar memória
            plt.close(fig)
            buffer.close()
            
            return grafico_base64
            
        except Exception as e:
            plt.close('all')  # Garantir limpeza em caso de erro
            raise ValueError(f"Erro ao gerar gráfico: {str(e)}")
    
    @staticmethod
    def obter_timestamp() -> str:
        """
        Retorna timestamp atual em formato ISO 8601.
        """
        return datetime.now().isoformat() 