#!/bin/bash

# Security Check Script
# This script checks for hardcoded credentials, security vulnerabilities, and sloppy practices
# Use as a pre-commit hook or run manually

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check for hardcoded credentials
check_hardcoded_credentials() {
    print_header "Checking for Hardcoded Credentials"
    
    local violations=0
    
    # Check for common credential patterns
    local patterns=(
        "AKIA[0-9A-Z]{16}"                    # AWS Access Key ID
        "[0-9a-zA-Z/+]{40}"                   # AWS Secret Access Key
        "sk-[0-9a-zA-Z]{48}"                  # OpenAI API Key
        "pk-[0-9a-zA-Z]{48}"                  # OpenAI API Key
        "[0-9a-zA-Z]{32}"                     # Generic API Key
        "ghp_[0-9a-zA-Z]{36}"                 # GitHub Personal Access Token
        "gho_[0-9a-zA-Z]{36}"                 # GitHub OAuth Token
        "ghu_[0-9a-zA-Z]{36}"                 # GitHub User-to-Server Token
        "ghs_[0-9a-zA-Z]{36}"                 # GitHub Server-to-Server Token
        "ghr_[0-9a-zA-Z]{36}"                 # GitHub Refresh Token
        "Bearer [0-9a-zA-Z._-]+"              # Bearer tokens
        "Basic [0-9a-zA-Z+/=]+"               # Basic auth
        "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"  # UUIDs
        "password.*=.*[^\"'\\s]+"             # Password assignments
        "secret.*=.*[^\"'\\s]+"               # Secret assignments
        "token.*=.*[^\"'\\s]+"                # Token assignments
        "key.*=.*[\"'][^\"']+[\"']"           # Key assignments with quotes (actual secrets)
        "credential.*=.*[^\"'\\s]+"           # Credential assignments (but exclude variable assignments)
    )
    
    for pattern in "${patterns[@]}"; do
        # Skip ParameterKey patterns which are legitimate
        if [[ "$pattern" == *"key.*=.*"* ]]; then
            local matches
            matches=$(grep -r -E "$pattern" . --exclude-dir=.git --exclude-dir=node_modules --exclude=*.log --exclude=security-check.sh 2>/dev/null | grep -v "ParameterKey" | grep -v "values\[" || true)
        elif [[ "$pattern" == *"credential.*=.*"* ]]; then
            local matches
            matches=$(grep -r -E "$pattern" . --exclude-dir=.git --exclude-dir=node_modules --exclude=*.log --exclude=security-check.sh 2>/dev/null | grep -v "values\[" || true)
        else
            local matches
            matches=$(grep -r -E "$pattern" . --exclude-dir=.git --exclude-dir=node_modules --exclude=*.log --exclude=security-check.sh 2>/dev/null || true)
        fi
        if [ -n "$matches" ]; then
            print_error "Found potential hardcoded credentials with pattern: $pattern"
            echo "$matches" | head -5
            violations=$((violations + 1))
        fi
    done
    
    if [ "$violations" -eq 0 ]; then
        print_success "No hardcoded credentials found"
    else
        print_error "Found $violations potential credential violations"
    fi
    
    return $violations
}

# Function to check for account-specific URLs and identifiers
check_account_specific_data() {
    print_header "Checking for Account-Specific Data"
    
    local violations=0
    
    # Check for common account-specific patterns
    local patterns=(
        "https://[a-z0-9-]+\\.snowflakecomputing\\.com"  # Snowflake URLs
        "https://[a-z0-9-]+\\.aws\\.snowflake-customer\\.app"  # Snowflake customer URLs
        "[A-Z]{6,}-[A-Z0-9]{8}"                          # Snowflake account patterns
        "[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"  # UUIDs
        "arn:aws:[a-z-]+:[0-9]{12}:"                      # AWS ARNs
        "[0-9]{12}"                                        # AWS Account IDs
    )
    
    for pattern in "${patterns[@]}"; do
        local matches
        matches=$(grep -r -E "$pattern" . --exclude-dir=.git --exclude-dir=node_modules --exclude=*.log 2>/dev/null || true)
        if [ -n "$matches" ]; then
            print_warning "Found potential account-specific data with pattern: $pattern"
            echo "$matches" | head -3
            violations=$((violations + 1))
        fi
    done
    
    if [ "$violations" -eq 0 ]; then
        print_success "No account-specific data found"
    else
        print_warning "Found $violations potential account-specific data violations"
    fi
    
    return $violations
}

# Function to check for hardcoded values in CloudFormation templates
check_cloudformation_hardcoded() {
    print_header "Checking CloudFormation Templates for Hardcoded Values"
    
    local violations=0
    
    # Check for hardcoded values in CloudFormation parameters
    local hardcoded_patterns=(
        "Default: https://[^\"']+"
        "Default: [A-Z0-9]{8,}"
        "Default: [a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
        "Default: [A-Z]{6,}-[A-Z0-9]{8}"
    )
    
    for pattern in "${hardcoded_patterns[@]}"; do
        local matches
        matches=$(grep -r -E "$pattern" . --include="*.yaml" --include="*.yml" --exclude-dir=.git 2>/dev/null || true)
        if [ -n "$matches" ]; then
            print_error "Found hardcoded values in CloudFormation templates: $pattern"
            echo "$matches"
            violations=$((violations + 1))
        fi
    done
    
    if [ "$violations" -eq 0 ]; then
        print_success "No hardcoded values found in CloudFormation templates"
    else
        print_error "Found $violations hardcoded value violations in CloudFormation templates"
    fi
    
    return $violations
}

