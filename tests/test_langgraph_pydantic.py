"""Test LangGraph workflow with pydantic state management."""

from pathlib import Path

import pytest

from src.ghostbusters import GhostbustersOrchestrator
from src.ghostbusters.state import GhostbustersState


class TestLangGraphPydanticIntegration:
    """Test LangGraph workflow with pydantic state."""

    @pytest.fixture
    def test_project(self, tmp_path: Path) -> Path:
        """Create a test project."""
        # Create a simple Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    print('Hello, World!')\n")
        return tmp_path

    @pytest.fixture
    def orchestrator(self, test_project: Path) -> GhostbustersOrchestrator:
        """Create orchestrator with test project."""
        return GhostbustersOrchestrator(str(test_project))

    @pytest.mark.asyncio
    async def test_orchestrator_initialization_with_pydantic_state(
        self, 
        orchestrator: GhostbustersOrchestrator
    ) -> None:
        """Test orchestrator initialization with pydantic state."""
        assert orchestrator.project_path is not None
        assert orchestrator.workflow is not None
        
        # Test that initial state is pydantic model
        initial_state = GhostbustersState(
            project_path=orchestrator.project_path,
            confidence_score=0.0,
            delusions_detected=[],
            validation_results=[],
            recovery_results=[],
            errors=[],
            warnings=[],
            metadata={}
        )
        
        # Verify it's a pydantic model
        assert hasattr(initial_state, 'model_dump')
        assert hasattr(initial_state, 'model_validate')
        
        # Test serialization
        state_dict = initial_state.model_dump()
        assert 'project_path' in state_dict
        assert 'confidence_score' in state_dict
        assert 'delusions_detected' in state_dict

    @pytest.mark.asyncio
    async def test_state_transitions_with_pydantic(
        self,
        orchestrator: GhostbustersOrchestrator
    ) -> None:
        """Test state transitions between workflow nodes with pydantic."""
        # Create initial pydantic state
        initial_state = GhostbustersState(
            project_path=orchestrator.project_path,
            confidence_score=0.0,
            delusions_detected=[],
            validation_results=[],
            recovery_results=[],
            errors=[],
            warnings=[],
            metadata={"test": "value"}
        )
        
        # Test state serialization for LangGraph
        serialized = initial_state.model_dump()
        assert isinstance(serialized, dict)
        assert serialized['confidence_score'] == 0.0
        assert serialized['metadata']['test'] == "value"
        
        # Test state deserialization from LangGraph
        restored_state = GhostbustersState(**serialized)
        assert restored_state.project_path == initial_state.project_path
        assert restored_state.confidence_score == initial_state.confidence_score
        assert restored_state.metadata == initial_state.metadata

    @pytest.mark.asyncio
    async def test_state_validation_during_workflow(
        self,
        orchestrator: GhostbustersOrchestrator
    ) -> None:
        """Test pydantic validation during workflow execution."""
        # Test confidence score validation
        state = GhostbustersState(
            project_path=orchestrator.project_path,
            confidence_score=1.5,  # Should be clamped to 1.0
            delusions_detected=[],
            validation_results=[],
            recovery_results=[],
            errors=[],
            warnings=[],
            metadata={}
        )
        
        # Verify confidence is validated
        assert state.confidence_score == 1.0
        
        # Test negative confidence
        state = GhostbustersState(
            project_path=orchestrator.project_path,
            confidence_score=-0.5,  # Should be clamped to 0.0
            delusions_detected=[],
            validation_results=[],
            recovery_results=[],
            errors=[],
            warnings=[],
            metadata={}
        )
        
        assert state.confidence_score == 0.0

    @pytest.mark.asyncio
    async def test_workflow_execution_with_pydantic_state(
        self,
        test_project: Path
    ) -> None:
        """Test complete workflow execution with pydantic state."""
        from src.ghostbusters import run_ghostbusters
        
        # Run the complete workflow
        final_state = await run_ghostbusters(str(test_project))
        
        # Verify final state is pydantic model
        assert hasattr(final_state, 'model_dump')
        assert hasattr(final_state, 'model_validate')
        
        # Test state properties
        assert hasattr(final_state, 'confidence_score')
        assert hasattr(final_state, 'delusions_detected')
        assert hasattr(final_state, 'validation_results')
        assert hasattr(final_state, 'recovery_results')
        assert hasattr(final_state, 'errors')
        
        # Test confidence validation
        assert 0.0 <= final_state.confidence_score <= 1.0
        
        # Test serialization of final state
        state_dict = final_state.model_dump()
        assert isinstance(state_dict, dict)
        assert 'confidence_score' in state_dict
        assert 'delusions_detected' in state_dict

    @pytest.mark.asyncio
    async def test_error_handling_in_workflow_with_pydantic(
        self,
        orchestrator: GhostbustersOrchestrator
    ) -> None:
        """Test error handling in workflow with pydantic validation."""
        # Create state with potential validation issues
        state = GhostbustersState(
            project_path=orchestrator.project_path,
            confidence_score=0.5,
            delusions_detected=[],
            validation_results=[],
            recovery_results=[],
            errors=["Test error"],
            warnings=["Test warning"],
            metadata={}
        )
        
        # Test that errors and warnings are properly handled
        assert len(state.errors) == 1
        assert len(state.warnings) == 1
        assert state.errors[0] == "Test error"
        assert state.warnings[0] == "Test warning"
        
        # Test serialization with errors
        state_dict = state.model_dump()
        assert state_dict['errors'] == ["Test error"]
        assert state_dict['warnings'] == ["Test warning"]

    @pytest.mark.asyncio
    async def test_state_immutability_and_updates(
        self,
        orchestrator: GhostbustersOrchestrator
    ) -> None:
        """Test state updates while maintaining pydantic validation."""
        # Create initial state
        initial_state = GhostbustersState(
            project_path=orchestrator.project_path,
            confidence_score=0.0,
            delusions_detected=[],
            validation_results=[],
            recovery_results=[],
            errors=[],
            warnings=[],
            metadata={}
        )
        
        # Test state update with model_copy
        updated_state = initial_state.model_copy(update={
            'confidence_score': 0.8,
            'delusions_detected': [{'type': 'test', 'file': 'test.py'}]
        })
        
        # Verify original state unchanged
        assert initial_state.confidence_score == 0.0
        assert len(initial_state.delusions_detected) == 0
        
        # Verify updated state
        assert updated_state.confidence_score == 0.8
        assert len(updated_state.delusions_detected) == 1
        assert updated_state.delusions_detected[0]['type'] == 'test'

    @pytest.mark.asyncio
    async def test_json_serialization_for_langgraph(
        self,
        orchestrator: GhostbustersOrchestrator
    ) -> None:
        """Test JSON serialization for LangGraph state management."""
        state = GhostbustersState(
            project_path=orchestrator.project_path,
            confidence_score=0.75,
            delusions_detected=[
                {'type': 'security', 'file': 'test.py', 'line': 42}
            ],
            validation_results=[],
            recovery_results=[],
            errors=[],
            warnings=[],
            metadata={'workflow_step': 'detection'}
        )
        
        # Test JSON serialization
        json_str = state.model_dump_json()
        assert isinstance(json_str, str)
        assert '0.75' in json_str
        assert 'security' in json_str
        assert 'workflow_step' in json_str
        
        # Test JSON deserialization
        import json
        state_dict = json.loads(json_str)
        restored_state = GhostbustersState(**state_dict)
        
        assert restored_state.confidence_score == 0.75
        assert len(restored_state.delusions_detected) == 1
        assert restored_state.metadata['workflow_step'] == 'detection'


