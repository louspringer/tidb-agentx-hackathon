#!/bin/bash

# Setup Security Hooks Script
# This script installs pre-commit hooks and security checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install pre-commit
install_pre_commit() {
    print_header "Installing Pre-commit Hooks"
    
    if ! command_exists pre-commit; then
        print_status "Installing pre-commit..."
        if command_exists pip; then
            pip install pre-commit
        elif command_exists pip3; then
            pip3 install pre-commit
        else
            print_error "pip not found. Please install pip first."
            exit 1
        fi
    else
        print_status "pre-commit already installed"
    fi
    
    # Install the git hook scripts
    print_status "Installing git hooks..."
    pre-commit install
    
    print_success "Pre-commit hooks installed successfully!"
}

# Function to create secrets baseline
create_secrets_baseline() {
    print_header "Creating Secrets Baseline"
    
    if command_exists detect-secrets; then
        print_status "Creating .secrets.baseline..."
        detect-secrets scan --baseline .secrets.baseline
        print_success "Secrets baseline created!"
    else
        print_warning "detect-secrets not found. Install with: pip install detect-secrets"
    fi
}

# Function to test security checks
test_security_checks() {
    print_header "Testing Security Checks"
    
    print_status "Running security check script..."
    if [ -f "scripts/security-check.sh" ]; then
        ./scripts/security-check.sh
        print_success "Security checks working!"
    else
        print_error "Security check script not found!"
        exit 1
    fi
}

# Function to create git hooks directory
setup_git_hooks() {
    print_header "Setting up Git Hooks"
    
    if [ -d ".git" ]; then
        print_status "Git repository found"
        
        # Create hooks directory if it doesn't exist
        mkdir -p .git/hooks
        
        # Create a pre-commit hook that runs our security checks
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for security checks

echo "Running security checks..."

# Run the security check script
if [ -f "scripts/security-check.sh" ]; then
    ./scripts/security-check.sh
    if [ $? -ne 0 ]; then
        echo "❌ Security violations found! Please fix them before committing."
        exit 1
    fi
fi

echo "✅ Security checks passed!"
EOF
        
        chmod +x .git/hooks/pre-commit
        print_success "Git pre-commit hook installed!"
    else
        print_warning "Not in a git repository. Skipping git hooks setup."
    fi
}

# Function to create documentation
create_documentation() {
    print_header "Creating Security Documentation"
    
    cat > SECURITY_GUIDELINES.md << 'EOF'
# Security Guidelines

## Pre-commit Hooks

This repository uses pre-commit hooks to prevent security violations:

1. **Security Check Script**: Runs `scripts/security-check.sh` to detect hardcoded credentials
2. **Hardcoded URL Detection**: Checks for Snowflake-specific URLs
3. **UUID Pattern Detection**: Checks for hardcoded UUIDs
4. **AWS Key Detection**: Checks for hardcoded AWS credentials
5. **Environment File Detection**: Warns about .env files

## Running Security Checks

### Manual Check
```bash
./scripts/security-check.sh
```

### Pre-commit Check (Automatic)
```bash
git commit -m "your message"  # Will run security checks automatically
```

### Install Hooks
```bash
./setup-security-hooks.sh
```

## Security Rules

1. **NEVER** hardcode credentials, API keys, or secrets
2. **NEVER** commit .env files with real values
3. **ALWAYS** use environment variables or secrets managers
4. **ALWAYS** use placeholder values in examples
5. **ALWAYS** validate configuration before deployment

## Common Violations

- Hardcoded OAuth credentials
- Account-specific URLs
- Real UUIDs or keys in examples
- Database connection strings with passwords
- AWS access keys or secret keys

## Fixing Violations

1. Replace hardcoded values with placeholders
2. Use environment variables for real values
3. Add validation for required parameters
4. Update documentation with proper examples
5. Test the security checks again

## Tools Used

- `scripts/security-check.sh`: Custom security validation
- `detect-secrets`: Automated secret detection
- `pre-commit`: Git hook management
- `bandit`: Python security linting
- `flake8`: Code quality checks
EOF
    
    print_success "Security documentation created!"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install    - Install all security hooks and tools (default)"
    echo "  test       - Test security checks"
    echo "  docs       - Create security documentation"
    echo "  all        - Install, test, and create docs"
    echo "  help       - Show this help message"
    echo ""
    echo "This script sets up security checks to prevent:"
    echo "  - Hardcoded credentials"
    echo "  - Account-specific data"
    echo "  - Security vulnerabilities"
    echo "  - Sloppy practices"
}

# Main function
main() {
    case "${1:-install}" in
        "install")
            install_pre_commit
            setup_git_hooks
            create_secrets_baseline
            ;;
        "test")
            test_security_checks
            ;;
        "docs")
            create_documentation
            ;;
        "all")
            install_pre_commit
            setup_git_hooks
            create_secrets_baseline
            test_security_checks
            create_documentation
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
    
    print_header "Setup Complete!"
    print_status "Security hooks are now active."
    print_status "Run './scripts/security-check.sh' to test manually."
    print_status "Security checks will run automatically on git commit."
}

# Run main function
main "$@" 