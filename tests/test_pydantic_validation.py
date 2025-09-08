"""Comprehensive pydantic validation tests for Ghostbusters models."""

import pytest
from pydantic import ValidationError

from src.ghostbusters.agents.base_expert import DelusionResult
from src.ghostbusters.validators.base_validator import ValidationResult
from src.ghostbusters.recovery_engines.base_recovery_engine import RecoveryResult


class TestDelusionResultValidation:
    """Test DelusionResult pydantic validation."""

    def test_valid_delusion_result(self):
        """Test creating a valid DelusionResult."""
        result = DelusionResult(
            delusions=[{"type": "test", "description": "test delusion"}],
            confidence=0.8,
            recommendations=["fix this", "fix that"],
            agent_name="TestAgent"
        )
        
        assert result.delusions == [{"type": "test", "description": "test delusion"}]
        assert result.confidence == 0.8
        assert result.recommendations == ["fix this", "fix that"]
        assert result.agent_name == "TestAgent"

    def test_confidence_validation_bounds(self):
        """Test confidence validation enforces 0.0-1.0 bounds."""
        # Test confidence > 1.0 raises ValidationError
        with pytest.raises(ValidationError):
            DelusionResult(
                delusions=[],
                confidence=1.5,
                recommendations=[],
                agent_name="TestAgent"
            )
        
        # Test confidence < 0.0 raises ValidationError
        with pytest.raises(ValidationError):
            DelusionResult(
                delusions=[],
                confidence=-0.5,
                recommendations=[],
                agent_name="TestAgent"
            )

    def test_default_values(self):
        """Test default values for optional fields."""
        result = DelusionResult(
            confidence=0.8,
            agent_name="TestAgent"
        )
        
        assert result.delusions == []
        assert result.recommendations == []
        assert result.confidence == 0.8
        assert result.agent_name == "TestAgent"

    def test_serialization(self):
        """Test model serialization to dict."""
        result = DelusionResult(
            delusions=[{"type": "security", "file": "test.py"}],
            confidence=0.9,
            recommendations=["use env vars"],
            agent_name="SecurityExpert"
        )
        
        data = result.model_dump()
        expected = {
            "delusions": [{"type": "security", "file": "test.py"}],
            "confidence": 0.9,
            "recommendations": ["use env vars"],
            "agent_name": "SecurityExpert"
        }
        
        assert data == expected

    def test_deserialization(self):
        """Test model creation from dict."""
        data = {
            "delusions": [{"type": "syntax", "line": 42}],
            "confidence": 0.7,
            "recommendations": ["fix syntax"],
            "agent_name": "CodeQualityExpert"
        }
        
        result = DelusionResult(**data)
        assert result.delusions == [{"type": "syntax", "line": 42}]
        assert result.confidence == 0.7
        assert result.recommendations == ["fix syntax"]
        assert result.agent_name == "CodeQualityExpert"

    def test_json_serialization(self):
        """Test JSON serialization."""
        result = DelusionResult(
            delusions=[{"type": "test"}],
            confidence=0.8,
            recommendations=["test rec"],
            agent_name="TestAgent"
        )
        
        json_str = result.model_dump_json()
        assert isinstance(json_str, str)
        assert "test" in json_str
        assert "0.8" in json_str


class TestValidationResultValidation:
    """Test ValidationResult pydantic validation."""

    def test_valid_validation_result(self):
        """Test creating a valid ValidationResult."""
        result = ValidationResult(
            is_valid=True,
            confidence=0.9,
            issues=["issue1", "issue2"],
            recommendations=["rec1", "rec2"],
            validator_name="TestValidator"
        )
        
        assert result.is_valid is True
        assert result.confidence == 0.9
        assert result.issues == ["issue1", "issue2"]
        assert result.recommendations == ["rec1", "rec2"]
        assert result.validator_name == "TestValidator"

    def test_confidence_validation(self):
        """Test confidence validation."""
        # Test valid confidence
        result = ValidationResult(
            is_valid=True,
            confidence=0.5,
            validator_name="TestValidator"
        )
        assert result.confidence == 0.5
        
        # Test confidence bounds - should raise ValidationError
        with pytest.raises(ValidationError):
            ValidationResult(
                is_valid=True,
                confidence=2.0,
                validator_name="TestValidator"
            )

    def test_default_values(self):
        """Test default values."""
        result = ValidationResult(
            is_valid=False,
            confidence=0.3,
            validator_name="TestValidator"
        )
        
        assert result.issues == []
        assert result.recommendations == []

    def test_serialization(self):
        """Test serialization."""
        result = ValidationResult(
            is_valid=False,
            confidence=0.6,
            issues=["syntax error"],
            recommendations=["fix syntax"],
            validator_name="CodeValidator"
        )
        
        data = result.model_dump()
        assert data["is_valid"] is False
        assert data["confidence"] == 0.6
        assert data["issues"] == ["syntax error"]
        assert data["recommendations"] == ["fix syntax"]
        assert data["validator_name"] == "CodeValidator"


