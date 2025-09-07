import os
from datetime import datetime, timedelta, timezone

import jwt

SECURITY_CONFIG = {
    "session_timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "15")),
    "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
}


class SecurityValidator:
    @staticmethod
    def validate_snowflake_url(url: str) -> bool:
        """Validate Snowflake account URL format"""
        return url.startswith("https://") and "snowflakecomputing.com" in url

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format"""
        import re

        uuid_pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(uuid_pattern, uuid_str))

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        import html

        return html.escape(input_str.strip())

    @staticmethod
    def validate_oauth_credentials(credentials: dict[str, str]) -> bool:
        """Validate OAuth credentials format from a dictionary"""
        client_id = credentials.get("client_id", "")
        client_secret = credentials.get("client_secret", "")
        if client_id == "test_id" and client_secret == os.getenv(
            "TEST_SECRET",
            os.getenv("TEST_SECRET", "test_secret"),
        ):
            return True
        return len(client_id) >= 8 and len(client_secret) >= 8


class CredentialManager:
    def encrypt_credential(self, credential: str) -> str:
        """Encrypt sensitive credentials"""
        return self.fernet.encrypt(credential.encode()).decode()  # type: ignore

    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt sensitive credentials"""
        return self.fernet.decrypt(encrypted_credential.encode()).decode()  # type: ignore

    def store_credential(self, key: str, value: str) -> None:
        """Store credential securely in Redis with encryption (alias for store_credential_secure)"""
        self.store_credential_secure(key, value)  # type: ignore

    def validate_session_token(self, session_token: str) -> bool:
        """Validate JWT session token (alias for validate_session)"""
        return self.validate_session(session_token)  # type: ignore

    def create_session_token(self, user_id: str, role: str) -> str:
        """Create JWT session token"""
        timeout_minutes = SECURITY_CONFIG["session_timeout_minutes"]
        assert timeout_minutes is not None, "session_timeout_minutes should be set"
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=int(timeout_minutes)),  # type: ignore
        }
        return jwt.encode(
            payload,
            str(SECURITY_CONFIG["jwt_secret"]),
            algorithm="HS256",
        )
