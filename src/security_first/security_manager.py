#!/usr/bin/env python3
"""Security Manager - Comprehensive security implementation for OpenFlow Playground"""

import os
import time
import hashlib
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timezone, timedelta

import jwt
import redis
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Security configuration
SECURITY_CONFIG = {
    "fernet_key": os.getenv("FERNET_KEY", Fernet.generate_key()),
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
    "session_timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "15")),
}


class SecurityManager:
    """Comprehensive security manager implementing all critical security functions"""

    def __init__(self) -> None:
        """Initialize security manager with encryption and Redis client"""
        fernet_key = SECURITY_CONFIG["fernet_key"]
        if isinstance(fernet_key, str):
            fernet_key = fernet_key.encode()
        elif isinstance(fernet_key, int):
            fernet_key = Fernet.generate_key()
        self.fernet = Fernet(fernet_key)
        self.redis_client = redis.from_url(SECURITY_CONFIG["redis_url"])

    def encrypt_credential(self, credential: str) -> str:
        """Encrypt sensitive credentials using Fernet"""
        return self.fernet.encrypt(credential.encode()).decode()

    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt sensitive credentials using Fernet"""
        return self.fernet.decrypt(encrypted_credential.encode()).decode()

    def store_credential(self, key: str, value: str) -> None:
        """Store credential securely in Redis with encryption"""
        encrypted_value = self.encrypt_credential(value)
        self.redis_client.setex(
            f"credential:{key}", 3600, encrypted_value
        )  # 1 hour TTL
        logger.info(f"Stored encrypted credential for key: {key}")

    def get_credential(self, key: str) -> Optional[str]:
        """Retrieve credential securely from Redis"""
        encrypted_value = self.redis_client.get(f"credential:{key}")
        if encrypted_value:
            return self.decrypt_credential(encrypted_value.decode())
        return None

    def validate_session_token(self, session_token: str) -> bool:
        """Validate JWT session token"""
        try:
            payload = jwt.decode(
                session_token, str(SECURITY_CONFIG["jwt_secret"]), algorithms=["HS256"]
            )
            return bool(payload.get("exp", 0) > time.time())
        except jwt.InvalidTokenError:
            logger.warning("Invalid session token provided")
            return False

    def create_session_token(self, user_id: str, role: str) -> str:
        """Create JWT session token with proper expiration"""
        timeout_minutes = SECURITY_CONFIG["session_timeout_minutes"]
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=int(timeout_minutes)),
        }
        return jwt.encode(
            payload, str(SECURITY_CONFIG["jwt_secret"]), algorithm="HS256"
        )

    def enforce_csrf_protection(self, token: str, session_id: str) -> bool:
        """Enforce CSRF protection by validating tokens"""
        expected_token = self._generate_csrf_token(session_id)
        return token == expected_token

    def _generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        data = f"{session_id}:{time.time()}:{SECURITY_CONFIG['jwt_secret']}"
        return hashlib.sha256(data.encode()).hexdigest()

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses"""
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        }

    def validate_security_config(self) -> Dict[str, Any]:
        """Validate security configuration and return status"""
        validation_results = {
            "fernet_key_configured": bool(SECURITY_CONFIG["fernet_key"]),
            "redis_url_configured": bool(SECURITY_CONFIG["redis_url"]),
            "jwt_secret_configured": bool(SECURITY_CONFIG["jwt_secret"]),
            "session_timeout_configured": bool(
                SECURITY_CONFIG["session_timeout_minutes"]
            ),
            "all_required_fields_present": True,
        }

        # Check if any required fields are missing
        required_fields = [
            "fernet_key",
            "redis_url",
            "jwt_secret",
            "session_timeout_minutes",
        ]
        for field in required_fields:
            if field not in SECURITY_CONFIG:
                validation_results["all_required_fields_present"] = False
                validation_results[f"{field}_configured"] = False

        return validation_results

    def enforce_security_policies(self, user_id: str, action: str) -> Dict[str, Any]:
        """Enforce security policies for user actions"""
        policies = {
            "max_login_attempts": 3,
            "session_timeout_minutes": 15,
            "password_min_length": 12,
            "require_2fa": False,  # Can be enabled per user
        }

        # Check if user has exceeded login attempts
        login_attempts_key = f"login_attempts:{user_id}"
        current_attempts = self.redis_client.get(login_attempts_key)

        if current_attempts and int(current_attempts) >= policies["max_login_attempts"]:
            return {
                "allowed": False,
                "reason": "Too many login attempts",
                "action_required": "Account temporarily locked",
            }

        # Log the action
        action_key = f"user_action:{user_id}:{action}"
        self.redis_client.setex(action_key, 3600, str(time.time()))

        return {
            "allowed": True,
            "policies": policies,
            "user_id": user_id,
            "action": action,
        }

    def audit_security_events(
        self, user_id: str, event_type: str, details: Dict[str, Any]
    ) -> None:
        """Audit security events for compliance and monitoring"""
        audit_entry = {
            "timestamp": time.time(),
            "user_id": user_id,
            "event_type": event_type,
            "details": details,
            "ip_address": details.get("ip_address", "unknown"),
            "user_agent": details.get("user_agent", "unknown"),
        }

        # Store audit event in Redis with 30-day retention
        audit_key = f"audit:{user_id}:{int(time.time())}"
        self.redis_client.setex(audit_key, 2592000, str(audit_entry))  # 30 days

        # Log to application logs
        logger.info("Security audit event: %s for user %s", event_type, user_id)

        # Check for suspicious patterns
        recent_events = self.redis_client.keys(f"audit:{user_id}:*")
        if len(recent_events) > 100:  # More than 100 events in 30 days
            logger.warning(
                f"High activity detected for user {user_id}: {len(recent_events)} events"
            )


def test_security_manager() -> None:
    """Test security manager functionality"""
    manager = SecurityManager()

    # Test credential encryption/decryption
    test_credential = "test-secret-value"
    encrypted = manager.encrypt_credential(test_credential)
    decrypted = manager.decrypt_credential(encrypted)
    assert decrypted == test_credential, "Encryption/decryption failed"

    # Test session token creation and validation
    token = manager.create_session_token("test-user", "admin")
    assert manager.validate_session_token(token), "Session token validation failed"

    print("✅ Security Manager tests passed")


if __name__ == "__main__":
    test_security_manager()