# Function to check for .env files with real values
check_env_files() {
    print_header "Checking .env Files"
    
    local violations=0
    
    # Check for .env files that might contain real credentials
    if [ -f ".env" ]; then
        print_warning "Found .env file - checking for real credentials"
        
        # Check for placeholder values that should be replaced
        local placeholder_patterns=(
            "YOUR_"
            "PLACEHOLDER"
            "REPLACE_"
            "EXAMPLE_"
        )
        
        for pattern in "${placeholder_patterns[@]}"; do
            local matches=$(grep -E "$pattern" .env 2>/dev/null || true)
            if [ -n "$matches" ]; then
                print_warning "Found placeholder values in .env file: $pattern"
                echo "$matches" | head -3
            fi
        done
        
        # Check for real-looking values
        local real_patterns=(
            "https://[a-z0-9-]+\\.snowflakecomputing\\.com"
            "[A-Z0-9]{8,}"
            "[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
        )
        
        for pattern in "${real_patterns[@]}"; do
            local matches=$(grep -E "$pattern" .env 2>/dev/null || true)
            if [ -n "$matches" ]; then
                print_error "Found real-looking values in .env file: $pattern"
                echo "$matches"
                violations=$((violations + 1))
            fi
        done
    else
        print_success "No .env file found"
    fi
    
    return $violations
}

# Function to check for proper placeholder usage
check_placeholder_usage() {
    print_header "Checking for Proper Placeholder Usage"
    
    local violations=0
    
    # Check that example files use proper placeholders
    local example_files=(
        "config.env.example"
        "*.template"
        "*.example"
    )
    
    for file_pattern in "${example_files[@]}"; do
        for file in $(find . -name "$file_pattern" -not -path "./.git/*" 2>/dev/null); do
            # Check for real-looking values in example files
            local real_patterns=(
                "https://[a-z0-9-]+\\.snowflakecomputing\\.com"
                "[A-Z0-9]{8,}"
                "[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
            )
            
            for pattern in "${real_patterns[@]}"; do
                local matches=$(grep -E "$pattern" "$file" 2>/dev/null || true)
                if [ -n "$matches" ]; then
                    print_error "Found real-looking values in example file $file: $pattern"
                    echo "$matches"
                    violations=$((violations + 1))
                fi
            done
        done
    done
    
    if [ "$violations" -eq 0 ]; then
        print_success "Example files use proper placeholders"
    else
        print_error "Found $violations violations in example files"
    fi
    
    return $violations
}

# Function to check for required parameter validation
check_parameter_validation() {
    print_header "Checking for Parameter Validation"
    
    local violations=0
    
    # Check for CloudFormation parameters without defaults (good)
    local required_params=$(grep -r "Type: String" . --include="*.yaml" --include="*.yml" --exclude-dir=.git | grep -v "Default:" | wc -l)
    
    # Check for parameters with hardcoded defaults (bad)
    local hardcoded_defaults=$(grep -r "Default:" . --include="*.yaml" --include="*.yml" --exclude-dir=.git | grep -E "(https://|UUID|KEY|SECRET)" | wc -l)
    
    if [ "$hardcoded_defaults" -gt 0 ]; then
        print_error "Found $hardcoded_defaults parameters with hardcoded defaults"
        violations=$((violations + hardcoded_defaults))
    fi
    
    if [ "$required_params" -gt 0 ]; then
        print_success "Found $required_params required parameters (good)"
    fi
    
    return $violations
}

# Main function
main() {
    print_header "Security Check Started"
    
    local total_violations=0
    local checks=0
    
    # Run all checks
    check_hardcoded_credentials
    total_violations=$((total_violations + $?))
    checks=$((checks + 1))
    
    check_account_specific_data
    total_violations=$((total_violations + $?))
    checks=$((checks + 1))
    
    check_cloudformation_hardcoded
    total_violations=$((total_violations + $?))
    checks=$((checks + 1))
    
    check_env_files
    total_violations=$((total_violations + $?))
    checks=$((checks + 1))
    
    check_placeholder_usage
    total_violations=$((total_violations + $?))
    checks=$((checks + 1))
    
    check_parameter_validation
    total_violations=$((total_violations + $?))
    checks=$((checks + 1))
    
    # Summary
    print_header "Security Check Summary"
    echo "Checks performed: $checks"
    echo "Total violations found: $total_violations"
    
    if [ "$total_violations" -eq 0 ]; then
        print_success "All security checks passed! ✅"
        exit 0
    else
        print_error "Security violations found! ❌"
        print_error "Please fix the violations before committing."
        exit 1
    fi
}

# Run main function
main "$@" 