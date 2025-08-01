# OpenFlow Playground Source Code

This directory contains the source code organized by domain according to the project model registry.

## Directory Structure

```
src/
├── __init__.py                    # Package initialization
├── streamlit/                     # Streamlit application components
│   ├── __init__.py               # Streamlit package initialization
│   └── openflow_quickstart_app.py # Main Streamlit application
├── security_first/                # Security-first architecture components
│   ├── __init__.py               # Security package initialization
│   └── test_streamlit_security_first.py # Security testing and validation
└── multi_agent_testing/          # Multi-agent testing framework components
    ├── __init__.py               # Multi-agent package initialization
    └── test_multi_agent_blind_spot_detection.py # Multi-agent validation
```

## Domain Organization

### Streamlit Domain (`src/streamlit/`)
Contains the main Streamlit application for OpenFlow deployment with:
- Security-first architecture
- Multi-user RBAC support
- Real-time monitoring and visualization
- Accessibility compliance
- Performance optimization

**Key Files:**
- `openflow_quickstart_app.py` - Main Streamlit application

### Security-First Domain (`src/security_first/`)
Contains security-first architecture components including:
- Credential management and encryption
- Session management with JWT
- Input validation and sanitization
- Security testing and validation

**Key Files:**
- `test_streamlit_security_first.py` - Security testing framework

### Multi-Agent Testing Domain (`src/multi_agent_testing/`)
Contains multi-agent testing framework components including:
- Diversity hypothesis testing
- Blind spot detection
- Multi-agent validation
- Coverage analysis

**Key Files:**
- `test_multi_agent_blind_spot_detection.py` - Multi-agent validation framework

## Usage

### Running the Streamlit App
```bash
# Install dependencies
pip install -r requirements_streamlit.txt

# Run the Streamlit app
streamlit run src/streamlit/openflow_quickstart_app.py
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific domain tests
pytest tests/test_core_concepts.py -v
pytest tests/test_basic_validation.py -v
pytest tests/test_file_organization.py -v
```

### Security Testing
```bash
# Run security tests
pytest src/security_first/test_streamlit_security_first.py -v

# Run multi-agent validation
pytest src/multi_agent_testing/test_multi_agent_blind_spot_detection.py -v
```

## Project Model Integration

This structure follows the project model registry domains:
- **streamlit**: Streamlit application components
- **security_first**: Security-first architecture components  
- **multi_agent_testing**: Multi-agent testing framework components

Each domain has its own:
- Linting rules (flake8, bandit)
- Formatting rules (black)
- Validation rules (pytest, detect-secrets)
- Testing requirements

## Development Guidelines

1. **Domain Separation**: Keep files in their appropriate domain directories
2. **Package Structure**: Each domain should have `__init__.py` for proper imports
3. **Testing**: All components should have corresponding tests
4. **Documentation**: Update this README when adding new domains or files
5. **Model Registry**: Update `project_model_registry.json` when adding new domains

## Adding New Components

1. **Create Domain Directory**: Add new domain directory under `src/`
2. **Add __init__.py**: Create package initialization file
3. **Update Model Registry**: Add domain configuration to `project_model_registry.json`
4. **Add Tests**: Create corresponding test files in `tests/`
5. **Update Documentation**: Update this README and implementation docs 