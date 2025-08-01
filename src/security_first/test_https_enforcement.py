#!/usr/bin/env python3
"""
Tests for HTTPS Enforcement Module
Validates critical security blind spot fixes identified by multi-agent analysis.
"""

import pytest
import unittest.mock as mock
from unittest.mock import MagicMock
import ssl
import socket
from typing import Dict, Any

from https_enforcement import HTTPSEnforcement, RateLimiting, CSRFProtection, SecurityManager


class TestHTTPSEnforcement:
    """Test HTTPS enforcement functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.enforcement = HTTPSEnforcement()
    
    def test_validate_https_url_valid(self):
        """Test validation of valid HTTPS URLs."""
        valid_urls = [
            "https://api.example.com",
            "https://streamlit.app",
            "wss://websocket.example.com",
            "https://localhost:8080"
        ]
        
        for url in valid_urls:
            assert self.enforcement.validate_https_url(url), f"URL should be valid: {url}"
    
    def test_validate_https_url_invalid(self):
        """Test validation of invalid HTTP URLs."""
        invalid_urls = [
            "http://api.example.com",
            "ftp://example.com",
            "ws://websocket.example.com"
        ]
        
        for url in invalid_urls:
            assert not self.enforcement.validate_https_url(url), f"URL should be invalid: {url}"
    
    def test_enforce_https_redirect(self):
        """Test HTTPS redirect enforcement."""
        test_cases = [
            ("http://api.example.com", "https://api.example.com"),
            ("https://api.example.com", "https://api.example.com"),  # No change
            ("wss://websocket.example.com", "wss://websocket.example.com")  # No change
        ]
        
        for input_url, expected_url in test_cases:
            result = self.enforcement.enforce_https_redirect(input_url)
            assert result == expected_url, f"Expected {expected_url}, got {result}"
    
    def test_ssl_context_configuration(self):
        """Test SSL context configuration."""
        context = self.enforcement.ssl_context
        
        # Verify minimum TLS version
        assert context.minimum_version == ssl.TLSVersion.TLSv1_2
        
        # Verify certificate verification
        assert context.verify_mode == ssl.CERT_REQUIRED
        
        # Verify hostname checking
        assert context.check_hostname is True
    
    @mock.patch('socket.create_connection')
    def test_validate_ssl_certificate_success(self, mock_socket):
        """Test successful SSL certificate validation."""
        # Mock successful SSL connection
        mock_socket.return_value.__enter__.return_value = MagicMock()
        
        result = self.enforcement.validate_ssl_certificate("example.com")
        
        # Should attempt to validate
        mock_socket.assert_called_once()
        assert isinstance(result, dict)
    
    @mock.patch('socket.create_connection')
    def test_validate_ssl_certificate_failure(self, mock_socket):
        """Test SSL certificate validation failure."""
        # Mock connection failure
        mock_socket.side_effect = Exception("Connection failed")
        
        result = self.enforcement.validate_ssl_certificate("invalid.example.com")
        
        assert result['valid'] is False
        assert 'error' in result


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.mock_redis = MagicMock()
        self.rate_limiting = RateLimiting(self.mock_redis)
    
    def test_check_rate_limit_first_request(self):
        """Test rate limit check for first request."""
        self.mock_redis.get.return_value = None
        
        result = self.rate_limiting.check_rate_limit("user123", "/api/endpoint")
        
        assert result is True
        self.mock_redis.setex.assert_called_once()
    
    def test_check_rate_limit_under_limit(self):
        """Test rate limit check when under limit."""
        self.mock_redis.get.return_value = "50"  # Under limit of 100
        
        result = self.rate_limiting.check_rate_limit("user123", "/api/endpoint")
        
        assert result is True
        self.mock_redis.incr.assert_called_once()
    
    def test_check_rate_limit_over_limit(self):
        """Test rate limit check when over limit."""
        self.mock_redis.get.return_value = "100"  # At limit
        
        result = self.rate_limiting.check_rate_limit("user123", "/api/endpoint")
        
        assert result is False
        self.mock_redis.incr.assert_not_called()
    
    def test_get_remaining_requests(self):
        """Test getting remaining requests."""
        self.mock_redis.get.return_value = "75"  # 25 requests used
        
        remaining = self.rate_limiting.get_remaining_requests("user123", "/api/endpoint")
        
        assert remaining == 25  # 100 - 75 = 25 remaining


class TestCSRFProtection:
    """Test CSRF protection functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.secret_key = "test_secret_key_123"
        self.csrf_protection = CSRFProtection(self.secret_key)
    
    def test_generate_csrf_token(self):
        """Test CSRF token generation."""
        session_id = "session123"
        
        token = self.csrf_protection.generate_csrf_token(session_id)
        
        assert isinstance(token, str)
        assert len(token) == 64  # SHA-256 hex digest length
    
    def test_validate_csrf_token_valid(self):
        """Test valid CSRF token validation."""
        session_id = "session123"
        token = self.csrf_protection.generate_csrf_token(session_id)
        
        result = self.csrf_protection.validate_csrf_token(token, session_id)
        
        assert result is True
    
    def test_validate_csrf_token_invalid(self):
        """Test invalid CSRF token validation."""
        session_id = "session123"
        invalid_token = "invalid_token_123"
        
        result = self.csrf_protection.validate_csrf_token(invalid_token, session_id)
        
        assert result is False


