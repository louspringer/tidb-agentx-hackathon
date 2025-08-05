import re
from typing import Any
from urllib.parse import urlparse


@staticmethod
def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def test_input_validator() -> None:
    """Test input validator functionality"""
    validator = InputValidator()
    assert validator.validate_snowflake_url("https://account.snowflakecomputing.com")
    assert not validator.validate_snowflake_url("http://invalid.com")
    assert not validator.validate_snowflake_url("not-a-url")
    assert validator.validate_uuid("123e4567-e89b-12d3-a456-426614174000")
    assert not validator.validate_uuid("not-a-uuid")
    assert validator.validate_oauth_credentials(
        {"client_id": "test_id", "client_secret": "test_secret"},
    )
    assert not validator.validate_oauth_credentials(
        {"client_id": "", "client_secret": ""},
    )
    print("✅ Input Validator tests passed")


@staticmethod
def validate_input(input_str: str, input_type: str = "text") -> bool:
    """Validate general input based on type"""
    if not input_str or not isinstance(input_str, str):
        return False
    if input_type == "text":
        return len(input_str.strip()) > 0
    if input_type == "email":
        return InputValidator.validate_email(input_str)
    if input_type == "url":
        return InputValidator.validate_url(input_str)
    if input_type == "phone":
        return InputValidator.validate_phone_number(input_str)
    if input_type == "uuid":
        return InputValidator.validate_uuid(input_str)
    return len(input_str.strip()) > 0


@staticmethod
def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


@staticmethod
def validate_password_strength(password: str) -> dict[str, Any]:
    """Validate password strength"""
    checks = {
        "length": len(password) >= 8,
        "uppercase": bool(re.search("[A-Z]", password)),
        "lowercase": bool(re.search("[a-z]", password)),
        "digit": bool(re.search("\\d", password)),
        "special": bool(re.search('[!@#$%^&*(),.?\\":{}|<>]', password)),
    }
    checks["strong"] = all(checks.values())
    return checks


@staticmethod
def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    digits_only = re.sub("\\D", "", phone)
    return len(digits_only) >= 10


@staticmethod
def validate_credit_card(card_number: str) -> bool:
    """Validate credit card number using Luhn algorithm"""
    card_number = re.sub("\\s+|-", "", card_number)
    if not card_number.isdigit():
        return False
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    return checksum % 10 == 0


@staticmethod
def validate_json_schema(data: dict[str, Any], schema: dict[str, Any]) -> bool:
    """Validate data against JSON schema"""
    try:
        from jsonschema import validate

        validate(instance=data, schema=schema)
        return True
    except ImportError:
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
        "(\\b(union|select|insert|update|delete|drop|create|alter)\\b)",
        "(--|#|/\\*|\\*/)",
        "(\\b(exec|execute|script)\\b)",
        "(\\b(xp_|sp_)\\b)",
    ]
    sql_lower = sql.lower()
    return all(not re.search(pattern, sql_lower) for pattern in dangerous_patterns)


@staticmethod
def validate_xss_safe(text: str) -> bool:
    """Check if text is safe from XSS attacks"""
    dangerous_patterns = [
        "<script[^>]*>.*?</script>",
        "javascript:",
        "on\\w+\\s*=",
        "<iframe[^>]*>",
        "<object[^>]*>",
        "<embed[^>]*>",
    ]
    text_lower = text.lower()
    return all(not re.search(pattern, text_lower) for pattern in dangerous_patterns)


@staticmethod
def validate_file_upload(
    filename: str,
    file_size: int,
    allowed_extensions: list[str],
    max_size_mb: int = 10,
) -> dict[str, Any]:
    """Validate file upload for security and size constraints"""
    validation_result: dict[str, Any] = {"valid": True, "errors": [], "warnings": []}
    if not InputValidator.validate_file_extension(filename, allowed_extensions):
        validation_result["valid"] = False
        validation_result["errors"].append(
            f"File extension not allowed. Allowed: {allowed_extensions}",
        )
    if not InputValidator.validate_file_size(file_size, max_size_mb):
        validation_result["valid"] = False
        validation_result["errors"].append(f"File too large. Max size: {max_size_mb}MB")
    dangerous_extensions = ["exe", "bat", "cmd", "com", "pi", "scr", "vbs", "js"]
    file_ext = filename.lower().split(".")[-1] if "." in filename else ""
    if file_ext in dangerous_extensions:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Dangerous file type: {file_ext}")
    suspicious_patterns = ["\\.\\./", "\\.\\.\\\\", "cmd\\.", "\\.tmp$"]
    for pattern in suspicious_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Suspicious filename pattern: {pattern}",
            )
            break
    return validation_result
