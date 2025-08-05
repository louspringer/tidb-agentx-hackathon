# OpenFlow Playground - Model-Driven Makefile
# This Makefile leverages the project_model_registry.json for domain-specific operations

.PHONY: help install install-python install-bash install-cloudformation install-docs install-security install-streamlit install-healthcare install-all
.PHONY: test test-python test-bash test-cloudformation test-docs test-security test-streamlit test-healthcare test-all
.PHONY: lint lint-python lint-bash lint-cloudformation lint-docs lint-security lint-streamlit lint-healthcare lint-all
.PHONY: format format-python format-bash format-docs format-all
.PHONY: validate validate-model validate-requirements validate-all
.PHONY: clean clean-python clean-cache clean-all
.PHONY: deploy deploy-streamlit deploy-security deploy-healthcare
.PHONY: security security-scan security-check security-audit
.PHONY: docs docs-build docs-serve docs-index

# Project configuration
PROJECT_NAME := openflow-playground
MODEL_FILE := project_model_registry.json
PYTHON := python3
UV := uv
MAKE := make


# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(CYAN)OpenFlow Playground - Model-Driven Makefile$(NC)"
	@echo "$(YELLOW)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(PURPLE)Domain-specific targets:$(NC)"
	@echo "  install-{domain}    - Install dependencies for specific domain"
	@echo "  test-{domain}       - Run tests for specific domain"
	@echo "  lint-{domain}       - Lint code for specific domain"
	@echo "  format-{domain}     - Format code for specific domain"
	@echo ""
	@echo "$(PURPLE)Available domains:$(NC)"
	@echo "  python, bash, cloudformation, docs, security, streamlit, healthcare"
	@echo ""
	@echo "$(PURPLE)Examples:$(NC)"
	@echo "  make install-python     - Install Python dependencies with UV"
	@echo "  make test-security      - Run security tests and scans"
	@echo "  make lint-all           - Lint all domains"
	@echo "  make validate-model     - Validate project model registry"

# =============================================================================
# INSTALLATION TARGETS
# =============================================================================

install: install-all ## Install all dependencies (default: install-all)

install-all: install-python install-bash install-cloudformation install-docs install-security install-streamlit install-healthcare ## Install dependencies for all domains
	@echo "$(GREEN)✅ All dependencies installed$(NC)"

install-python: ## Install Python dependencies with UV
	@echo "$(BLUE)🐍 Installing Python dependencies with UV...$(NC)"
	@$(UV) sync --all-extras
	@echo "$(GREEN)✅ Python dependencies installed$(NC)"

install-bash: ## Install bash script dependencies
	@echo "$(BLUE)🐚 Installing bash script dependencies...$(NC)"
	@command -v shellcheck >/dev/null 2>&1 || { echo "$(YELLOW)⚠️  shellcheck not found, installing...$(NC)"; sudo apt-get install -y shellcheck; }
	@echo "$(GREEN)✅ Bash dependencies installed$(NC)"

install-cloudformation: ## Install CloudFormation dependencies
	@echo "$(BLUE)☁️  Installing CloudFormation dependencies...$(NC)"
	@command -v cfn-lint >/dev/null 2>&1 || { echo "$(YELLOW)⚠️  cfn-lint not found, installing...$(NC)"; pip install cfn-lint; }
	@echo "$(GREEN)✅ CloudFormation dependencies installed$(NC)"

install-docs: ## Install documentation dependencies
	@echo "$(BLUE)📚 Installing documentation dependencies...$(NC)"
	@command -v markdownlint >/dev/null 2>&1 || { echo "$(YELLOW)⚠️  markdownlint not found, installing...$(NC)"; npm install -g markdownlint-cli; }
	@echo "$(GREEN)✅ Documentation dependencies installed$(NC)"

install-security: ## Install security tooling dependencies
	@echo "$(BLUE)🔒 Installing security dependencies...$(NC)"
	@$(UV) sync --extra security
	@echo "$(GREEN)✅ Security dependencies installed$(NC)"

install-streamlit: ## Install Streamlit app dependencies
	@echo "$(BLUE)📊 Installing Streamlit dependencies...$(NC)"
	@$(UV) sync
	@echo "$(GREEN)✅ Streamlit dependencies installed$(NC)"

