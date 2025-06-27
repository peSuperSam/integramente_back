import re
import sympy as sp
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """
    Resultado da validação de entrada.
    """
    is_valid: bool
    cleaned_input: str
    issues: List[str]
    warnings: List[str]
    security_score: int  # 0-100, onde 100 é mais seguro
    recommendations: List[str]

class AdvancedInputValidator:
    """
    Validador avançado de entrada para funções matemáticas.
    """
    
    # Padrões suspeitos que podem indicar tentativas de ataque
    SUSPICIOUS_PATTERNS = [
        r'__[a-zA-Z_]+__',  # Métodos especiais Python
        r'import\s+',       # Tentativas de import
        r'exec\s*\(',       # Execução de código
        r'eval\s*\(',       # Avaliação de código
        r'open\s*\(',       # Abertura de arquivos
        r'file\s*\(',       # Manipulação de arquivos
        r'subprocess',      # Execução de subprocessos
        r'os\.',            # Módulo os
        r'sys\.',           # Módulo sys
        r'\..*\(',          # Chamadas de método suspeitas
        r'[\'\"]{3,}',      # Strings longas
        r'\n|\r',           # Quebras de linha
        r';',               # Separadores de comando
        r'\\x[0-9a-fA-F]{2}',  # Caracteres hexadecimais
    ]
    
    # Funções matemáticas permitidas
    ALLOWED_FUNCTIONS = {
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
        'asin', 'acos', 'atan', 'atan2',
        'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
        'exp', 'log', 'ln', 'log10', 'log2',
        'sqrt', 'cbrt', 'abs', 'sign',
        'floor', 'ceil', 'round',
        'pi', 'e', 'I', 'oo', 'inf',
        'factorial', 'gamma', 'beta',
        'erf', 'erfc', 'erfi',
        'Si', 'Ci', 'Ei', 'li',
        'besseli', 'besselj', 'besselk', 'bessely',
        'max', 'min', 'sum', 'prod'
    }
    
    # Operadores permitidos
    ALLOWED_OPERATORS = {'+', '-', '*', '/', '^', '**', '(', ')', '[', ']', ',', '.'}
    
    # Constantes permitidas
    ALLOWED_CONSTANTS = {'pi', 'e', 'I', 'oo', 'inf'}
    
    @staticmethod
    def validate_function_input(input_str: str, max_length: int = 500) -> ValidationResult:
        """
        Valida entrada de função matemática.
        """
        issues = []
        warnings = []
        recommendations = []
        security_score = 100
        
        # Verificação básica de tamanho
        if len(input_str) > max_length:
            issues.append(f"Entrada muito longa (máximo: {max_length} caracteres)")
            security_score -= 30
        
        if len(input_str.strip()) == 0:
            issues.append("Entrada vazia")
            return ValidationResult(False, "", issues, warnings, 0, recommendations)
        
        # Limpar entrada básica
        cleaned = input_str.strip()
        
        # Verificar padrões suspeitos
        for pattern in AdvancedInputValidator.SUSPICIOUS_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                issues.append(f"Padrão suspeito detectado: {pattern}")
                security_score -= 50
        
        # Verificar caracteres não ASCII suspeitos
        if not all(ord(c) < 127 for c in cleaned):
            non_ascii = [c for c in cleaned if ord(c) >= 127]
            if non_ascii:
                warnings.append(f"Caracteres não-ASCII detectados: {non_ascii[:5]}")
                security_score -= 10
        
        # Normalizar entrada
        cleaned = AdvancedInputValidator._normalize_function(cleaned)
        
        # Verificar balanceamento de parênteses
        if not AdvancedInputValidator._check_parentheses_balance(cleaned):
            issues.append("Parênteses não balanceados")
            security_score -= 20
        
        # Verificar funções e operadores permitidos
        validation_result = AdvancedInputValidator._validate_tokens(cleaned)
        if not validation_result['valid']:
            issues.extend(validation_result['issues'])
            security_score -= 30
        
        warnings.extend(validation_result.get('warnings', []))
        
        # Verificar complexidade
        complexity_result = AdvancedInputValidator._analyze_complexity(cleaned)
        if complexity_result['score'] > 1000:
            warnings.append("Função muito complexa - pode afetar performance")
            security_score -= 5
        
        # Gerar recomendações
        recommendations = AdvancedInputValidator._generate_recommendations(
            cleaned, complexity_result, validation_result
        )
        
        # Determinar se é válido
        is_valid = len(issues) == 0 and security_score >= 50
        
        return ValidationResult(
            is_valid=is_valid,
            cleaned_input=cleaned,
            issues=issues,
            warnings=warnings,
            security_score=max(0, security_score),
            recommendations=recommendations
        )
    
    @staticmethod
    def validate_numeric_input(value: Any, min_val: float = None, max_val: float = None,
                             param_name: str = "valor") -> ValidationResult:
        """
        Valida entrada numérica.
        """
        issues = []
        warnings = []
        recommendations = []
        security_score = 100
        
        try:
            # Tentar converter para float
            if isinstance(value, str):
                if value.lower() in ['inf', 'infinity', '+inf']:
                    cleaned_value = float('inf')
                elif value.lower() in ['-inf', '-infinity']:
                    cleaned_value = float('-inf')
                else:
                    cleaned_value = float(value)
            else:
                cleaned_value = float(value)
            
            # Verificar se é NaN
            if str(cleaned_value).lower() == 'nan':
                issues.append(f"{param_name} não pode ser NaN")
                security_score -= 50
            
            # Verificar limites
            if min_val is not None and cleaned_value < min_val:
                issues.append(f"{param_name} deve ser >= {min_val}")
                security_score -= 30
            
            if max_val is not None and cleaned_value > max_val:
                issues.append(f"{param_name} deve ser <= {max_val}")
                security_score -= 30
            
            # Verificar valores extremos
            if abs(cleaned_value) > 1e10:
                warnings.append(f"{param_name} muito grande - pode causar instabilidade numérica")
                security_score -= 10
            
            is_valid = len(issues) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                cleaned_input=str(cleaned_value),
                issues=issues,
                warnings=warnings,
                security_score=security_score,
                recommendations=recommendations
            )
            
        except (ValueError, TypeError) as e:
            issues.append(f"{param_name} deve ser um número válido: {str(e)}")
            return ValidationResult(False, "", issues, warnings, 0, recommendations)
    
    @staticmethod
    def _normalize_function(func_str: str) -> str:
        """
        Normaliza função para formato padrão.
        """
        # Remover espaços extras
        normalized = re.sub(r'\s+', '', func_str)
        
        # Substituições padrão
        substitutions = {
            '^': '**',
            'sen': 'sin',
            'tg': 'tan',
            'cotg': 'cot',
            'ln': 'log',
            'lg': 'log10',
            'arcsin': 'asin',
            'arccos': 'acos',
            'arctan': 'atan',
            'arctg': 'atan',
        }
        
        for old, new in substitutions.items():
            normalized = normalized.replace(old, new)
        
        return normalized
    
    @staticmethod
    def _check_parentheses_balance(func_str: str) -> bool:
        """
        Verifica se parênteses estão balanceados.
        """
        stack = []
        pairs = {'(': ')', '[': ']', '{': '}'}
        
        for char in func_str:
            if char in pairs:
                stack.append(char)
            elif char in pairs.values():
                if not stack:
                    return False
                if pairs[stack.pop()] != char:
                    return False
        
        return len(stack) == 0
    
    @staticmethod
    def _validate_tokens(func_str: str) -> Dict[str, Any]:
        """
        Valida tokens na função.
        """
        result = {'valid': True, 'issues': [], 'warnings': []}
        
        # Extrair tokens (números, variáveis, funções, operadores)
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|[0-9]*\.?[0-9]+|[+\-*/^()[\],.]', func_str)
        
        for token in tokens:
            # Verificar se é número
            if re.match(r'^[0-9]*\.?[0-9]+$', token):
                continue
            
            # Verificar se é variável permitida (x, y, z, t)
            if re.match(r'^[xyzt]$', token):
                continue
            
            # Verificar se é operador permitido
            if token in AdvancedInputValidator.ALLOWED_OPERATORS:
                continue
            
            # Verificar se é função permitida
            if token.lower() in AdvancedInputValidator.ALLOWED_FUNCTIONS:
                continue
            
            # Verificar se é constante permitida
            if token.lower() in AdvancedInputValidator.ALLOWED_CONSTANTS:
                continue
            
            # Token não reconhecido
            result['issues'].append(f"Token não permitido: {token}")
            result['valid'] = False
        
        return result
    
    @staticmethod
    def _analyze_complexity(func_str: str) -> Dict[str, Any]:
        """
        Analisa complexidade da função.
        """
        try:
            # Contar diferentes tipos de elementos
            operators = len(re.findall(r'[+\-*/^]', func_str))
            functions = len(re.findall(r'[a-zA-Z]+\(', func_str))
            parentheses = len(re.findall(r'[()]', func_str))
            
            # Calcular score de complexidade
            complexity_score = operators * 2 + functions * 5 + parentheses
            
            return {
                'score': complexity_score,
                'operators': operators,
                'functions': functions,
                'parentheses': parentheses
            }
            
        except Exception:
            return {'score': 999, 'error': True}
    
    @staticmethod
    def _generate_recommendations(func_str: str, complexity: Dict, validation: Dict) -> List[str]:
        """
        Gera recomendações baseadas na análise.
        """
        recommendations = []
        
        # Recomendações de complexidade
        if complexity.get('score', 0) > 500:
            recommendations.append("Considere simplificar a função para melhor performance")
        
        if complexity.get('functions', 0) > 10:
            recommendations.append("Muitas funções aninhadas - verifique se há simplificações possíveis")
        
        # Recomendações de formatação
        if '**' not in func_str and '^' in func_str:
            recommendations.append("Use ** ao invés de ^ para potenciação")
        
        if 'ln(' in func_str:
            recommendations.append("Use log() ao invés de ln() para logaritmo natural")
        
        if not recommendations:
            recommendations.append("Função bem formatada")
        
        return recommendations

# Instância global do validador
input_validator = AdvancedInputValidator() 