class TestSecurityManager:
    """Test comprehensive security manager."""
    
    def setup_method(self):
        """Setup test environment."""
        self.mock_redis = MagicMock()
        self.secret_key = "test_secret_key_123"
        self.security_manager = SecurityManager(self.mock_redis, self.secret_key)
    
    def test_validate_request_all_valid(self):
        """Test request validation with all security checks passing."""
        user_id = "user123"
        endpoint = "/api/endpoint"
        url = "https://api.example.com"
        
        # Mock rate limiting to return True
        self.mock_redis.get.return_value = "50"  # Under limit
        
        result = self.security_manager.validate_request(user_id, endpoint, url)
        
        assert result['https_valid'] is True
        assert result['rate_limit_valid'] is True
        assert result['csrf_valid'] is True
    
    def test_validate_request_https_invalid(self):
        """Test request validation with invalid HTTPS."""
        user_id = "user123"
        endpoint = "/api/endpoint"
        url = "http://api.example.com"  # Invalid HTTP
        
        result = self.security_manager.validate_request(user_id, endpoint, url)
        
        assert result['https_valid'] is False
    
    def test_validate_request_rate_limit_exceeded(self):
        """Test request validation with rate limit exceeded."""
        user_id = "user123"
        endpoint = "/api/endpoint"
        url = "https://api.example.com"
        
        # Mock rate limiting to return False
        self.mock_redis.get.return_value = "100"  # At limit
        
        result = self.security_manager.validate_request(user_id, endpoint, url)
        
        assert result['rate_limit_valid'] is False
    
    def test_get_security_headers(self):
        """Test security headers generation."""
        headers = self.security_manager.get_security_headers()
        
        # Verify all required security headers are present
        required_headers = [
            'Strict-Transport-Security',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Content-Security-Policy'
        ]
        
        for header in required_headers:
            assert header in headers, f"Missing security header: {header}"
            assert headers[header] is not None, f"Empty security header: {header}"


class TestIntegration:
    """Integration tests for security components."""
    
    def test_security_manager_integration(self):
        """Test integration of all security components."""
        mock_redis = MagicMock()
        secret_key = "integration_test_key"
        security_manager = SecurityManager(mock_redis, secret_key)
        
        # Test comprehensive validation
        user_id = "test_user"
        endpoint = "/api/test"
        url = "https://api.test.com"
        session_id = "test_session"
        csrf_token = security_manager.csrf_protection.generate_csrf_token(session_id)
        
        # Mock rate limiting
        mock_redis.get.return_value = "50"
        
        result = security_manager.validate_request(
            user_id, endpoint, url, csrf_token, session_id
        )
        
        # All security checks should pass
        assert result['https_valid'] is True
        assert result['rate_limit_valid'] is True
        assert result['csrf_valid'] is True
        
        # Verify security headers
        headers = security_manager.get_security_headers()
        assert len(headers) >= 6  # At least 6 security headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 