install-healthcare: ## Install healthcare CDC dependencies
	@echo "$(BLUE)🏥 Installing healthcare CDC dependencies...$(NC)"
	@$(UV) sync
	@echo "$(GREEN)✅ Healthcare CDC dependencies installed$(NC)"

# =============================================================================
# TESTING TARGETS
# =============================================================================

test: test-all ## Run all tests (default: test-all)

test-all: test-python test-bash test-cloudformation test-docs test-security test-streamlit test-healthcare ## Run tests for all domains
	@echo "$(GREEN)✅ All tests completed$(NC)"

test-python: ## Run Python tests
	@echo "$(BLUE)🐍 Running Python tests...$(NC)"
	@$(UV) run pytest tests/ -v
	@echo "$(GREEN)✅ Python tests completed$(NC)"


test-bash: ## Run bash script tests
	@echo "$(BLUE)🐚 Running bash script tests...$(NC)"
	@find scripts/ -name "*.sh" -exec shellcheck {} \;
	@echo "$(GREEN)✅ Bash script tests completed$(NC)"

test-cloudformation: ## Run CloudFormation tests
	@echo "$(BLUE)☁️  Running CloudFormation tests...$(NC)"
	@find . -name "*.template.yaml" -exec cfn-lint {} \;
	@echo "$(GREEN)✅ CloudFormation tests completed$(NC)"

test-docs: ## Run documentation tests
	@echo "$(BLUE)📚 Running documentation tests...$(NC)"
	@find docs/ -name "*.md" -exec markdownlint {} \;
	@echo "$(GREEN)✅ Documentation tests completed$(NC)"

test-security: ## Run security tests and scans
	@echo "$(BLUE)🔒 Running security tests...$(NC)"
	@$(UV) run bandit -r src/
	@$(UV) run safety check
	@$(UV) run detect-secrets scan
	@echo "$(GREEN)✅ Security tests completed$(NC)"

test-streamlit: ## Run Streamlit app tests
	@echo "$(BLUE)📊 Running Streamlit app tests...$(NC)"
	@$(UV) run pytest tests/test_uv_package_management.py -v
	@$(UV) run pytest tests/test_basic_validation.py -v
	@echo "$(GREEN)✅ Streamlit app tests completed$(NC)"

test-healthcare: ## Run healthcare CDC tests
	@echo "$(BLUE)🏥 Running healthcare CDC tests...$(NC)"
	@$(UV) run pytest tests/test_healthcare_cdc_requirements.py -v
	@echo "$(GREEN)✅ Healthcare CDC tests completed$(NC)"

test-model: ## Run model validation tests
	@echo "$(BLUE)🔍 Running model validation tests...$(NC)"
	@python scripts/pre_test_model_check.py
	@echo "$(GREEN)✅ Model validation tests completed$(NC)"
# =============================================================================
# LINTING TARGETS
# =============================================================================

lint: lint-all ## Lint all code (default: lint-all)

lint-all: lint-python lint-bash lint-cloudformation lint-docs lint-security lint-streamlit lint-healthcare ## Lint all domains
	@echo "$(GREEN)✅ All linting completed$(NC)"

lint-python: ## Lint Python code
	@echo "$(BLUE)🐍 Linting Python code...$(NC)"
	@$(UV) run flake8 src/ tests/
	@$(UV) run mypy src/
	@echo "$(GREEN)✅ Python linting completed$(NC)"

lint-bash: ## Lint bash scripts
	@echo "$(BLUE)🐚 Linting bash scripts...$(NC)"
	@find scripts/ -name "*.sh" -exec shellcheck {} \;
	@echo "$(GREEN)✅ Bash script linting completed$(NC)"

lint-cloudformation: ## Lint CloudFormation templates
	@echo "$(BLUE)☁️  Linting CloudFormation templates...$(NC)"
	@find . -name "*.template.yaml" -exec cfn-lint {} \;
	@echo "$(GREEN)✅ CloudFormation linting completed$(NC)"

lint-docs: ## Lint documentation
	@echo "$(BLUE)📚 Linting documentation...$(NC)"
	@find docs/ -name "*.md" -exec markdownlint {} \;
	@echo "$(GREEN)✅ Documentation linting completed$(NC)"

