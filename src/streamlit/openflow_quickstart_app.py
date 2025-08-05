#!/usr/bin/env python3


# Pydantic models for validation
class SnowflakeConfig(BaseModel):
    account_url: str = Field(..., description="Snowflake account URL")
    organization: str = Field(..., description="Snowflake organization")
    account: str = Field(..., description="Snowflake account identifier")
    oauth_integration_name: str = Field(..., description="OAuth integration name")
    oauth_client_id: str = Field(..., description="OAuth client ID")
    oauth_client_secret: str = Field(..., description="OAuth client secret")

class OpenFlowConfig(BaseModel):
    data_plane_url: str = Field(..., description="Data plane URL")
    data_plane_uuid: str = Field(..., description="Data plane UUID")
    data_plane_key: str = Field(..., description="Data plane key")
    telemetry_url: str = Field(..., description="Telemetry URL")
    control_plane_url: str = Field(..., description="Control plane URL")

@dataclass
class DeploymentStatus:
    stack_name: str
    status: str
    progress: int
    resources_created: int
    resources_total: int
    error_message: Optional[str] = None
    last_updated: Optional[datetime] = None


    def get_credential_secure(self, key: str) -> Optional[str]:
        """Retrieve credential securely from Redis"""
        encrypted_value = self.redis_client.get(f"credential:{key}")
        if encrypted_value:
            return self.decrypt_credential(encrypted_value.decode())
        return None

    def create_session_token(self, user_id: str, role: str) -> str:
        """Create JWT session token"""
        timeout_minutes = SECURITY_CONFIG["session_timeout_minutes"]
        assert timeout_minutes is not None, "session_timeout_minutes should be set"
        payload = {
            "user_id": user_id,
            "role": role,

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format"""
        import re

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        import html

