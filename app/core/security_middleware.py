import time
import hashlib
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Callable, Any
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Sistema de rate limiting baseado em sliding window.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self.blocked_ips = defaultdict(float)  # IP -> tempo_de_desbloqueio
        
    def is_allowed(self, client_ip: str) -> bool:
        """
        Verifica se o IP pode fazer uma requisição.
        """
        current_time = time.time()
        
        # Verificar se IP está bloqueado
        if client_ip in self.blocked_ips:
            if current_time < self.blocked_ips[client_ip]:
                return False
            else:
                # Desbloquear IP
                del self.blocked_ips[client_ip]
        
        # Limpar requisições antigas
        client_requests = self.requests[client_ip]
        while client_requests and client_requests[0] < current_time - self.window_seconds:
            client_requests.popleft()
        
        # Verificar limite
        if len(client_requests) >= self.max_requests:
            # Bloquear IP por 5 minutos
            self.blocked_ips[client_ip] = current_time + 300
            logger.warning(f"IP {client_ip} bloqueado por excesso de requisições")
            return False
        
        # Registrar requisição
        client_requests.append(current_time)
        return True
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """
        Retorna o número de requisições restantes.
        """
        current_time = time.time()
        client_requests = self.requests[client_ip]
        
        # Limpar requisições antigas
        while client_requests and client_requests[0] < current_time - self.window_seconds:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))

class SecurityMonitor:
    """
    Monitor de segurança para detectar padrões suspeitos.
    """
    
    def __init__(self):
        self.suspicious_patterns = {
            'rapid_requests': defaultdict(list),  # IP -> lista de timestamps
            'error_patterns': defaultdict(int),   # IP -> contador de erros
            'payload_sizes': defaultdict(list),   # IP -> lista de tamanhos
            'unusual_endpoints': defaultdict(set) # IP -> set de endpoints acessados
        }
        
    def analyze_request(self, client_ip: str, request: Request) -> Dict[str, Any]:
        """
        Analisa requisição para padrões suspeitos.
        """
        current_time = time.time()
        analysis = {
            'risk_score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # Analisar frequência de requisições
        rapid_requests = self.suspicious_patterns['rapid_requests'][client_ip]
        rapid_requests.append(current_time)
        
        # Manter apenas requisições dos últimos 10 segundos
        rapid_requests[:] = [t for t in rapid_requests if t > current_time - 10]
        
        if len(rapid_requests) > 10:  # Mais de 10 req/10s
            analysis['risk_score'] += 30
            analysis['issues'].append("Frequência de requisições muito alta")
        
        # Analisar tamanho do payload
        content_length = request.headers.get('content-length', '0')
        try:
            payload_size = int(content_length)
            self.suspicious_patterns['payload_sizes'][client_ip].append(payload_size)
            
            if payload_size > 10000:  # Payload > 10KB
                analysis['risk_score'] += 20
                analysis['issues'].append("Payload muito grande")
        except ValueError:
            pass
        
        # Analisar endpoints acessados
        endpoint = str(request.url.path)
        self.suspicious_patterns['unusual_endpoints'][client_ip].add(endpoint)
        
        # Se acessou muitos endpoints diferentes rapidamente
        if len(self.suspicious_patterns['unusual_endpoints'][client_ip]) > 5:
            analysis['risk_score'] += 15
            analysis['issues'].append("Muitos endpoints diferentes acessados")
        
        return analysis

class SecurityMiddleware:
    """
    Middleware de segurança principal.
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests=60, window_seconds=60)  # 60 req/min
        self.security_monitor = SecurityMonitor()
        self.blocked_ips = set()
        
    async def __call__(self, request: Request, call_next: Callable) -> Any:
        """
        Processa requisição através do middleware de segurança.
        """
        # Obter IP do cliente
        client_ip = self._get_client_ip(request)
        
        # Verificar se IP está bloqueado permanentemente
        if client_ip in self.blocked_ips:
            logger.warning(f"Requisição bloqueada de IP banido: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "IP bloqueado por violações de segurança"}
            )
        
        # Verificar rate limiting
        if not self.rate_limiter.is_allowed(client_ip):
            remaining = self.rate_limiter.get_remaining_requests(client_ip)
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Muitas requisições",
                    "message": "Limite de requisições excedido",
                    "remaining_requests": remaining,
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Análise de segurança
        security_analysis = self.security_monitor.analyze_request(client_ip, request)
        
        # Se risk score muito alto, bloquear
        if security_analysis['risk_score'] > 50:
            logger.warning(f"IP {client_ip} com risk score alto: {security_analysis['risk_score']}")
            logger.warning(f"Issues: {security_analysis['issues']}")
            
            # Adicionar à lista de bloqueados se score muito alto
            if security_analysis['risk_score'] > 80:
                self.blocked_ips.add(client_ip)
                logger.error(f"IP {client_ip} banido permanentemente")
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Comportamento suspeito detectado",
                    "risk_score": security_analysis['risk_score'],
                    "issues": security_analysis['issues']
                }
            )
        
        # Processar requisição normalmente
        try:
            # Adicionar headers de segurança
            start_time = time.time()
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # Adicionar headers de segurança
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["X-Rate-Limit-Remaining"] = str(self.rate_limiter.get_remaining_requests(client_ip))
            response.headers["X-Processing-Time"] = f"{processing_time:.4f}"
            
            # Log para requisições lentas
            if processing_time > 5.0:
                logger.warning(f"Requisição lenta detectada: {processing_time:.2f}s para {client_ip}")
            
            return response
            
        except Exception as e:
            # Registrar erro de segurança
            self.security_monitor.suspicious_patterns['error_patterns'][client_ip] += 1
            
            logger.error(f"Erro processando requisição de {client_ip}: {str(e)}")
            
            # Se muitos erros, aumentar suspeita
            if self.security_monitor.suspicious_patterns['error_patterns'][client_ip] > 5:
                logger.warning(f"Muitos erros do IP {client_ip} - possível ataque")
            
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extrai IP do cliente considerando proxies.
        """
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Pegar primeiro IP da lista
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback para IP direto
        return request.client.host if request.client else "unknown"
    
    def get_security_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de segurança.
        """
        return {
            "blocked_ips_count": len(self.blocked_ips),
            "rate_limited_ips": len(self.rate_limiter.requests),
            "monitored_ips": len(self.security_monitor.suspicious_patterns['rapid_requests']),
            "blocked_ips": list(self.blocked_ips),
            "high_risk_ips": [
                ip for ip, requests in self.security_monitor.suspicious_patterns['rapid_requests'].items()
                if len(requests) > 5
            ]
        }
    
    def unblock_ip(self, ip: str) -> bool:
        """
        Remove IP da lista de bloqueados.
        """
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"IP {ip} desbloqueado manualmente")
            return True
        return False

# Instância global do middleware
security_middleware = SecurityMiddleware() 