lint-security: ## Lint security code
	@echo "$(BLUE)🔒 Linting security code...$(NC)"
	@$(UV) run bandit -r src/security_first/
	@$(UV) run safety check
	@echo "$(GREEN)✅ Security linting completed$(NC)"

lint-streamlit: ## Lint Streamlit code
	@echo "$(BLUE)📊 Linting Streamlit code...$(NC)"
	@$(UV) run flake8 src/streamlit/
	@$(UV) run mypy src/streamlit/
	@echo "$(GREEN)✅ Streamlit linting completed$(NC)"

lint-healthcare: ## Lint healthcare CDC code
	@echo "$(BLUE)🏥 Linting healthcare CDC code...$(NC)"
	@$(UV) run flake8 healthcare-cdc/
	@echo "$(GREEN)✅ Healthcare CDC linting completed$(NC)"

# =============================================================================
# FORMATTING TARGETS
# =============================================================================

format: format-all ## Format all code (default: format-all)

format-all: format-python format-bash format-docs ## Format all domains
	@echo "$(GREEN)✅ All formatting completed$(NC)"

format-python: ## Format Python code
	@echo "$(BLUE)🐍 Formatting Python code...$(NC)"
	@$(UV) run black src/ tests/
	@echo "$(GREEN)✅ Python formatting completed$(NC)"
format-bash: ## Format bash scripts
	@echo "$(BLUE)🐚 Formatting bash scripts...$(NC)"
	@find scripts/ -name "*.sh" -exec shfmt -w {} \;
	@echo "$(GREEN)✅ Bash script formatting completed$(NC)"

format-docs: ## Format documentation
	@echo "$(BLUE)📚 Formatting documentation...$(NC)"
	@find docs/ -name "*.md" -exec prettier --write {} \;
	@echo "$(GREEN)✅ Documentation formatting completed$(NC)"

# =============================================================================
# VALIDATION TARGETS
# =============================================================================

validate: validate-all ## Validate all components (default: validate-all)

validate-all: validate-model validate-requirements ## Validate all components
	@echo "$(GREEN)✅ All validation completed$(NC)"

validate-model: ## Validate project model registry
	@echo "$(BLUE)🔍 Validating project model registry...$(NC)"
	@$(PYTHON) -c "import json; json.load(open('$(MODEL_FILE)'))"
	@echo "$(GREEN)✅ Project model registry is valid JSON$(NC)"

validate-requirements: ## Validate requirements traceability
	@echo "$(BLUE)🔍 Validating requirements traceability...$(NC)"
	@$(UV) run python tests/test_model_traceability.py
	@echo "$(GREEN)✅ Requirements traceability validated$(NC)"

# =============================================================================
# CLEANUP TARGETS
# =============================================================================

clean: clean-all ## Clean all artifacts (default: clean-all)

clean-all: clean-python clean-cache ## Clean all artifacts
	@echo "$(GREEN)✅ All cleanup completed$(NC)"

clean-python: ## Clean Python artifacts
	@echo "$(BLUE)🧹 Cleaning Python artifacts...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Python artifacts cleaned$(NC)"

clean-cache: ## Clean all cache directories
	@echo "$(BLUE)🧹 Cleaning cache directories...$(NC)"
	@find . -name ".cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cache directories cleaned$(NC)"

# =============================================================================
# DEPLOYMENT TARGETS
# =============================================================================

deploy: deploy-streamlit ## Deploy applications (default: deploy-streamlit)

deploy-streamlit: ## Deploy Streamlit app
	@echo "$(BLUE)📊 Deploying Streamlit app...$(NC)"
	@$(UV) run streamlit run src/streamlit/openflow_quickstart_app.py
	@echo "$(GREEN)✅ Streamlit app deployed$(NC)"

deploy-security: ## Deploy security components
	@echo "$(BLUE)🔒 Deploying security components...$(NC)"
	@$(UV) run python src/security_first/test_https_enforcement.py
	@echo "$(GREEN)✅ Security components deployed$(NC)"

deploy-healthcare: ## Deploy healthcare CDC components
	@echo "$(BLUE)🏥 Deploying healthcare CDC components...$(NC)"
	@$(UV) run python healthcare-cdc/models/healthcare_cdc_domain_model.py
	@echo "$(GREEN)✅ Healthcare CDC components deployed$(NC)"

