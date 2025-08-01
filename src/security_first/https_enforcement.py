#!/usr/bin/env python3
"""
HTTPS Enforcement Module
Addresses critical security blind spot identified by multi-agent analysis.
"""

import ssl
import certifi
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import logging
import socket

logger = logging.getLogger(__name__)


class HTTPSEnforcement:
    """HTTPS enforcement and SSL/TLS configuration for security-first architecture."""
    
    def __init__(self):
        self.ssl_context = self._create_ssl_context()
        self.required_protocols = ['https', 'wss']
        self.min_tls_version = ssl.TLSVersion.TLSv1_2
        
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create secure SSL context with modern TLS configuration."""
        context = ssl.create_default_context(cafile=certifi.where())
        context.minimum_version = self.min_tls_version
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        return context
    
    def validate_https_url(self, url: str) -> bool:
        """Validate that URL uses HTTPS protocol."""
        parsed = urlparse(url)
        return parsed.scheme.lower() in self.required_protocols
    
    def enforce_https_redirect(self, url: str) -> str:
        """Enforce HTTPS redirect for HTTP URLs."""
        if not self.validate_https_url(url):
            # Redirect HTTP to HTTPS
            if url.startswith('http://'):
                return url.replace('http://', 'https://', 1)
        return url
    
    def validate_ssl_certificate(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Validate SSL certificate for given hostname."""
        try:
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with self.ssl_context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        'valid': True,
                        'subject': cert.get('subject'),
                        'issuer': cert.get('issuer'),
                        'version': cert.get('version'),
                        'serial_number': cert.get('serialNumber'),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter')
                    }
        except Exception as e:
            logger.error(f"SSL certificate validation failed for {hostname}: {e}")
            return {'valid': False, 'error': str(e)}
    
    def configure_secure_requests_session(self) -> requests.Session:
        """Configure requests session with secure SSL settings."""
        session = requests.Session()
        session.verify = certifi.where()
        session.mount('https://', requests.adapters.HTTPAdapter())
        return session


class RateLimiting:
    """Rate limiting implementation to prevent abuse."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_limit = 100  # requests per minute
        self.default_window = 60  # seconds
        
    def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Check if user has exceeded rate limit for endpoint."""
        key = f"rate_limit:{user_id}:{endpoint}"
        current = self.redis.get(key)
        
        if current is None:
            self.redis.setex(key, self.default_window, 1)
            return True
        
        count = int(current)
        if count >= self.default_limit:
            return False
        
        self.redis.incr(key)
        return True
    
    def get_remaining_requests(self, user_id: str, endpoint: str) -> int:
        """Get remaining requests for user on endpoint."""
        key = f"rate_limit:{user_id}:{endpoint}"
        current = self.redis.get(key)
        
        if current is None:
            return self.default_limit
        
        return max(0, self.default_limit - int(current))


class CSRFProtection:
    """CSRF protection implementation."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        import hashlib
        import time
        
        data = f"{session_id}:{time.time()}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_csrf_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token for session."""
        expected_token = self.generate_csrf_token(session_id)
        return token == expected_token


class SecurityManager:
    """Comprehensive security manager implementing all critical blind spots."""
    
    def __init__(self, redis_client, secret_key: str):
        self.https_enforcement = HTTPSEnforcement()
        self.rate_limiting = RateLimiting(redis_client)
        self.csrf_protection = CSRFProtection(secret_key)
        
    def validate_request(self, user_id: str, endpoint: str, url: str, 
                        csrf_token: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive request validation."""
        results = {
            'https_valid': self.https_enforcement.validate_https_url(url),
            'rate_limit_valid': self.rate_limiting.check_rate_limit(user_id, endpoint),
            'csrf_valid': True  # Default to True if no CSRF token provided
        }
        
        # Validate CSRF token if provided
        if csrf_token and session_id:
            results['csrf_valid'] = self.csrf_protection.validate_csrf_token(csrf_token, session_id)
        
        # Log security validation results
        logger.info(f"Security validation for user {user_id}: {results}")
        
        return results
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses."""
        return {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }


if __name__ == "__main__":
    # Test HTTPS enforcement
    enforcement = HTTPSEnforcement()
    
    # Test URL validation
    test_urls = [
        "https://api.example.com",
        "http://api.example.com",
        "wss://stream.example.com"
    ]
    
    for url in test_urls:
        is_valid = enforcement.validate_https_url(url)
        print(f"URL: {url} - Valid HTTPS: {is_valid}")
        
        if not is_valid:
            redirected = enforcement.enforce_https_redirect(url)
            print(f"  Redirected to: {redirected}") 