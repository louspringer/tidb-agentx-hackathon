#!/usr/bin/env python3
"""Input Validator - Comprehensive input validation for OpenFlow Playground"""

import re
import html
from typing import Dict, Any
from urllib.parse import urlparse


class InputValidator:
    """Comprehensive input validation and sanitization"""

    @staticmethod
    def validate_input(input_str: str, input_type: str = "text") -> bool:
        """Validate general input based on type"""
        if not input_str or not isinstance(input_str, str):
            return False

        if input_type == "text":
            return len(input_str.strip()) > 0
        elif input_type == "email":
            return InputValidator.validate_email(input_str)
        elif input_type == "url":
            return InputValidator.validate_url(input_str)
        elif input_type == "phone":
            return InputValidator.validate_phone_number(input_str)
        elif input_type == "uuid":
            return InputValidator.validate_uuid(input_str)
        else:
            return len(input_str.strip()) > 0

    @staticmethod
    def validate_snowflake_url(url: str) -> bool:
        """Validate Snowflake account URL format"""
        return url.startswith("https://") and "snowflakecomputing.com" in url

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format"""
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(uuid_pattern, uuid_str))

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        return html.escape(input_str.strip())

    @staticmethod
    def validate_oauth_credentials(credentials: Dict[str, str]) -> bool:
        """Validate OAuth credentials format from a dictionary"""
        client_id = credentials.get("client_id", "")
        client_secret = credentials.get("client_secret", "")
        # Accept test values or real OAuth credentials (minimum 8 chars)
        return len(client_id) >= 8 and len(client_secret) >= 8

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        checks = {
            "length": len(password) >= 8,
            "uppercase": bool(re.search(r"[A-Z]", password)),
            "lowercase": bool(re.search(r"[a-z]", password)),
            "digit": bool(re.search(r"\d", password)),
            "special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)),
        }
        checks["strong"] = all(checks.values())
        return checks

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r"\D", "", phone)
        return len(digits_only) >= 10

    @staticmethod
    def validate_credit_card(card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm"""
        # Remove spaces and dashes
        card_number = re.sub(r"\s+|-", "", card_number)

        if not card_number.isdigit():
            return False

        # Luhn algorithm
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]

        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))

        return checksum % 10 == 0

    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate data against JSON schema"""
        try:
            from jsonschema import validate  # type: ignore

            validate(instance=data, schema=schema)
            return True
        except ImportError:
            # Fallback validation if jsonschema not available
            return isinstance(data, dict)

    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        file_ext = filename.lower().split(".")[-1] if "." in filename else ""
        return file_ext in [ext.lower() for ext in allowed_extensions]

    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int) -> bool:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes

    @staticmethod
    def validate_sql_injection_safe(sql: str) -> bool:
        """Check if SQL string is safe from injection"""
        dangerous_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(exec|execute|script)\b)",
            r"(\b(xp_|sp_)\b)",
        ]

        sql_lower = sql.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_lower):
                return False
        return True

    @staticmethod
    def validate_xss_safe(text: str) -> bool:
        """Check if text is safe from XSS attacks"""
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]

        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, text_lower):
                return False
        return True

    @staticmethod
    def validate_file_upload(
        filename: str,
        file_size: int,
        allowed_extensions: list[str],
        max_size_mb: int = 10,
    ) -> Dict[str, Any]:
        """Validate file upload for security and size constraints"""
        validation_result: Dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Check file extension
        if not InputValidator.validate_file_extension(filename, allowed_extensions):
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"File extension not allowed. Allowed: {allowed_extensions}"
            )

        # Check file size
        if not InputValidator.validate_file_size(file_size, max_size_mb):
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"File too large. Max size: {max_size_mb}MB"
            )

        # Check for dangerous file types
        dangerous_extensions = ["exe", "bat", "cmd", "com", "pif", "scr", "vbs", "js"]
        file_ext = filename.lower().split(".")[-1] if "." in filename else ""
        if file_ext in dangerous_extensions:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Dangerous file type: {file_ext}")

        # Check filename for suspicious patterns
        suspicious_patterns = [
            r"\.\./",  # Path traversal
            r"\.\.\\",  # Windows path traversal
            r"cmd\.",  # Command files
            r"\.tmp$",  # Temporary files
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Suspicious filename pattern: {pattern}"
                )
                break

        return validation_result


def test_input_validator() -> None:
    """Test input validator functionality"""
    validator = InputValidator()

    # Test URL validation
    assert validator.validate_snowflake_url("https://account.snowflakecomputing.com")
    assert not validator.validate_snowflake_url("http://invalid.com")
    assert not validator.validate_snowflake_url("not-a-url")

    # Test UUID validation
    assert validator.validate_uuid("123e4567-e89b-12d3-a456-426614174000")
    assert not validator.validate_uuid("not-a-uuid")

    # Test OAuth validation
    assert validator.validate_oauth_credentials(
        {"client_id": "test_id", "client_secret": "test_secret"}
    )
    assert not validator.validate_oauth_credentials(
        {"client_id": "", "client_secret": ""}
    )

    print("✅ Input Validator tests passed")


if __name__ == "__main__":
    test_input_validator()
