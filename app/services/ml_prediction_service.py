import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import sympy as sp
from sympy import lambdify, symbols, diff, integrate
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
import warnings
from datetime import datetime, timedelta
import os
import hashlib
import json

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class MLPredictionService:
    """
    Serviço de Machine Learning para predições matemáticas inteligentes.
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_generators = {}
        self.model_cache_dir = "ml_models_cache"
        self.x = symbols('x')
        
        # Criar diretório de cache se não existir
        os.makedirs(self.model_cache_dir, exist_ok=True)
        
        # Inicializar modelos base
        self._initialize_base_models()
    
    def _initialize_base_models(self):
        """
        Inicializa modelos base para diferentes tipos de predições.
        """
        self.models = {
            'integration_difficulty': RandomForestRegressor(
                n_estimators=100, random_state=42
            ),
            'computation_time': GradientBoostingRegressor(
                n_estimators=100, random_state=42
            ),
            'numerical_stability': RandomForestRegressor(
                n_estimators=50, random_state=42
            ),
            'convergence_predictor': GradientBoostingRegressor(
                n_estimators=80, random_state=42
            )
        }
        
        self.scalers = {
            model_name: StandardScaler() 
            for model_name in self.models.keys()
        }
        
        self.feature_generators = {
            model_name: PolynomialFeatures(degree=2, include_bias=False)
            for model_name in self.models.keys()
        }
    
    def extract_function_features(self, function_str: str) -> np.ndarray:
        """
        Extrai características matemáticas de uma função para ML.
        """
        try:
            expr = sp.sympify(function_str.replace('^', '**'))
            
            features = []
            
            # 1. Características básicas
            complexity = len(str(expr))
            features.append(complexity)
            
            # 2. Grau do polinômio (se aplicável)
            try:
                degree = sp.degree(expr, self.x)
                features.append(degree if degree is not None else 0)
            except:
                features.append(0)
            
            # 3. Número de operações
            operations = {
                'add': expr.count(sp.Add),
                'mul': expr.count(sp.Mul),
                'pow': expr.count(sp.Pow),
                'sin': expr.count(sp.sin),
                'cos': expr.count(sp.cos),
                'tan': expr.count(sp.tan),
                'exp': expr.count(sp.exp),
                'log': expr.count(sp.log),
                'sqrt': expr.count(sp.sqrt)
            }
            
            features.extend(list(operations.values()))
            
            # 4. Características das derivadas
            try:
                first_deriv = diff(expr, self.x)
                second_deriv = diff(first_deriv, self.x)
                
                features.append(len(str(first_deriv)))
                features.append(len(str(second_deriv)))
                
                # Singularidades aparentes
                critical_points = sp.solve(first_deriv, self.x)
                features.append(len(critical_points) if isinstance(critical_points, list) else 0)
            except:
                features.extend([0, 0, 0])
            
            # 5. Características de integração
            try:
                # Tentar integração simbólica simples
                antiderivative = integrate(expr, self.x)
                features.append(len(str(antiderivative)))
                
                # Verificar se há funções especiais
                has_special_functions = any(
                    func in str(antiderivative) 
                    for func in ['Integral', 'erf', 'gamma', 'Ei', 'Si', 'Ci']
                )
                features.append(int(has_special_functions))
            except:
                features.extend([1000, 1])  # Valores indicando dificuldade
            
            # 6. Características de estabilidade numérica
            # Verificar crescimento da função
            try:
                limit_inf = sp.limit(expr, self.x, sp.oo)
                limit_neg_inf = sp.limit(expr, self.x, -sp.oo)
                
                growth_factor = 0
                if limit_inf == sp.oo or limit_neg_inf == sp.oo:
                    growth_factor = 2
                elif limit_inf == -sp.oo or limit_neg_inf == -sp.oo:
                    growth_factor = 2
                elif limit_inf is None or limit_neg_inf is None:
                    growth_factor = 1
                
                features.append(growth_factor)
            except:
                features.append(1)
            
            # 7. Densidade de singularidades
            function_str_clean = str(expr)
            singularity_indicators = function_str_clean.count('/') + function_str_clean.count('log')
            features.append(singularity_indicators)
            
            return np.array(features, dtype=float)
            
        except Exception as e:
            logger.warning(f"Erro ao extrair características: {str(e)}")
            # Retornar features padrão em caso de erro
            return np.zeros(20, dtype=float)
    
    def predict_integration_difficulty(self, function_str: str) -> Dict[str, Any]:
        """
        Prediz a dificuldade de integração de uma função.
        """
        try:
            features = self.extract_function_features(function_str)
            
            # Se o modelo não foi treinado, usar heurísticas
            if not hasattr(self.models['integration_difficulty'], 'feature_importances_'):
                return self._heuristic_integration_difficulty(function_str, features)
            
            # Usar modelo treinado
            features_scaled = self.scalers['integration_difficulty'].transform([features])
            features_poly = self.feature_generators['integration_difficulty'].transform(features_scaled)
            
            difficulty_score = self.models['integration_difficulty'].predict(features_poly)[0]
            
            # Normalizar score entre 0 e 1
            difficulty_normalized = max(0, min(1, difficulty_score / 100))
            
            # Classificar dificuldade
            if difficulty_normalized < 0.3:
                difficulty_level = "Fácil"
                recommended_method = "simpson"
            elif difficulty_normalized < 0.7:
                difficulty_level = "Moderada"
                recommended_method = "adaptativo"
            else:
                difficulty_level = "Difícil"
                recommended_method = "monte_carlo"
            
            return {
                'difficulty_score': float(difficulty_normalized),
                'difficulty_level': difficulty_level,
                'recommended_method': recommended_method,
                'confidence': 0.8,  # Placeholder para confiança
                'features_used': len(features)
            }
            
        except Exception as e:
            logger.error(f"Erro na predição de dificuldade: {str(e)}")
            return self._heuristic_integration_difficulty(function_str)
    
    def _heuristic_integration_difficulty(self, function_str: str, features: np.ndarray = None) -> Dict[str, Any]:
        """
        Heurística para estimar dificuldade quando modelo não está disponível.
        """
        try:
            expr = sp.sympify(function_str.replace('^', '**'))
            
            difficulty_score = 0.0
            
            # Analisar complexidade básica
            complexity = len(str(expr))
            difficulty_score += min(0.3, complexity / 100)
            
            # Analisar tipos de funções
            function_types = {
                'trigonometric': any(f in str(expr) for f in ['sin', 'cos', 'tan', 'sec', 'csc', 'cot']),
                'exponential': 'exp' in str(expr),
                'logarithmic': 'log' in str(expr),
                'rational': '/' in str(expr),
                'radical': any(f in str(expr) for f in ['sqrt', 'cbrt']),
                'hyperbolic': any(f in str(expr) for f in ['sinh', 'cosh', 'tanh'])
            }
            
            # Pontuar baseado nos tipos de função
            type_scores = {
                'trigonometric': 0.2,
                'exponential': 0.15,
                'logarithmic': 0.25,
                'rational': 0.3,
                'radical': 0.2,
                'hyperbolic': 0.2
            }
            
            for func_type, present in function_types.items():
                if present:
                    difficulty_score += type_scores[func_type]
            
            # Analisar composição de funções
            nesting_level = str(expr).count('(')
            difficulty_score += min(0.2, nesting_level / 10)
            
            # Normalizar
            difficulty_score = max(0, min(1, difficulty_score))
            
            # Classificar
            if difficulty_score < 0.3:
                difficulty_level = "Fácil"
                recommended_method = "simpson"
            elif difficulty_score < 0.7:
                difficulty_level = "Moderada"  
                recommended_method = "adaptativo"
            else:
                difficulty_level = "Difícil"
                recommended_method = "monte_carlo"
            
            return {
                'difficulty_score': float(difficulty_score),
                'difficulty_level': difficulty_level,
                'recommended_method': recommended_method,
                'confidence': 0.6,
                'method': 'heuristic'
            }
            
        except Exception as e:
            logger.error(f"Erro na heurística: {str(e)}")
            return {
                'difficulty_score': 0.5,
                'difficulty_level': "Moderada",
                'recommended_method': "simpson",
                'confidence': 0.3,
                'error': str(e)
            }
    
    def predict_computation_time(self, function_str: str, method: str, bounds: Tuple[float, float]) -> Dict[str, Any]:
        """
        Prediz tempo de computação para um cálculo.
        """
        try:
            features = self.extract_function_features(function_str)
            
            # Adicionar características específicas do método e bounds
            method_encoding = {
                'simpson': 0.5,
                'trapz': 0.3,
                'adaptativo': 0.7,
                'romberg': 0.8,
                'monte_carlo': 1.0
            }
            
            additional_features = [
                method_encoding.get(method, 0.5),
                abs(bounds[1] - bounds[0]),  # Largura do intervalo
                abs(bounds[0]) + abs(bounds[1])  # Magnitude dos bounds
            ]
            
            extended_features = np.concatenate([features, additional_features])
            
            # Heurística para tempo de computação
            base_time = 0.1  # 100ms base
            
            # Fator de complexidade da função
            complexity_factor = min(5.0, len(str(function_str)) / 20)
            
            # Fator do método
            method_factor = method_encoding.get(method, 0.5) * 2
            
            # Fator do intervalo
            interval_factor = max(1.0, abs(bounds[1] - bounds[0]) / 10)
            
            estimated_time = base_time * complexity_factor * method_factor * interval_factor
            
            # Adicionar variação aleatória pequena
            import random
            random_factor = 1 + (random.random() - 0.5) * 0.2
            estimated_time *= random_factor
            
            return {
                'estimated_time_seconds': float(estimated_time),
                'confidence': 0.7,
                'factors': {
                    'complexity': float(complexity_factor),
                    'method': float(method_factor),
                    'interval': float(interval_factor)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na predição de tempo: {str(e)}")
            return {
                'estimated_time_seconds': 1.0,
                'confidence': 0.3,
                'error': str(e)
            }
    
    def predict_optimal_resolution(self, function_str: str, bounds: Tuple[float, float]) -> Dict[str, Any]:
        """
        Prediz resolução ótima para visualização/cálculo.
        """
        try:
            features = self.extract_function_features(function_str)
            
            # Análise da variação da função
            expr = sp.sympify(function_str.replace('^', '**'))
            
            # Calcular derivada para estimar variação
            try:
                first_deriv = diff(expr, self.x)
                
                # Amostrar alguns pontos para estimar variação
                x_vals = np.linspace(bounds[0], bounds[1], 20)
                func = lambdify(self.x, expr, modules=['numpy'])
                deriv_func = lambdify(self.x, first_deriv, modules=['numpy'])
                
                variations = []
                for x_val in x_vals:
                    try:
                        deriv_val = abs(float(deriv_func(x_val)))
                        if np.isfinite(deriv_val):
                            variations.append(deriv_val)
                    except:
                        continue
                
                if variations:
                    max_variation = max(variations)
                    avg_variation = sum(variations) / len(variations)
                else:
                    max_variation = avg_variation = 1.0
                    
            except:
                max_variation = avg_variation = 1.0
            
            # Calcular resolução baseada na variação
            base_resolution = 50
            
            # Fator de variação
            variation_factor = max(1.0, min(4.0, avg_variation))
            
            # Fator de intervalo
            interval_length = abs(bounds[1] - bounds[0])
            interval_factor = max(1.0, min(3.0, interval_length / 10))
            
            optimal_resolution = int(base_resolution * variation_factor * interval_factor)
            optimal_resolution = max(20, min(500, optimal_resolution))
            
            return {
                'optimal_resolution': optimal_resolution,
                'min_recommended': max(20, optimal_resolution // 2),
                'max_recommended': min(500, optimal_resolution * 2),
                'variation_analysis': {
                    'max_variation': float(max_variation),
                    'avg_variation': float(avg_variation),
                    'interval_length': float(interval_length)
                },
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"Erro na predição de resolução: {str(e)}")
            return {
                'optimal_resolution': 50,
                'min_recommended': 20,
                'max_recommended': 200,
                'confidence': 0.3,
                'error': str(e)
            }
    
    def analyze_function_behavior(self, function_str: str) -> Dict[str, Any]:
        """
        Análise completa do comportamento de uma função usando ML.
        """
        try:
            features = self.extract_function_features(function_str)
            expr = sp.sympify(function_str.replace('^', '**'))
            
            analysis = {
                'function': function_str,
                'complexity_score': float(features[0] / 100),  # Normalizado
                'function_type': self._classify_function_type(expr),
                'integration_analysis': self.predict_integration_difficulty(function_str),
                'stability_analysis': self._analyze_numerical_stability(expr),
                'domain_analysis': self._analyze_domain_restrictions(expr),
                'asymptotic_behavior': self._analyze_asymptotic_behavior(expr),
                'recommended_strategies': self._recommend_computation_strategies(function_str, features)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise comportamental: {str(e)}")
            return {
                'function': function_str,
                'error': str(e),
                'basic_analysis': True
            }
    
    def _classify_function_type(self, expr) -> Dict[str, Any]:
        """
        Classifica o tipo da função.
        """
        function_str = str(expr)
        
        types = {
            'polynomial': sp.degree(expr, self.x) is not None and sp.degree(expr, self.x) >= 0,
            'rational': '/' in function_str,
            'trigonometric': any(f in function_str for f in ['sin', 'cos', 'tan']),
            'exponential': 'exp' in function_str,
            'logarithmic': 'log' in function_str,
            'radical': any(f in function_str for f in ['sqrt', 'cbrt']),
            'hyperbolic': any(f in function_str for f in ['sinh', 'cosh', 'tanh']),
            'special': any(f in function_str for f in ['erf', 'gamma', 'beta'])
        }
        
        primary_type = max(types.items(), key=lambda x: x[1])[0] if any(types.values()) else 'unknown'
        
        return {
            'primary_type': primary_type,
            'all_types': [k for k, v in types.items() if v],
            'complexity_level': 'high' if len([k for k, v in types.items() if v]) > 2 else 'medium' if len([k for k, v in types.items() if v]) > 1 else 'low'
        }
    
    def _analyze_numerical_stability(self, expr) -> Dict[str, Any]:
        """
        Analisa estabilidade numérica da função.
        """
        try:
            # Verificar crescimento da função
            limits = {
                'at_infinity': sp.limit(expr, self.x, sp.oo),
                'at_neg_infinity': sp.limit(expr, self.x, -sp.oo),
                'at_zero': sp.limit(expr, self.x, 0)
            }
            
            # Analisar derivadas para detectar oscilações
            first_deriv = diff(expr, self.x)
            second_deriv = diff(first_deriv, self.x)
            
            stability_score = 1.0
            issues = []
            
            # Verificar crescimento explosivo
            if limits['at_infinity'] == sp.oo or limits['at_neg_infinity'] == sp.oo:
                stability_score -= 0.3
                issues.append("Crescimento explosivo detectado")
            
            # Verificar oscilações rápidas
            if any(f in str(expr) for f in ['sin', 'cos', 'tan']):
                # Verificar frequência alta
                if any(str(coef).replace('.', '').isdigit() and float(str(coef)) > 10 
                       for coef in expr.atoms(sp.Number) if str(coef) != '1'):
                    stability_score -= 0.2
                    issues.append("Oscilações de alta frequência")
            
            # Verificar singularidades
            if '/' in str(expr):
                stability_score -= 0.2
                issues.append("Possíveis singularidades")
            
            stability_level = 'high' if stability_score > 0.7 else 'medium' if stability_score > 0.4 else 'low'
            
            return {
                'stability_score': float(max(0, stability_score)),
                'stability_level': stability_level,
                'limits': {k: str(v) for k, v in limits.items()},
                'issues': issues,
                'recommendations': self._generate_stability_recommendations(stability_score, issues)
            }
            
        except Exception as e:
            return {
                'stability_score': 0.5,
                'stability_level': 'unknown',
                'error': str(e)
            }
    
    def _analyze_domain_restrictions(self, expr) -> Dict[str, Any]:
        """
        Analisa restrições de domínio da função.
        """
        try:
            restrictions = []
            critical_points = []
            
            # Verificar logaritmos
            if any(f in str(expr) for f in ['log', 'ln']):
                restrictions.append("Argumentos de logaritmos devem ser positivos")
            
            # Verificar raízes pares
            if 'sqrt' in str(expr):
                restrictions.append("Argumentos de raízes quadradas devem ser não-negativos")
            
            # Verificar divisões por zero
            if '/' in str(expr):
                # Tentar encontrar zeros do denominador
                try:
                    # Esta é uma análise simplificada
                    restrictions.append("Verificar zeros do denominador")
                except:
                    pass
            
            # Verificar funções trigonométricas inversas
            if any(f in str(expr) for f in ['asin', 'acos']):
                restrictions.append("Argumentos de funções trigonométricas inversas devem estar em [-1, 1]")
            
            return {
                'has_restrictions': len(restrictions) > 0,
                'restrictions': restrictions,
                'critical_points': critical_points,
                'domain_type': 'restricted' if restrictions else 'real_numbers'
            }
            
        except Exception as e:
            return {
                'has_restrictions': True,
                'error': str(e),
                'domain_type': 'unknown'
            }
    
    def _analyze_asymptotic_behavior(self, expr) -> Dict[str, Any]:
        """
        Analisa comportamento assintótico.
        """
        try:
            behavior = {}
            
            # Limites no infinito
            behavior['lim_inf'] = str(sp.limit(expr, self.x, sp.oo))
            behavior['lim_neg_inf'] = str(sp.limit(expr, self.x, -sp.oo))
            
            # Assíntotas verticais (verificação simplificada)
            vertical_asymptotes = []
            if '/' in str(expr):
                vertical_asymptotes.append("Possíveis assíntotas verticais em zeros do denominador")
            
            # Assíntotas horizontais
            horizontal_asymptotes = []
            if behavior['lim_inf'] not in ['oo', '-oo', 'zoo', 'nan']:
                horizontal_asymptotes.append(f"y = {behavior['lim_inf']}")
            
            return {
                'vertical_asymptotes': vertical_asymptotes,
                'horizontal_asymptotes': horizontal_asymptotes,
                'limits_at_infinity': {
                    'positive': behavior['lim_inf'],
                    'negative': behavior['lim_neg_inf']
                },
                'growth_type': self._classify_growth_type(behavior)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'growth_type': 'unknown'
            }
    
    def _classify_growth_type(self, behavior: Dict) -> str:
        """
        Classifica tipo de crescimento da função.
        """
        lim_inf = behavior.get('lim_inf', '0')
        lim_neg_inf = behavior.get('lim_neg_inf', '0')
        
        if lim_inf == 'oo' and lim_neg_inf == 'oo':
            return 'exponential_growth'
        elif lim_inf == 'oo' and lim_neg_inf == '-oo':
            return 'unbounded'
        elif lim_inf == '-oo' and lim_neg_inf == 'oo':
            return 'unbounded'
        elif lim_inf in ['0', 'finite'] and lim_neg_inf in ['0', 'finite']:
            return 'bounded'
        else:
            return 'mixed'
    
    def _recommend_computation_strategies(self, function_str: str, features: np.ndarray) -> Dict[str, Any]:
        """
        Recomenda estratégias computacionais baseadas na análise.
        """
        integration_analysis = self.predict_integration_difficulty(function_str)
        
        strategies = {
            'integration': {
                'primary_method': integration_analysis.get('recommended_method', 'simpson'),
                'fallback_methods': self._get_fallback_methods(integration_analysis.get('recommended_method')),
                'adaptive_tolerance': self._recommend_tolerance(integration_analysis.get('difficulty_score', 0.5))
            },
            'visualization': {
                'recommended_resolution': 50 if integration_analysis.get('difficulty_score', 0.5) < 0.5 else 100,
                'adaptive_sampling': integration_analysis.get('difficulty_score', 0.5) > 0.7
            },
            'numerical_methods': {
                'precision_level': 'high' if integration_analysis.get('difficulty_score', 0.5) > 0.7 else 'standard',
                'use_symbolic': integration_analysis.get('difficulty_score', 0.5) < 0.3
            }
        }
        
        return strategies
    
    def _get_fallback_methods(self, primary_method: str) -> List[str]:
        """
        Retorna métodos de fallback baseados no método primário.
        """
        fallback_map = {
            'simpson': ['trapz', 'adaptativo'],
            'trapz': ['simpson', 'adaptativo'],
            'adaptativo': ['simpson', 'romberg'],
            'romberg': ['simpson', 'adaptativo'],
            'monte_carlo': ['adaptativo', 'simpson']
        }
        
        return fallback_map.get(primary_method, ['simpson', 'trapz'])
    
    def _recommend_tolerance(self, difficulty_score: float) -> float:
        """
        Recomenda tolerância baseada na dificuldade.
        """
        if difficulty_score < 0.3:
            return 1e-10
        elif difficulty_score < 0.7:
            return 1e-8
        else:
            return 1e-6
    
    def _generate_stability_recommendations(self, stability_score: float, issues: List[str]) -> List[str]:
        """
        Gera recomendações baseadas na análise de estabilidade.
        """
        recommendations = []
        
        if stability_score < 0.4:
            recommendations.append("Use precisão estendida para cálculos")
            recommendations.append("Considere métodos adaptativos")
        
        if "Crescimento explosivo detectado" in issues:
            recommendations.append("Limite o domínio de integração")
            recommendations.append("Use transformação de variáveis")
        
        if "Oscilações de alta frequência" in issues:
            recommendations.append("Aumente a resolução de sampling")
            recommendations.append("Use métodos especializados para funções oscilatórias")
        
        if "Possíveis singularidades" in issues:
            recommendations.append("Verifique pontos de descontinuidade")
            recommendations.append("Use integração por partes se necessário")
        
        if not recommendations:
            recommendations.append("Função numericamente estável - use métodos padrão")
        
        return recommendations

# Instância global do serviço
ml_prediction_service = MLPredictionService() 