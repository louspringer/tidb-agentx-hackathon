"""Tests for the Ghostbusters system."""

from pathlib import Path

import pytest

from src.ghostbusters import GhostbustersOrchestrator, run_ghostbusters
from src.ghostbusters.agents import (
    ArchitectureExpert,
    BuildExpert,
    CodeQualityExpert,
    ModelExpert,
    SecurityExpert,
    TestExpert,
)


class TestGhostbustersOrchestrator:
    """Test the Ghostbusters orchestrator."""

    @pytest.fixture
    def orchestrator(self, tmp_path: Path) -> GhostbustersOrchestrator:
        """Create a test orchestrator."""
        return GhostbustersOrchestrator(str(tmp_path))

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(
        self,
        orchestrator: GhostbustersOrchestrator,
    ) -> None:
        """Test orchestrator initialization."""
        assert orchestrator.project_path is not None
        assert orchestrator.workflow is not None

    @pytest.mark.asyncio
    async def test_run_ghostbusters(self, tmp_path: Path) -> None:
        """Test running the complete Ghostbusters workflow."""
        # Create a simple test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    print('Hello, World!')\n")

        state = await run_ghostbusters(str(tmp_path))

        assert state is not None
        assert hasattr(state, "confidence_score")
        assert hasattr(state, "delusions_detected")
        assert hasattr(state, "errors")


class TestExpertAgents:
    """Test the expert agents."""

    @pytest.fixture
    def test_project(self, tmp_path: Path) -> Path:
        """Create a test project structure."""
        # Create src directory
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create a simple Python file
        test_file = src_dir / "test.py"
        test_file.write_text("def hello():\n    print('Hello, World!')\n")

        return tmp_path

    @pytest.mark.asyncio
    async def test_security_expert(self, test_project: Path) -> None:
        """Test the security expert agent."""
        expert = SecurityExpert()
        result = await expert.detect_delusions(test_project)

        assert result is not None
        assert hasattr(result, "delusions")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommendations")
        assert result.agent_name == "SecurityExpert"

    @pytest.mark.asyncio
    async def test_code_quality_expert(self, test_project: Path) -> None:
        """Test the code quality expert agent."""
        expert = CodeQualityExpert()
        result = await expert.detect_delusions(test_project)

        assert result is not None
        assert hasattr(result, "delusions")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommendations")
        assert result.agent_name == "CodeQualityExpert"

    @pytest.mark.asyncio
    async def test_test_expert(self, test_project: Path) -> None:
        """Test the test expert agent."""
        expert = TestExpert()
        result = await expert.detect_delusions(test_project)

        assert result is not None
        assert hasattr(result, "delusions")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommendations")
        assert result.agent_name == "TestExpert"

    @pytest.mark.asyncio
    async def test_build_expert(self, test_project: Path) -> None:
        """Test the build expert agent."""
        expert = BuildExpert()
        result = await expert.detect_delusions(test_project)

        assert result is not None
        assert hasattr(result, "delusions")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommendations")
        assert result.agent_name == "BuildExpert"

    @pytest.mark.asyncio
    async def test_architecture_expert(self, test_project: Path) -> None:
        """Test the architecture expert agent."""
        expert = ArchitectureExpert()
        result = await expert.detect_delusions(test_project)

        assert result is not None
        assert hasattr(result, "delusions")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommendations")
        assert result.agent_name == "ArchitectureExpert"

    @pytest.mark.asyncio
    async def test_model_expert(self, test_project: Path) -> None:
        """Test the model expert agent."""
        expert = ModelExpert()
        result = await expert.detect_delusions(test_project)

        assert result is not None
        assert hasattr(result, "delusions")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommendations")
        assert result.agent_name == "ModelExpert"


class TestPydanticValidation:
    """Test pydantic model validation."""

    @pytest.mark.asyncio
    async def test_delusion_result_validation(self, tmp_path: Path) -> None:
        """Test DelusionResult pydantic validation."""
        from src.ghostbusters.agents import SecurityExpert

        expert = SecurityExpert()
        result = await expert.detect_delusions(tmp_path)

        # Test pydantic model properties
        assert isinstance(result.delusions, list)
        assert isinstance(result.confidence, float)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.agent_name, str)
        
        # Test confidence validation (should be between 0.0 and 1.0)
        assert 0.0 <= result.confidence <= 1.0
        
        # Test model serialization
        result_dict = result.model_dump()
        assert "delusions" in result_dict
        assert "confidence" in result_dict
        assert "recommendations" in result_dict
        assert "agent_name" in result_dict

    @pytest.mark.asyncio
    async def test_validation_result_validation(self) -> None:
        """Test ValidationResult pydantic validation."""
        from src.ghostbusters.validators import SecurityValidator

        validator = SecurityValidator()
        result = await validator.validate_findings([])

        # Test pydantic model properties
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.confidence, float)
        assert isinstance(result.issues, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.validator_name, str)
        
        # Test confidence validation
        assert 0.0 <= result.confidence <= 1.0
        
        # Test model serialization
        result_dict = result.model_dump()
        assert "is_valid" in result_dict
        assert "confidence" in result_dict
        assert "issues" in result_dict
        assert "recommendations" in result_dict
        assert "validator_name" in result_dict

    @pytest.mark.asyncio
    async def test_recovery_result_validation(self, tmp_path: Path) -> None:
        """Test RecoveryResult pydantic validation."""
        from src.ghostbusters.recovery import SyntaxRecoveryEngine

        engine = SyntaxRecoveryEngine()
        result = await engine.execute_recovery({"target_files": []})

        # Test pydantic model properties
        assert isinstance(result.success, bool)
        assert isinstance(result.message, str)
        assert isinstance(result.confidence, float)
        assert isinstance(result.changes_made, list)
        assert isinstance(result.engine_name, str)
        
        # Test confidence validation
        assert 0.0 <= result.confidence <= 1.0
        
        # Test model serialization
        result_dict = result.model_dump()
        assert "success" in result_dict
        assert "message" in result_dict
        assert "confidence" in result_dict
        assert "changes_made" in result_dict
        assert "engine_name" in result_dict


class TestRecoveryEngines:
    """Test the recovery engines."""

    @pytest.fixture
    def test_file(self, tmp_path: Path) -> Path:
        """Create a test file with issues."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello()\n    print('Hello, World!')\n")
        return test_file

    @pytest.mark.asyncio
    async def test_syntax_recovery_engine(self, test_file: Path) -> None:
        """Test the syntax recovery engine."""
        from src.ghostbusters.recovery import SyntaxRecoveryEngine

        engine = SyntaxRecoveryEngine()
        action = {"target_files": [str(test_file)]}

        result = await engine.execute_recovery(action)

        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "message")
        assert hasattr(result, "confidence")
        assert hasattr(result, "changes_made")
        assert result.engine_name == "SyntaxRecoveryEngine"
        # Test pydantic model validation
        assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_indentation_fixer(self, test_file: Path) -> None:
        """Test the indentation fixer."""
        from src.ghostbusters.recovery import IndentationFixer

        engine = IndentationFixer()
        action = {"target_files": [str(test_file)]}

        result = await engine.execute_recovery(action)

        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "message")
        assert hasattr(result, "confidence")
        assert hasattr(result, "changes_made")
        assert result.engine_name == "IndentationFixer"
        # Test pydantic model validation
        assert 0.0 <= result.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__])
