#!/bin/bash
# Rule Compliance Checker
# Validates that files follow deterministic editing rules and other coding standards

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RULES_DIR="$PROJECT_ROOT/.cursor/rules"
VIOLATIONS=0
TOTAL_CHECKS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((VIOLATIONS++))
}

# Check if file uses deterministic editing
check_deterministic_editing() {
    local file="$1"
    local file_type="${file##*.}"
    
    case "$file_type" in
        yaml|yml|json|toml|ini|cfg|mdc|py|xml|properties|env)
            log_info "Checking deterministic editing for $file"
            
            # Check for common non-deterministic patterns
            if grep -q "edit_file" "$file" 2>/dev/null; then
                log_error "File $file may use non-deterministic edit_file tool"
                return 1
            fi
            
            # Check for proper YAML frontmatter in .mdc files
            if [[ "$file_type" == "mdc" ]]; then
                if ! grep -q "^---$" "$file" 2>/dev/null; then
                    log_error "File $file missing YAML frontmatter"
                    return 1
                fi
                
                if ! grep -q "description:" "$file" 2>/dev/null; then
                    log_error "File $file missing description in frontmatter"
                    return 1
                fi
                
                if ! grep -q "globs:" "$file" 2>/dev/null; then
                    log_error "File $file missing globs in frontmatter"
                    return 1
                fi
            fi
            
            log_success "File $file passes deterministic editing checks"
            ;;
    esac
    return 0
}

# Check security compliance
check_security_compliance() {
    local file="$1"
    
    log_info "Checking security compliance for $file"
    
    # Check for hardcoded credentials
    if grep -q -E "(password|secret|key|token).*=.*['\"][^'\"]*['\"]" "$file" 2>/dev/null; then
        log_error "File $file contains potential hardcoded credentials"
        return 1
    fi
    
    # Check for AWS keys
    if grep -q "AKIA[0-9A-Z]\{16\}" "$file" 2>/dev/null; then
        log_error "File $file contains potential AWS access keys"
        return 1
    fi
    
    # Check for UUID patterns
    if grep -q "[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}" "$file" 2>/dev/null; then
        log_warning "File $file contains UUID patterns (may be legitimate)"
    fi
    
    log_success "File $file passes security compliance checks"
    return 0
}

# Check .mdc file structure
check_mdc_structure() {
    local file="$1"
    
    if [[ "${file##*.}" != "mdc" ]]; then
        return 0
    fi
    
    log_info "Checking .mdc file structure for $file"
    
    # Check for proper YAML frontmatter
    if ! awk '/^---$/{count++} END{exit count!=2}' "$file" 2>/dev/null; then
        log_error "File $file has incorrect YAML frontmatter structure"
        return 1
    fi
    
    # Check for required frontmatter fields
    local has_description=false
    local has_globs=false
    local has_always_apply=false
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^description: ]]; then
            has_description=true
        elif [[ "$line" =~ ^globs: ]]; then
            has_globs=true
        elif [[ "$line" =~ ^alwaysApply: ]]; then
            has_always_apply=true
        fi
    done < "$file"
    
    if [[ "$has_description" == "false" ]]; then
        log_error "File $file missing description field"
        return 1
    fi
    
    if [[ "$has_globs" == "false" ]]; then
        log_error "File $file missing globs field"
        return 1
    fi
    
    if [[ "$has_always_apply" == "false" ]]; then
        log_error "File $file missing alwaysApply field"
        return 1
    fi
    
    log_success "File $file has correct .mdc structure"
    return 0
}

# Check file organization compliance
check_file_organization() {
    local file="$1"
    
    log_info "Checking file organization compliance for $file"
    
    # Check if file is in appropriate directory based on type
    local file_type="${file##*.}"
    local dir_name="$(dirname "$file")"
    
    case "$file_type" in
        py)
            if [[ "$dir_name" == "src/"* ]] || [[ "$dir_name" == "tests/" ]] || [[ "$dir_name" == "scripts/" ]]; then
                log_success "Python file $file is in appropriate directory"
            else
                log_warning "Python file $file may be in wrong directory"
            fi
            ;;
        md)
            if [[ "$dir_name" == "docs/" ]] || [[ "$dir_name" == "." ]] || [[ "$dir_name" == "healthcare-cdc/" ]]; then
                log_success "Markdown file $file is in appropriate directory"
            else
                log_warning "Markdown file $file may be in wrong directory"
            fi
            ;;
        yaml|yml)
            if [[ "$dir_name" == "config/" ]] || [[ "$dir_name" == "." ]]; then
                log_success "YAML file $file is in appropriate directory"
            else
                log_warning "YAML file $file may be in wrong directory"
            fi
            ;;
        json)
            if [[ "$dir_name" == "data/" ]] || [[ "$dir_name" == "config/" ]] || [[ "$dir_name" == "." ]]; then
                log_success "JSON file $file is in appropriate directory"
            else
                log_warning "JSON file $file may be in wrong directory"
            fi
            ;;
    esac
}

# Main validation function
validate_file() {
    local file="$1"
    ((TOTAL_CHECKS++))
    
    log_info "Validating file: $file"
    
    local has_violations=false
    
    # Run all checks
    if ! check_deterministic_editing "$file"; then
        has_violations=true
    fi
    
    if ! check_security_compliance "$file"; then
        has_violations=true
    fi
    
    if ! check_mdc_structure "$file"; then
        has_violations=true
    fi
    
    check_file_organization "$file"
    
    if [[ "$has_violations" == "true" ]]; then
        return 1
    fi
    
    return 0
}

# Process all files
main() {
    log_info "Starting rule compliance check"
    
    # Get list of files to check (excluding git, node_modules, etc.)
    local files_to_check
    files_to_check=$(find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.mdc" -o -name "*.sh" \) \
        -not -path "./.git/*" \
        -not -path "./node_modules/*" \
        -not -path "./__pycache__/*" \
        -not -path "./.pytest_cache/*" \
        -not -path "./.mypy_cache/*" \
        -not -path "./venv/*" \
        -not -path "./.venv/*" \
        -not -path "./env/*" \
        -not -path "./.env/*")
    
    local failed_files=0
    
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            if ! validate_file "$file"; then
                ((failed_files++))
            fi
        fi
    done <<< "$files_to_check"
    
    # Summary
    echo
    log_info "Rule compliance check completed"
    log_info "Total files checked: $TOTAL_CHECKS"
    log_info "Violations found: $VIOLATIONS"
    log_info "Files with issues: $failed_files"
    
    if [[ $VIOLATIONS -eq 0 ]]; then
        log_success "All files pass rule compliance checks!"
        exit 0
    else
        log_error "Found $VIOLATIONS violations. Please fix before committing."
        exit 1
    fi
}

# Run main function
main "$@" 