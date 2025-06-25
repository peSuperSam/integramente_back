from typing import Dict, List

class ExemplosService:
    
    @staticmethod
    def obter_exemplos() -> Dict[str, List[str]]:
        """
        Retorna exemplos organizados por categoria.
        """
        exemplos = {
            "basicas": [
                "x",
                "x^2", 
                "x^3",
                "2*x",
                "x^2 + 3*x",
                "x^3 - 2*x + 1"
            ],
            "trigonometricas": [
                "sin(x)",
                "cos(x)", 
                "tan(x)",
                "sin(x)^2",
                "cos(2*x)",
                "sin(x)*cos(x)"
            ],
            "exponenciais": [
                "exp(x)",
                "2^x",
                "e^(-x)",
                "x*exp(x)",
                "exp(x^2)"
            ],
            "logaritmicas": [
                "log(x)",
                "ln(x)",
                "log(x^2)",
                "x*log(x)",
                "log(x)/x"
            ],
            "radicais": [
                "sqrt(x)",
                "sqrt(x^2 + 1)",
                "x*sqrt(x)",
                "1/sqrt(x)",
                "sqrt(1 - x^2)"
            ],
            "racionais": [
                "1/x",
                "1/x^2",
                "x/(x^2 + 1)",
                "(x + 1)/(x - 1)",
                "x^2/(x + 1)"
            ]
        }
        
        return exemplos
    
    @staticmethod
    def contar_total_exemplos(exemplos: Dict[str, List[str]]) -> int:
        """
        Conta o total de exemplos em todas as categorias.
        """
        return sum(len(lista) for lista in exemplos.values()) 