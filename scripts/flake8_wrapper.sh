#!/bin/bash
# flake8 wrapper - only allows execution through make

check_parent_process() {
    local parent_pid=$(ps -o ppid= -p $$)
    local parent_name=$(ps -o comm= -p $parent_pid)
    
    # Allow if parent is make
    if [[ "$parent_name" == "make" ]]; then
        return 0
    fi
    
    # Allow if we're in a make environment
    if [[ -n "$MAKEFLAGS" || -n "$MAKELEVEL" ]]; then
        return 0
    fi
    
    # Block direct execution
    echo "❌ ERROR: flake8 can only be executed through make"
    echo "✅ Use: make flake8"
    echo "📋 Available targets:"
    echo "   - make flake8"
    echo "   - make flake8-all"
    echo "   - make flake8-python"
    exit 1
}

check_parent_process
exec /home/lou/.local/bin/flake8.original "$@"
