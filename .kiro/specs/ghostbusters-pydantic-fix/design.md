# Design Document

## Overview

The Ghostbusters pydantic compatibility issue stems from the transition between pydantic v1 and v2, combined with LangChain's recent migration to pydantic v2 (as of langchain-core 0.3.0). The current implementation uses Python dataclasses for data models, but LangGraph and LangChain expect pydantic BaseModel objects for proper serialization and state management.

The solution involves migrating from dataclasses to pydantic v2 BaseModel classes while ensuring compatibility with LangChain/LangGraph's state management system.

## Architecture

### Current State
- **Data Models**: Using Python `@dataclass` decorators
- **LangChain Version**: 0.3.27 (uses pydantic v2 internally)
- **Pydantic Version**: 2.9.2
- **Issue**: LangGraph expects pydantic models for state serialization, but we're using dataclasses

### Target State
- **Data Models**: Migrate to pydantic v2 `BaseModel` classes
- **State Management**: Use pydantic models for LangGraph state
- **Serialization**: Proper JSON serialization/deserialization
- **Type Safety**: Enhanced type validation with pydantic v2 features

## Components and Interfaces

### 1. Base Data Models Migration

**Current Implementation:**
```python
@dataclass
class DelusionResult:
    delusions: list[dict[str, Any]]
    confidence: float
    recommendations: list[str]
    agent_name: str
```

**New Implementation:**
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any

class DelusionResult(BaseModel):
    delusions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    recommendations: List[str] = Field(default_factory=list)
    agent_name: str
    
    @validator('confidence')
    def validate_confidence(cls, v):
        return max(0.0, min(1.0, v))
```

### 2. LangGraph State Model

**Current Implementation:**
```python
@dataclass
class GhostbustersState:
    project_path: str
    delusions_detected: list[dict[str, Any]]
    # ... other fields
```

**New Implementation:**
```python
class GhostbustersState(BaseModel):
    project_path: str
    delusions_detected: List[Dict[str, Any]] = Field(default_factory=list)
    recovery_actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    recovery_results: Dict[str, Any] = Field(default_factory=dict)
    current_phase: str = Field(default="detection")
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
```

### 3. Agent Interface Updates

**Base Expert Class:**
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from pathlib import Path

class BaseExpert(ABC):
    def __init__(self, name: str):
        self.name = name
        self.confidence_threshold = 0.7

    @abstractmethod
    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect delusions in the project."""
```

### 4. Validator Interface Updates

**Base Validator Class:**
```python
class ValidationResult(BaseModel):
    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    validator_name: str
```

### 5. Recovery Engine Interface Updates

**Base Recovery Engine Class:**
```python
class RecoveryResult(BaseModel):
    success: bool
    message: str
    confidence: float = Field(ge=0.0, le=1.0)
    changes_made: List[str] = Field(default_factory=list)
    engine_name: str
```

## Data Models

### Pydantic v2 Model Hierarchy

```
BaseModel (pydantic)
├── DelusionResult
├── ValidationResult  
├── RecoveryResult
└── GhostbustersState
    ├── project_path: str
    ├── delusions_detected: List[Dict[str, Any]]
    ├── recovery_actions: List[Dict[str, Any]]
    ├── confidence_score: float (0.0-1.0)
    ├── validation_results: Dict[str, Any]
    ├── recovery_results: Dict[str, Any]
    ├── current_phase: str
    ├── errors: List[str]
    ├── warnings: List[str]
    └── metadata: Dict[str, Any]
```

### Field Validation Rules

1. **Confidence Scores**: Must be between 0.0 and 1.0
2. **Lists**: Default to empty lists, not None
3. **Dictionaries**: Default to empty dicts, not None
4. **Strings**: Required fields must be non-empty
5. **Phase Values**: Restricted to valid phase names

## Error Handling

### 1. Pydantic Validation Errors
- Catch `ValidationError` exceptions during model creation
- Provide meaningful error messages for invalid data
- Fallback to default values where appropriate

### 2. LangGraph Serialization Errors
- Ensure all state objects are JSON serializable
- Handle complex objects in metadata with custom serializers
- Validate state transitions between workflow nodes

### 3. Import Compatibility
- Remove any remaining pydantic v1 imports
- Use direct pydantic imports instead of langchain_core.pydantic_v1
- Handle deprecation warnings gracefully

## Testing Strategy

### 1. Unit Tests for Data Models
- Test pydantic model validation
- Test field constraints and validators
- Test serialization/deserialization

### 2. Integration Tests for LangGraph
- Test state transitions in workflow
- Test serialization of complex state objects
- Test error handling in workflow nodes

### 3. Compatibility Tests
- Test with current LangChain version (0.3.27)
- Test with current pydantic version (2.9.2)
- Test import statements work correctly

### 4. Migration Tests
- Test that existing functionality still works
- Test that test suite passes with new models
- Test performance impact of pydantic validation

## Migration Strategy

### Phase 1: Base Model Migration
1. Update base data model classes to use pydantic BaseModel
2. Add field validation and constraints
3. Update import statements

### Phase 2: State Model Migration  
1. Convert GhostbustersState to pydantic BaseModel
2. Update LangGraph workflow initialization
3. Test state serialization

### Phase 3: Interface Updates
1. Update all agent, validator, and recovery engine interfaces
2. Ensure return types match new pydantic models
3. Update error handling

### Phase 4: Test Re-enablement
1. Re-enable disabled test file
2. Update test assertions for pydantic models
3. Add new tests for pydantic-specific features

### Phase 5: Validation and Cleanup
1. Run full test suite
2. Fix any remaining compatibility issues
3. Remove deprecated code and imports