# =============================================================================
# SECURITY TARGETS
# =============================================================================

security: security-scan ## Run security checks (default: security-scan)

security-scan: ## Run comprehensive security scan
	@echo "$(BLUE)🔒 Running comprehensive security scan...$(NC)"
	@$(UV) run bandit -r src/ -f json -o security-report.json
	@$(UV) run safety check --json --output security-vulnerabilities.json
	@$(UV) run detect-secrets scan --baseline .secrets.baseline
	@echo "$(GREEN)✅ Security scan completed$(NC)"

security-check: ## Run quick security check
	@echo "$(BLUE)🔒 Running quick security check...$(NC)"
	@$(UV) run bandit -r src/ -f txt
	@$(UV) run safety check
	@echo "$(GREEN)✅ Quick security check completed$(NC)"

security-audit: ## Run security audit
	@echo "$(BLUE)🔒 Running security audit...$(NC)"
	@$(UV) run bandit -r src/ -f json -o security-audit.json
	@$(UV) run safety check --json --output security-audit-vulnerabilities.json
	@$(UV) run detect-secrets audit .secrets.baseline
	@echo "$(GREEN)✅ Security audit completed$(NC)"

# =============================================================================
# DOCUMENTATION TARGETS
# =============================================================================

docs: docs-index ## Build documentation (default: docs-index)

docs-build: ## Build documentation
	@echo "$(BLUE)📚 Building documentation...$(NC)"
	@find docs/ -name "*.md" -exec markdownlint {} \;
	@echo "$(GREEN)✅ Documentation built$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)📚 Serving documentation locally...$(NC)"
	@$(PYTHON) -m http.server 8000 --directory docs/
	@echo "$(GREEN)✅ Documentation served at http://localhost:8000$(NC)"

docs-index: ## Index documentation
	@echo "$(BLUE)📚 Indexing documentation...$(NC)"
	@find docs/ -name "*.md" -exec basename {} \; | sort
	@echo "$(GREEN)✅ Documentation indexed$(NC)"

# =============================================================================
# DEVELOPMENT TARGETS
# =============================================================================

dev-setup: install-all ## Setup development environment
	@echo "$(GREEN)✅ Development environment setup complete$(NC)"

dev-test: test-all ## Run all tests for development
	@echo "$(GREEN)✅ Development tests complete$(NC)"

dev-lint: lint-all ## Run all linting for development
	@echo "$(GREEN)✅ Development linting complete$(NC)"

dev-format: format-all ## Run all formatting for development
	@echo "$(GREEN)✅ Development formatting complete$(NC)"

# =============================================================================
# UTILITY TARGETS
# =============================================================================

check-deps: ## Check if all dependencies are installed
	@echo "$(BLUE)🔍 Checking dependencies...$(NC)"
	@command -v $(UV) >/dev/null 2>&1 || { echo "$(RED)❌ UV not found$(NC)"; exit 1; }
	@command -v shellcheck >/dev/null 2>&1 || { echo "$(YELLOW)⚠️  shellcheck not found$(NC)"; }
	@command -v cfn-lint >/dev/null 2>&1 || { echo "$(YELLOW)⚠️  cfn-lint not found$(NC)"; }
	@echo "$(GREEN)✅ Dependencies check completed$(NC)"

show-domains: ## Show available domains from model
	@echo "$(BLUE)🔍 Available domains from model:$(NC)"
	@$(PYTHON) -c "import json; data=json.load(open('$(MODEL_FILE)')); print('\n'.join(data['domains'].keys()))"

show-rules: ## Show available rules
	@echo "$(BLUE)🔍 Available rules:$(NC)"
	@find .cursor/rules/ -name "*.mdc" -exec basename {} \;

status: ## Show project status
	@echo "$(CYAN)OpenFlow Playground Status$(NC)"
	@echo "$(BLUE)📁 Project structure:$(NC)"
	@find . -maxdepth 2 -type d | grep -v __pycache__ | grep -v .git | sort
	@echo ""
		@echo "$(BLUE)🔧 Available make targets:$(NC)"
	@make help | grep -E "^[a-zA-Z_-]+:" | head -10
	@echo "$(YELLOW)... and more (run 'make help' for full list)$(NC)"
