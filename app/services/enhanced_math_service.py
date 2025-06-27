import sympy as sp
import numpy as np
from scipy import integrate
from scipy.integrate import quad, dblquad, romberg
import mpmath
# from numba import jit, njit  # Removido para compatibilidade com Python 3.13
from typing import Tuple, List, Optional, Dict, Any, Union
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
import concurrent.futures
import time
import logging

from app.models.responses import PontoGrafico
from app.core.config import settings
from app.core.cache_manager import cached_calculation, expression_cache_key, cache_manager

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore', category=RuntimeWarning)

class EnhancedMathService:
    """
    Serviço matemático aprimorado com maior precisão e otimizações.
    """
    
    @staticmethod
    def set_precision(precision: int = None):
        """
        Define a precisão global para cálculos.
        """
        if precision is None:
            precision = settings.numerical_precision
        
        # Configurar precisão do mpmath
        mpmath.mp.dps = precision
        
        # Configurar precisão do SymPy
        sp.init_printing(use_unicode=True)
        
    @staticmethod
    @cached_calculation(cache_key_func=lambda funcao_str, *args, **kwargs: 
                       expression_cache_key(funcao_str, "validate", *args, **kwargs))
    def validar_e_processar_funcao_avancada(funcao_str: str) -> Tuple[bool, Optional[sp.Expr], str, Dict[str, Any]]:
        """
        Validação avançada com análise de complexidade e propriedades.
        """
        try:
            # Definir precisão
            EnhancedMathService.set_precision()
            
            # Limpar e preparar a string
            funcao_limpa = funcao_str.replace('^', '**').replace(' ', '')
            
            # Substituições comuns para melhor interpretação
            substituicoes = {
                'ln': 'log',
                'e': 'E',
                'pi': 'pi',
                'sen': 'sin',
                'cos': 'cos',
                'tg': 'tan',
                'tan': 'tan',
                'sec': 'sec',
                'csc': 'csc',
                'cot': 'cot',
                'arcsin': 'asin',
                'arccos': 'acos',
                'arctan': 'atan',
                'sqrt': 'sqrt',
                'abs': 'Abs'
            }
            
            for old, new in substituicoes.items():
                funcao_limpa = funcao_limpa.replace(old, new)
            
            # Definir variável simbólica
            x = sp.Symbol('x', real=True)
            
            # Parsear com tratamento de erro mais robusto
            try:
                expr = sp.sympify(funcao_limpa, locals={'x': x}, evaluate=False)
            except:
                # Tentativa com parsing mais permissivo
                expr = sp.parse_expr(funcao_limpa, local_dict={'x': x}, evaluate=False)
            
            # Simplificar e validar
            expr_simplificada = sp.simplify(expr)
            
            # Análise de complexidade
            analise = EnhancedMathService._analisar_complexidade_funcao(expr_simplificada)
            
            # Verificações de validade
            if not isinstance(expr_simplificada, (sp.Expr, sp.Number)):
                return False, None, "Expressão matemática inválida", {}
            
            # Verificar se é muito complexa
            if analise['complexidade'] > settings.max_function_complexity:
                return False, None, f"Função muito complexa (limite: {settings.max_function_complexity})", analise
            
            return True, expr_simplificada, "Função válida", analise
            
        except Exception as e:
            return False, None, f"Erro de sintaxe: {str(e)}", {}
    
    @staticmethod
    def _analisar_complexidade_funcao(expr: sp.Expr) -> Dict[str, Any]:
        """
        Analisa a complexidade computacional de uma função.
        """
        try:
            # Contar nós na árvore de expressão
            nos_totais = len(sp.preorder_traversal(expr))
            
            # Identificar tipos de operações
            operacoes = {
                'trigonometricas': 0,
                'exponenciais': 0,
                'logaritmicas': 0,
                'potencias': 0,
                'racionais': 0
            }
            
            for node in sp.preorder_traversal(expr):
                if isinstance(node, (sp.sin, sp.cos, sp.tan, sp.sec, sp.csc, sp.cot)):
                    operacoes['trigonometricas'] += 1
                elif isinstance(node, (sp.exp, sp.sinh, sp.cosh, sp.tanh)):
                    operacoes['exponenciais'] += 1
                elif isinstance(node, (sp.log, sp.ln)):
                    operacoes['logaritmicas'] += 1
                elif isinstance(node, sp.Pow):
                    operacoes['potencias'] += 1
                elif isinstance(node, sp.Rational):
                    operacoes['racionais'] += 1
            
            # Calcular score de complexidade
            complexidade = nos_totais + sum(operacoes.values()) * 2
            
            return {
                'complexidade': complexidade,
                'nos_totais': nos_totais,
                'operacoes': operacoes,
                'nivel_complexidade': 'baixa' if complexidade < 50 else 'media' if complexidade < 200 else 'alta'
            }
            
        except Exception:
            return {'complexidade': 999, 'erro': 'Análise falhou'}
    
    @staticmethod
    @cached_calculation(cache_key_func=lambda expr, a, b, *args, **kwargs: 
                       expression_cache_key(str(expr), "integral_numerica", a, b, *args, **kwargs))
    def calcular_integral_numerica_avancada(expr: sp.Expr, a: float, b: float, 
                                          metodo: str = None, tolerancia: float = 1e-12) -> Tuple[float, float, Dict[str, Any]]:
        """
        Cálculo de integral numérica com múltiplos métodos e controle de erro.
        """
        try:
            if metodo is None:
                metodo = settings.integration_method
            
            # Converter para função numérica otimizada
            x = sp.Symbol('x')
            
            # Tentar usar lambdify com diferentes backends para otimização
            backends = ['numpy', 'scipy', 'math']
            func_numerica = None
            
            for backend in backends:
                try:
                    func_numerica = sp.lambdify(x, expr, backend)
                    # Testar se funciona
                    func_numerica(float(a))
                    break
                except:
                    continue
            
            if func_numerica is None:
                raise ValueError("Não foi possível converter para função numérica")
            
            # JIT desabilitado para compatibilidade com Python 3.13
            # if settings.enable_numba_jit:
            #     try:
            #         func_numerica = EnhancedMathService._criar_funcao_jit(func_numerica)
            #     except:
            #         pass  # Continuar sem JIT se houver problema
            
            # Escolher método de integração
            resultado, erro, info = EnhancedMathService._integrar_com_metodo(
                func_numerica, a, b, metodo, tolerancia
            )
            
            return resultado, erro, info
            
        except Exception as e:
            raise ValueError(f"Erro no cálculo numérico avançado: {str(e)}")
    
    @staticmethod
    def _criar_funcao_jit(func):
        """
        Função JIT desabilitada para compatibilidade com Python 3.13.
        Retorna a função original sem modificações.
        """
        # JIT compilation desabilitado para compatibilidade
        return func
    
    @staticmethod
    def _integrar_com_metodo(func, a: float, b: float, metodo: str, tolerancia: float) -> Tuple[float, float, Dict[str, Any]]:
        """
        Aplica diferentes métodos de integração numérica.
        """
        start_time = time.time()
        
        try:
            if metodo == "adaptive":
                # Integração adaptativa com subdivisions limitadas
                resultado, erro = quad(
                    func, a, b, 
                    epsabs=tolerancia, 
                    epsrel=tolerancia,
                    limit=settings.max_subdivisions
                )
                info = {
                    'metodo': 'Quadratura Adaptativa',
                    'subdivisions': 'variável',
                    'convergencia': 'adaptativa'
                }
                
            elif metodo == "romberg":
                # Método de Romberg (mais preciso para funções suaves)
                try:
                    # Criar array de pontos
                    n_pontos = min(100, settings.default_resolution)
                    pontos = np.linspace(a, b, n_pontos)
                    valores = [func(x) for x in pontos]
                    
                    resultado = romberg(func, a, b, tol=tolerancia)
                    erro = tolerancia  # Estimativa
                    
                    info = {
                        'metodo': 'Romberg',
                        'pontos_utilizados': n_pontos,
                        'convergencia': 'extrapolação'
                    }
                except:
                    # Fallback para quad
                    resultado, erro = quad(func, a, b, epsabs=tolerancia)
                    info = {'metodo': 'Fallback Adaptativa'}
                    
            else:  # fixed
                # Método fixo com número predefinido de pontos
                n_pontos = settings.default_resolution
                pontos = np.linspace(a, b, n_pontos)
                valores = np.array([func(x) for x in pontos])
                
                # Regra de Simpson composta
                h = (b - a) / (n_pontos - 1)
                resultado = integrate.simpson(valores, dx=h)
                
                # Estimativa de erro baseada na resolução
                erro = abs(resultado) * (1.0 / n_pontos)
                
                info = {
                    'metodo': 'Simpson Composta',
                    'pontos_utilizados': n_pontos,
                    'passo': h
                }
            
            execution_time = time.time() - start_time
            info['tempo_execucao'] = execution_time
            
            return resultado, abs(erro), info
            
        except Exception as e:
            # Método de fallback mais simples
            resultado, erro = quad(func, a, b)
            return resultado, abs(erro), {'metodo': 'Fallback Simples', 'erro': str(e)}
    
    @staticmethod
    @cached_calculation(cache_key_func=lambda expr, *args, **kwargs: 
                       expression_cache_key(str(expr), "integral_simbolica", *args, **kwargs))
    def calcular_integral_simbolica_avancada(expr: sp.Expr, a: Optional[float] = None, 
                                           b: Optional[float] = None) -> Dict[str, Any]:
        """
        Cálculo simbólico avançado com múltiplas tentativas e simplificação inteligente.
        """
        try:
            x = sp.Symbol('x')
            
            # Tentar diferentes abordagens de integração
            antiderivada = None
            metodo_usado = None
            
            # 1. Tentativa padrão
            try:
                antiderivada = sp.integrate(expr, x)
                metodo_usado = "integração_direta"
            except:
                pass
            
            # 2. Tentativa com expansão em série (para funções complexas)
            if antiderivada is None:
                try:
                    expr_expandida = sp.series(expr, x, 0, 10).removeO()
                    antiderivada = sp.integrate(expr_expandida, x)
                    metodo_usado = "expansão_serie"
                except:
                    pass
            
            # 3. Tentativa com simplificação prévia
            if antiderivada is None:
                try:
                    expr_simples = sp.simplify(expr)
                    antiderivada = sp.integrate(expr_simples, x)
                    metodo_usado = "simplificação_prévia"
                except:
                    pass
            
            # 4. Tentativa com partes (para produtos)
            if antiderivada is None and isinstance(expr, sp.Mul):
                try:
                    # Identificar partes para integração por partes
                    fatores = expr.as_ordered_factors()
                    if len(fatores) >= 2:
                        u = fatores[0]
                        dv = sp.Mul(*fatores[1:])
                        
                        # Aplicar fórmula de integração por partes
                        v = sp.integrate(dv, x)
                        du = sp.diff(u, x)
                        
                        antiderivada = u * v - sp.integrate(v * du, x)
                        metodo_usado = "integração_por_partes"
                except:
                    pass
            
            if antiderivada is None:
                return {
                    'sucesso': False,
                    'erro': 'Integral simbólica não encontrada',
                    'antiderivada': None
                }
            
            # Simplificar resultado
            antiderivada_simplificada = sp.simplify(antiderivada)
            
            resultado = {
                'sucesso': True,
                'antiderivada': str(antiderivada_simplificada),
                'antiderivada_latex': sp.latex(antiderivada_simplificada),
                'metodo_integracao': metodo_usado,
                'resultado_simbolico': None
            }
            
            # Calcular integral definida se limites fornecidos
            if a is not None and b is not None:
                try:
                    # Usar alta precisão para o cálculo
                    with sp.evaluate(False):
                        integral_definida = antiderivada_simplificada.subs(x, b) - antiderivada_simplificada.subs(x, a)
                    
                    valor_numerico = float(integral_definida.evalf(settings.numerical_precision))
                    resultado['resultado_simbolico'] = valor_numerico
                    
                except Exception as e:
                    # Fallback para cálculo numérico
                    try:
                        valor_numerico, _, _ = EnhancedMathService.calcular_integral_numerica_avancada(expr, a, b)
                        resultado['resultado_simbolico'] = valor_numerico
                        resultado['nota'] = 'Valor calculado numericamente (simbólico falhou)'
                    except:
                        resultado['erro_definida'] = str(e)
            
            return resultado
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f"Erro no cálculo simbólico: {str(e)}",
                'antiderivada': None
            }
    
    @staticmethod
    @cached_calculation(cache_key_func=lambda expr, tipo_derivada, *args, **kwargs: 
                       expression_cache_key(str(expr), "derivada", tipo_derivada, *args, **kwargs))
    def calcular_derivada_avancada(expr: sp.Expr, tipo_derivada: str = "primeira") -> Dict[str, Any]:
        """
        Cálculo de derivada com verificação de continuidade e análise de pontos críticos.
        """
        try:
            x = sp.Symbol('x')
            
            # Determinar ordem da derivada
            ordem_map = {
                'primeira': 1, 'segunda': 2, 'terceira': 3,
                '1': 1, '2': 2, '3': 3
            }
            
            ordem = ordem_map.get(tipo_derivada.lower(), 1)
            
            # Extrair número se formato "na" (ex: "4a")
            if tipo_derivada.lower().endswith('a') and tipo_derivada[:-1].isdigit():
                ordem = int(tipo_derivada[:-1])
            
            # Calcular derivada com alta precisão
            derivada = sp.diff(expr, x, ordem)
            
            # Simplificar resultado
            derivada_simplificada = sp.simplify(derivada)
            
            # Análise adicional da derivada
            analise = EnhancedMathService._analisar_derivada(expr, derivada_simplificada, ordem)
            
            resultado = {
                'derivada': str(derivada_simplificada),
                'derivada_latex': sp.latex(derivada_simplificada),
                'derivada_simplificada': str(derivada_simplificada),
                'ordem': ordem,
                'analise': analise
            }
            
            return resultado
            
        except Exception as e:
            raise ValueError(f"Erro no cálculo de derivada avançado: {str(e)}")
    
    @staticmethod
    def _analisar_derivada(expr_original: sp.Expr, derivada: sp.Expr, ordem: int) -> Dict[str, Any]:
        """
        Análise detalhada da derivada calculada.
        """
        try:
            x = sp.Symbol('x')
            analise = {
                'pontos_criticos': [],
                'singularidades': [],
                'comportamento': {},
                'continuidade': 'verificar'
            }
            
            # Encontrar pontos críticos (onde derivada = 0)
            if ordem == 1:
                try:
                    pontos_criticos = sp.solve(derivada, x)
                    # Filtrar apenas soluções reais
                    pontos_reais = []
                    for ponto in pontos_criticos:
                        if ponto.is_real:
                            pontos_reais.append(float(ponto.evalf()))
                    
                    analise['pontos_criticos'] = pontos_reais[:10]  # Limitar a 10 pontos
                except:
                    analise['pontos_criticos'] = 'cálculo_falhou'
            
            # Verificar singularidades
            try:
                singularidades = sp.solve(sp.denom(derivada), x)
                sing_reais = []
                for sing in singularidades:
                    if sing.is_real:
                        sing_reais.append(float(sing.evalf()))
                
                analise['singularidades'] = sing_reais[:5]  # Limitar a 5
            except:
                analise['singularidades'] = 'cálculo_falhou'
            
            return analise
            
        except Exception:
            return {'erro': 'análise_falhou'}
    
    @staticmethod
    @cached_calculation(cache_key_func=lambda expr, ponto_limite, tipo_limite, *args, **kwargs: 
                       expression_cache_key(str(expr), "limite", ponto_limite, tipo_limite, *args, **kwargs))
    def calcular_limite_avancado(expr: sp.Expr, ponto_limite: float, 
                               tipo_limite: str = "bilateral") -> Dict[str, Any]:
        """
        Cálculo de limite com análise de convergência e múltiplas abordagens.
        """
        try:
            x = sp.Symbol('x')
            
            # Normalizar ponto limite para casos especiais
            if ponto_limite == float('inf'):
                ponto_sp = sp.oo
            elif ponto_limite == float('-inf'):
                ponto_sp = -sp.oo
            else:
                ponto_sp = ponto_limite
            
            # Calcular limite baseado no tipo com múltiplas abordagens
            limites_calculados = {}
            
            # 1. Cálculo direto
            try:
                if tipo_limite.lower() == "esquerda":
                    limite_direto = sp.limit(expr, x, ponto_sp, '-')
                elif tipo_limite.lower() == "direita":
                    limite_direto = sp.limit(expr, x, ponto_sp, '+')
                else:  # bilateral
                    limite_direto = sp.limit(expr, x, ponto_sp)
                
                limites_calculados['direto'] = limite_direto
            except Exception as e:
                limites_calculados['direto'] = f'erro: {str(e)}'
            
            # 2. Usando L'Hôpital para formas indeterminadas
            try:
                limite_lhopital = EnhancedMathService._aplicar_lhopital(expr, x, ponto_sp, tipo_limite)
                if limite_lhopital is not None:
                    limites_calculados['lhopital'] = limite_lhopital
            except:
                pass
            
            # 3. Expansão em série para pontos finitos
            if ponto_sp not in [sp.oo, -sp.oo]:
                try:
                    serie = sp.series(expr, x, ponto_sp, 3).removeO()
                    limite_serie = sp.limit(serie, x, ponto_sp)
                    limites_calculados['serie'] = limite_serie
                except:
                    pass
            
            # Escolher melhor resultado
            limite_final = limites_calculados.get('direto')
            metodo_usado = 'direto'
            
            # Se direto falhou, usar alternativas
            if isinstance(limite_final, str) or limite_final is None:
                if 'lhopital' in limites_calculados:
                    limite_final = limites_calculados['lhopital']
                    metodo_usado = 'lhopital'
                elif 'serie' in limites_calculados:
                    limite_final = limites_calculados['serie']
                    metodo_usado = 'serie'
            
            # Verificar se o limite existe e é finito
            valor_limite = None
            existe_limite = False
            
            if limite_final not in [sp.oo, -sp.oo, sp.nan, None] and not isinstance(limite_final, str):
                try:
                    valor_limite = float(limite_final.evalf(settings.numerical_precision))
                    existe_limite = True
                except:
                    existe_limite = False
            elif limite_final == sp.oo:
                valor_limite = float('inf')
                existe_limite = True
            elif limite_final == -sp.oo:
                valor_limite = float('-inf')
                existe_limite = True
            
            resultado = {
                'valor_limite': valor_limite,
                'limite_latex': sp.latex(limite_final) if existe_limite and limite_final is not None else None,
                'existe_limite': existe_limite,
                'metodo_usado': metodo_usado,
                'todos_calculos': limites_calculados,
                'tipo_convergencia': EnhancedMathService._analisar_convergencia(limite_final)
            }
            
            return resultado
            
        except Exception as e:
            raise ValueError(f"Erro no cálculo de limite avançado: {str(e)}")
    
    @staticmethod
    def _aplicar_lhopital(expr: sp.Expr, x: sp.Symbol, ponto: sp.Number, tipo_limite: str) -> Optional[sp.Expr]:
        """
        Aplica a regra de L'Hôpital para formas indeterminadas.
        """
        try:
            # Verificar se é forma indeterminada (0/0 ou ∞/∞)
            limite_num = sp.limit(sp.numer(expr), x, ponto)
            limite_den = sp.limit(sp.denom(expr), x, ponto)
            
            # Aplicar L'Hôpital se necessário (máximo 3 vezes)
            for i in range(3):
                if (limite_num == 0 and limite_den == 0) or (limite_num == sp.oo and limite_den == sp.oo):
                    # Derivar numerador e denominador
                    num_deriv = sp.diff(sp.numer(expr), x)
                    den_deriv = sp.diff(sp.denom(expr), x)
                    
                    expr = num_deriv / den_deriv
                    
                    # Recalcular limites
                    limite_num = sp.limit(num_deriv, x, ponto)
                    limite_den = sp.limit(den_deriv, x, ponto)
                    
                    if limite_den != 0:
                        if tipo_limite.lower() == "esquerda":
                            return sp.limit(expr, x, ponto, '-')
                        elif tipo_limite.lower() == "direita":
                            return sp.limit(expr, x, ponto, '+')
                        else:
                            return sp.limit(expr, x, ponto)
                else:
                    break
            
            return None
            
        except:
            return None
    
    @staticmethod
    def _analisar_convergencia(limite: sp.Expr) -> str:
        """
        Analisa o tipo de convergência do limite.
        """
        if limite == sp.oo:
            return "diverge_para_infinito"
        elif limite == -sp.oo:
            return "diverge_para_menos_infinito"
        elif limite == sp.nan:
            return "indeterminado"
        elif limite is None:
            return "nao_existe"
        else:
            try:
                valor = float(limite.evalf())
                return "converge_para_valor_finito"
            except:
                return "comportamento_complexo"
    
    @staticmethod
    @cached_calculation(cache_key_func=lambda expr, a, b, resolucao, *args, **kwargs: 
                       expression_cache_key(str(expr), "grafico", a, b, resolucao, *args, **kwargs))
    def gerar_grafico_otimizado(expr: sp.Expr, a: float, b: float, 
                              resolucao: int = None) -> Tuple[str, List[PontoGrafico], Dict[str, Any]]:
        """
        Geração de gráfico otimizada com detecção automática de singularidades.
        """
        try:
            if resolucao is None:
                resolucao = settings.default_resolution
            
            x = sp.Symbol('x')
            
            # Detectar singularidades no intervalo
            singularidades = EnhancedMathService._detectar_singularidades(expr, a, b)
            
            # Gerar pontos adaptativos (mais pontos perto de singularidades)
            pontos_x = EnhancedMathService._gerar_pontos_adaptativos(a, b, resolucao, singularidades)
            
            # Converter para função numérica
            func_numerica = sp.lambdify(x, expr, 'numpy')
            
            # Calcular pontos com tratamento de erro
            pontos_grafico = []
            pontos_problematicos = []
            
            for x_val in pontos_x:
                try:
                    y_val = func_numerica(x_val)
                    
                    # Verificar se o valor é válido
                    if np.isfinite(y_val):
                        pontos_grafico.append(PontoGrafico(x=float(x_val), y=float(y_val)))
                    else:
                        pontos_problematicos.append(x_val)
                        
                except:
                    pontos_problematicos.append(x_val)
            
            # Gerar gráfico com matplotlib otimizado
            plt.style.use('seaborn-v0_8')  # Estilo mais moderno
            fig, ax = plt.subplots(figsize=(settings.graph_width, settings.graph_height), 
                                 dpi=settings.graph_dpi)
            
            # Plotar função
            x_vals = [p.x for p in pontos_grafico]
            y_vals = [p.y for p in pontos_grafico]
            
            ax.plot(x_vals, y_vals, 'b-', linewidth=2, alpha=0.8, label=f'f(x) = {str(expr)}')
            
            # Destacar singularidades se encontradas
            if singularidades:
                for sing in singularidades:
                    if a <= sing <= b:
                        ax.axvline(x=sing, color='red', linestyle='--', alpha=0.7, 
                                 label=f'Singularidade em x={sing:.3f}')
            
            # Configurações do gráfico
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('x', fontsize=12)
            ax.set_ylabel('f(x)', fontsize=12)
            ax.set_title(f'Gráfico de f(x) = {str(expr)}', fontsize=14, fontweight='bold')
            
            # Auto-escala inteligente
            if y_vals:
                y_min, y_max = min(y_vals), max(y_vals)
                y_range = y_max - y_min
                if y_range > 0:
                    margin = y_range * 0.1
                    ax.set_ylim(y_min - margin, y_max + margin)
            
            ax.legend()
            plt.tight_layout()
            
            # Converter para base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            plt.close(fig)  # Liberar memória
            
            # Informações adicionais
            info_grafico = {
                'pontos_calculados': len(pontos_grafico),
                'pontos_problematicos': len(pontos_problematicos),
                'singularidades_detectadas': len(singularidades),
                'resolucao_efetiva': len(pontos_x),
                'intervalo': [a, b]
            }
            
            return image_base64, pontos_grafico, info_grafico
            
        except Exception as e:
            raise ValueError(f"Erro na geração de gráfico otimizado: {str(e)}")
    
    @staticmethod
    def _detectar_singularidades(expr: sp.Expr, a: float, b: float) -> List[float]:
        """
        Detecta singularidades (pontos onde a função não está definida) no intervalo.
        """
        try:
            x = sp.Symbol('x')
            singularidades = []
            
            # Encontrar zeros do denominador
            denominador = sp.denom(expr)
            if denominador != 1:
                zeros_denom = sp.solve(denominador, x)
                for zero in zeros_denom:
                    try:
                        zero_val = float(zero.evalf())
                        if a <= zero_val <= b:
                            singularidades.append(zero_val)
                    except:
                        continue
            
            return sorted(singularidades)
            
        except:
            return []
    
    @staticmethod
    def _gerar_pontos_adaptativos(a: float, b: float, resolucao: int, 
                                singularidades: List[float]) -> np.ndarray:
        """
        Gera pontos com densidade adaptativa (mais pontos perto de singularidades).
        """
        try:
            if not singularidades:
                return np.linspace(a, b, resolucao)
            
            # Distribuir pontos com mais densidade perto de singularidades
            pontos_finais = []
            
            # Pontos base distribuídos uniformemente
            pontos_base = np.linspace(a, b, resolucao // 2)
            pontos_finais.extend(pontos_base)
            
            # Pontos adicionais perto de singularidades
            for sing in singularidades:
                if a < sing < b:
                    # Janela ao redor da singularidade
                    delta = min(0.1 * (b - a), abs(b - a) / 20)
                    
                    # Pontos à esquerda da singularidade
                    left_start = max(a, sing - delta)
                    left_points = np.linspace(left_start, sing - 1e-6, resolucao // 10)
                    pontos_finais.extend(left_points)
                    
                    # Pontos à direita da singularidade
                    right_end = min(b, sing + delta)
                    right_points = np.linspace(sing + 1e-6, right_end, resolucao // 10)
                    pontos_finais.extend(right_points)
            
            # Remover duplicatas e ordenar
            pontos_finais = sorted(list(set(pontos_finais)))
            
            return np.array(pontos_finais)
            
        except Exception:
            return np.linspace(a, b, resolucao) 