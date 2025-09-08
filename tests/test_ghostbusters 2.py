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
        from src.ghostbusters.recovery_engines import SyntaxRecoveryEngine

        engine = SyntaxRecoveryEngine()
        action = {"target_file": str(test_file)}

        result = await engine.execute_recovery(action)

        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "message")
        assert hasattr(result, "confidence")
        assert hasattr(result, "changes_made")
        assert result.engine_name == "SyntaxRecoveryEngine"

    @pytest.mark.asyncio
    async def test_indentation_fixer(self, test_file: Path) -> None:
        """Test the indentation fixer."""
        from src.ghostbusters.recovery_engines import IndentationFixer

        engine = IndentationFixer()
        action = {"target_file": str(test_file)}

        result = await engine.execute_recovery(action)

        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "message")
        assert hasattr(result, "confidence")
        assert hasattr(result, "changes_made")
        assert result.engine_name == "IndentationFixer"


if __name__ == "__main__":
    pytest.main([__file__])
