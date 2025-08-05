#!/usr/bin/env python3
"""Generated from improved model-driven projection"""

import os
from pydantic import BaseModel, Field, field_validator
from cryptography.fernet import Fernet

SECURITY_CONFIG = {
    "fernet_key": os.getenv("FERNET_KEY", Fernet.generate_key()),
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
    "session_timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "15")),
    "max_login_attempts": int(os.getenv("MAX_LOGIN_ATTEMPTS", "3")),
    "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "12")),
}
AWS_CONFIG = {
    "region": os.getenv("AWS_REGION", "us-east-1"),
    "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
}


class SnowflakeConfig(BaseModel):
    account_url: str = Field(..., description="Snowflake account URL")
    organization: str = Field(..., description="Snowflake organization")
    account: str = Field(..., description="Snowflake account identifier")
    oauth_integration_name: str = Field(..., description="OAuth integration name")
    oauth_client_id: str = Field(..., description="OAuth client ID")
    oauth_client_secret: str = Field(..., description="OAuth client secret")

    @field_validator("account_url")
    def validate_account_url(cls, v: str) -> str:
        """Validate Snowflake account URL format"""
        if not v.startswith("https://") or "snowflakecomputing.com" not in v:
            raise ValueError("Invalid Snowflake account URL format")
        return v