# Ghostbusters Task 8: Fix Legacy agents.py Implementation Plan

## Task Overview
**Task 8**: Fix legacy agents.py file with dataclass imports
- Remove dataclass DelusionResult from src/ghostbusters/agents.py
- Update all agent classes to use the new BaseExpert from agents/base_expert.py
- Remove dataclass imports and update to use pydantic models
- Ensure all agents inherit from the correct BaseExpert class

## Current State Analysis
The legacy `src/ghostbusters/agents.py` file likely contains:
- Old dataclass-based DelusionResult definitions
- Agent classes using outdated base classes
- Dataclass imports that conflict with pydantic models
- Inconsistent inheritance patterns

## Implementation Strategy

### 1. Code Audit and Cleanup
```python
# Remove these old patterns:
from dataclasses import dataclass
@dataclass
class DelusionResult: ...

# Replace with:
from src.ghostbusters.agents.base_expert import BaseExpert
from src.ghostbusters.models import DelusionResult  # pydantic model
```

### 2. Agent Class Migration
- Update all agent classes to inherit from new BaseExpert
- Ensure detect_delusions methods return pydantic DelusionResult
- Remove any local dataclass definitions
- Update import statements

### 3. Validation and Testing
- Verify all agents use consistent base class
- Test agent initialization and method calls
- Ensure pydantic model compatibility
- Check for any remaining dataclass references

## Files to Modify
1. `src/ghostbusters/agents.py` - Primary cleanup target
2. Any agent classes that import from the legacy file
3. Test files that reference the old structure

## Migration Checklist
- [ ] Remove dataclass DelusionResult definition
- [ ] Update all agent class inheritance
- [ ] Fix import statements
- [ ] Remove dataclass imports
- [ ] Update method signatures
- [ ] Test agent functionality
- [ ] Verify pydantic compatibility

## Success Criteria
- No dataclass imports in agents.py
- All agents inherit from correct BaseExpert
- All agents return pydantic DelusionResult objects
- No import conflicts between old and new models
- All existing functionality preserved

## Risk Mitigation
- Create backup of current agents.py before changes
- Test each agent class individually after migration
- Verify no breaking changes to existing API
- Check for any external dependencies on old structure

## Dependencies
- Requires new BaseExpert class (✓ Complete)
- Requires pydantic DelusionResult model (✓ Complete)
- Blocks all subsequent validator and recovery engine updates

## Estimated Effort: 1-2 days