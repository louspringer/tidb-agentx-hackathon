# Security-First Code Review Guidelines

## Security Vulnerabilities to Flag:

1. **Subprocess Usage**: Flag subprocess.run, os.system, os.popen
2. **Credential Exposure**: Check for hardcoded secrets/credentials
3. **Input Validation**: Ensure all user inputs are validated
4. **Error Handling**: Verify proper exception handling
5. **Secure Shell**: Prefer elegant secure shell client over direct subprocess

## Model-Driven Architecture:

1. **Project Model Registry**: Align with project_model_registry.json
2. **Domain Detection**: Verify proper domain classification
3. **Tool Selection**: Check appropriate linters/validators
4. **Requirements Traceability**: Ensure changes trace to model requirements

## Code Quality Standards:

1. **Python Standards**: PEP 8, type hints, docstrings
2. **Error Handling**: Comprehensive exception handling
3. **Logging**: Appropriate levels, secure logging
4. **Testing**: Adequate test coverage
5. **Documentation**: Update docs for significant changes

## Security-First Review Checklist:

### High Priority Security Issues:
- [ ] **Subprocess vulnerabilities** - Use elegant secure shell client instead
- [ ] **Hardcoded credentials** - Move to environment variables
- [ ] **Unvalidated inputs** - Add proper input validation
- [ ] **Insecure error handling** - Implement proper exception handling
- [ ] **Missing type hints** - Add comprehensive type annotations

### Model-Driven Requirements:
- [ ] **Domain classification** - Ensure proper domain detection
- [ ] **Tool selection** - Verify appropriate linters/validators
- [ ] **Requirements traceability** - Link changes to model requirements
- [ ] **Project structure** - Follow established patterns

### Code Quality Requirements:
- [ ] **PEP 8 compliance** - Follow Python style guidelines
- [ ] **Type hints** - Add comprehensive type annotations
- [ ] **Docstrings** - Include proper documentation
- [ ] **Error handling** - Implement robust exception handling
- [ ] **Logging** - Use appropriate logging levels
- [ ] **Testing** - Ensure adequate test coverage
- [ ] **Documentation** - Update relevant documentation

## Repository-Specific Guidelines:

### Security-First Architecture:
- **Prefer secure shell client** over direct subprocess calls
- **Use environment variables** for all credentials
- **Implement input validation** for all user inputs
- **Add comprehensive error handling** with proper logging
- **Follow least privilege principle** for all operations

### Model-Driven Development:
- **Check project_model_registry.json** for domain requirements
- **Verify tool selection** matches domain configuration
- **Ensure requirements traceability** to model requirements
- **Follow established patterns** for new components

### Integration Requirements:
- **GitHub MCP Integration** - Leverage repository context
- **Ghostbusters Integration** - Address detected delusions
- **Secure Shell Service** - Use elegant client for shell operations
- **Model-Driven Architecture** - Follow established patterns

## Review Focus Areas:

### Security:
1. **Subprocess Usage** - Flag and suggest secure alternatives
2. **Credential Management** - Ensure no hardcoded secrets
3. **Input Validation** - Verify all inputs are properly validated
4. **Error Handling** - Check for comprehensive exception handling
5. **Secure Logging** - Ensure sensitive data is not logged

### Quality:
1. **Code Standards** - Follow PEP 8 and project conventions
2. **Type Safety** - Add comprehensive type hints
3. **Documentation** - Include proper docstrings and comments
4. **Testing** - Ensure adequate test coverage
5. **Performance** - Check for efficient implementations

### Architecture:
1. **Model Alignment** - Verify changes align with project model
2. **Domain Classification** - Ensure proper domain detection
3. **Tool Integration** - Check appropriate tools are used
4. **Requirements Traceability** - Link changes to requirements
5. **Pattern Consistency** - Follow established architectural patterns 