class TestRecoveryResultValidation:
    """Test RecoveryResult pydantic validation."""

    def test_valid_recovery_result(self):
        """Test creating a valid RecoveryResult."""
        result = RecoveryResult(
            success=True,
            message="Recovery completed successfully",
            confidence=0.95,
            changes_made=["fixed syntax", "added imports"],
            engine_name="SyntaxEngine"
        )
        
        assert result.success is True
        assert result.message == "Recovery completed successfully"
        assert result.confidence == 0.95
        assert result.changes_made == ["fixed syntax", "added imports"]
        assert result.engine_name == "SyntaxEngine"

    def test_confidence_validation(self):
        """Test confidence validation."""
        # Test confidence bounds - should raise ValidationError
        with pytest.raises(ValidationError):
            RecoveryResult(
                success=True,
                message="test",
                confidence=1.2,
                engine_name="TestEngine"
            )

    def test_default_values(self):
        """Test default values."""
        result = RecoveryResult(
            success=False,
            message="Failed",
            confidence=0.1,
            engine_name="TestEngine"
        )
        
        assert result.changes_made == []

    def test_serialization(self):
        """Test serialization."""
        result = RecoveryResult(
            success=True,
            message="Fixed issues",
            confidence=0.8,
            changes_made=["change1", "change2"],
            engine_name="RecoveryEngine"
        )
        
        data = result.model_dump()
        assert data["success"] is True
        assert data["message"] == "Fixed issues"
        assert data["confidence"] == 0.8
        assert data["changes_made"] == ["change1", "change2"]
        assert data["engine_name"] == "RecoveryEngine"


class TestModelEquality:
    """Test model equality and comparison operations."""

    def test_delusion_result_equality(self):
        """Test DelusionResult equality."""
        result1 = DelusionResult(
            delusions=[{"type": "test"}],
            confidence=0.8,
            recommendations=["fix"],
            agent_name="TestAgent"
        )
        
        result2 = DelusionResult(
            delusions=[{"type": "test"}],
            confidence=0.8,
            recommendations=["fix"],
            agent_name="TestAgent"
        )
        
        result3 = DelusionResult(
            delusions=[{"type": "different"}],
            confidence=0.8,
            recommendations=["fix"],
            agent_name="TestAgent"
        )
        
        assert result1 == result2
        assert result1 != result3

    def test_validation_result_equality(self):
        """Test ValidationResult equality."""
        result1 = ValidationResult(
            is_valid=True,
            confidence=0.9,
            validator_name="TestValidator"
        )
        
        result2 = ValidationResult(
            is_valid=True,
            confidence=0.9,
            validator_name="TestValidator"
        )
        
        assert result1 == result2

    def test_recovery_result_equality(self):
        """Test RecoveryResult equality."""
        result1 = RecoveryResult(
            success=True,
            message="test",
            confidence=0.8,
            engine_name="TestEngine"
        )
        
        result2 = RecoveryResult(
            success=True,
            message="test",
            confidence=0.8,
            engine_name="TestEngine"
        )
        
        assert result1 == result2


class TestErrorHandling:
    """Test error handling for invalid model data."""

    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValidationError):
            DelusionResult(
                confidence=0.8
                # Missing required agent_name
            )

    def test_invalid_field_types(self):
        """Test validation error for invalid field types."""
        with pytest.raises(ValidationError):
            DelusionResult(
                delusions="not a list",  # Should be list
                confidence=0.8,
                agent_name="TestAgent"
            )

    def test_invalid_confidence_type(self):
        """Test validation error for invalid confidence type."""
        with pytest.raises(ValidationError):
            ValidationResult(
                is_valid=True,
                confidence="not a number",  # Should be float
                validator_name="TestValidator"
            )


if __name__ == "__main__":
    pytest.main([__file__])