class TestLangGraphWorkflowNodes:
    """Test individual workflow nodes with pydantic state."""

    @pytest.fixture
    def sample_state(self, tmp_path: Path) -> GhostbustersState:
        """Create sample pydantic state for testing."""
        return GhostbustersState(
            project_path=str(tmp_path),
            confidence_score=0.0,
            delusions_detected=[],
            validation_results=[],
            recovery_results=[],
            errors=[],
            warnings=[],
            metadata={}
        )

    @pytest.mark.asyncio
    async def test_detection_node_with_pydantic_state(
        self,
        sample_state: GhostbustersState
    ) -> None:
        """Test detection node updates pydantic state correctly."""
        # Simulate detection node processing
        updated_state = sample_state.model_copy(update={
            'delusions_detected': [
                {'type': 'syntax', 'file': 'test.py', 'confidence': 0.9}
            ],
            'confidence_score': 0.8
        })
        
        # Verify state update
        assert len(updated_state.delusions_detected) == 1
        assert updated_state.delusions_detected[0]['type'] == 'syntax'
        assert updated_state.confidence_score == 0.8
        
        # Verify serialization still works
        state_dict = updated_state.model_dump()
        assert len(state_dict['delusions_detected']) == 1

    @pytest.mark.asyncio
    async def test_validation_node_with_pydantic_state(
        self,
        sample_state: GhostbustersState
    ) -> None:
        """Test validation node updates pydantic state correctly."""
        # Simulate validation node processing
        updated_state = sample_state.model_copy(update={
            'validation_results': [
                {'is_valid': False, 'validator': 'SecurityValidator'}
            ]
        })
        
        # Verify state update
        assert len(updated_state.validation_results) == 1
        assert updated_state.validation_results[0]['is_valid'] is False
        
        # Test serialization
        state_dict = updated_state.model_dump()
        assert len(state_dict['validation_results']) == 1

    @pytest.mark.asyncio
    async def test_recovery_node_with_pydantic_state(
        self,
        sample_state: GhostbustersState
    ) -> None:
        """Test recovery node updates pydantic state correctly."""
        # Simulate recovery node processing
        updated_state = sample_state.model_copy(update={
            'recovery_results': [
                {'success': True, 'engine': 'SyntaxRecoveryEngine'}
            ],
            'confidence_score': 0.9
        })
        
        # Verify state update
        assert len(updated_state.recovery_results) == 1
        assert updated_state.recovery_results[0]['success'] is True
        assert updated_state.confidence_score == 0.9
        
        # Test serialization
        state_dict = updated_state.model_dump()
        assert len(state_dict['recovery_results']) == 1


if __name__ == "__main__":
    pytest.main([__file__])