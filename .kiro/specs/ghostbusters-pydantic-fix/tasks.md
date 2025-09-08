# Implementation Plan

- [x] 1. Update base data model classes to use pydantic BaseModel
  - Convert DelusionResult from dataclass to pydantic BaseModel with field validation
  - Convert ValidationResult from dataclass to pydantic BaseModel with constraints
  - Convert RecoveryResult from dataclass to pydantic BaseModel with validation
  - Add proper type hints using List, Dict instead of list, dict
  - Add field constraints for confidence scores (0.0-1.0 range)
  - _Requirements: 1.1, 1.2, 2.2_

- [x] 2. Migrate GhostbustersState to pydantic BaseModel
  - Convert GhostbustersState dataclass to pydantic BaseModel
  - Add field defaults using Field(default_factory=list) for lists and dicts
  - Add validation for confidence_score field (0.0-1.0 range)
  - Configure arbitrary_types_allowed for Path objects
  - Test state serialization with LangGraph
  - _Requirements: 2.1, 2.3_

- [x] 3. Update base expert agent class interface
  - Modify BaseExpert class to return pydantic DelusionResult
  - Update detect_delusions method signature and return type
  - Add proper type hints for all methods
  - Update helper methods to work with pydantic models
  - Test agent initialization and delusion detection
  - _Requirements: 1.1, 3.1_

- [x] 4. Update base validator class interface  
  - Modify BaseValidator class to return pydantic ValidationResult
  - Update validate_findings method signature and return type
  - Add proper type hints for validation methods
  - Update helper methods to work with pydantic models
  - Test validator functionality with new models
  - _Requirements: 1.1, 3.2_

- [x] 5. Update base recovery engine class interface
  - Modify BaseRecoveryEngine class to return pydantic RecoveryResult
  - Update execute_recovery method signature and return type
  - Add proper type hints for recovery methods
  - Update helper methods to work with pydantic models
  - Test recovery engine functionality with new models
  - _Requirements: 1.1, 3.3_

- [x] 6. Update GhostbustersOrchestrator for pydantic compatibility
  - Modify orchestrator to work with pydantic GhostbustersState
  - Update LangGraph workflow initialization to use pydantic state
  - Fix state transitions between workflow nodes
  - Update error handling for pydantic ValidationError exceptions
  - Test orchestrator initialization and workflow execution
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 7. Update all concrete agent implementations
  - Update SecurityExpert, CodeQualityExpert, TestExpert, BuildExpert, ArchitectureExpert, ModelExpert
  - Ensure all agents return proper pydantic DelusionResult objects
  - Update agent-specific logic to work with pydantic models
  - Add proper error handling for pydantic validation
  - Test each agent individually with new models
  - _Requirements: 1.1, 3.1_

- [x] 8. Fix legacy agents.py file with dataclass imports
  - Remove dataclass DelusionResult from src/ghostbusters/agents.py
  - Update all agent classes to use the new BaseExpert from agents/base_expert.py
  - Remove dataclass imports and update to use pydantic models
  - Ensure all agents inherit from the correct BaseExpert class
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 9. Update all concrete validator implementations
  - Update SecurityValidator, CodeQualityValidator, TestValidator, BuildValidator, ArchitectureValidator, ModelValidator
  - Ensure all validators return proper pydantic ValidationResult objects
  - Update validator-specific logic to work with pydantic models
  - Add proper error handling for pydantic validation
  - Test each validator individually with new models
  - _Requirements: 1.1, 3.2_

- [x] 10. Update all concrete recovery engine implementations
  - Update SyntaxRecoveryEngine, IndentationFixer, ImportResolver, TypeAnnotationFixer
  - Ensure all recovery engines return proper pydantic RecoveryResult objects
  - Update recovery engine logic to work with pydantic models
  - Add proper error handling for pydantic validation
  - Test each recovery engine individually with new models
  - _Requirements: 1.1, 3.3_

- [x] 11. Update existing test file for pydantic compatibility
  - Modify tests/test_ghostbusters.py to work with pydantic models
  - Update test assertions to check pydantic model attributes
  - Add tests for model validation and serialization
  - Update mock objects to return pydantic models
  - Test error handling for invalid model data
  - _Requirements: 1.1, 5.3_

- [x] 12. Add comprehensive pydantic validation tests
  - Create tests for field validation (confidence score ranges, required fields)
  - Test model serialization and deserialization (to_dict, from_dict)
  - Test error handling for ValidationError exceptions
  - Test model equality and comparison operations
  - Test JSON serialization for LangGraph state management
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 13. Test LangGraph workflow with pydantic state
  - Test GhostbustersOrchestrator initialization with pydantic state
  - Test state transitions between workflow nodes
  - Test state serialization during workflow execution
  - Test error handling in workflow with pydantic validation
  - Test complete workflow execution end-to-end
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 14. Run full test suite and fix remaining issues
  - Execute pytest tests/test_ghostbusters.py
  - Fix any remaining pydantic compatibility issues
  - Ensure test success rate >90% for Ghostbusters tests
  - Update project model registry with completion status
  - Document any breaking changes or migration notes
  - _Requirements: 1.3, 5.2, 5.3_