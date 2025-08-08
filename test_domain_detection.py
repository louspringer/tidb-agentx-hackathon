#!/usr/bin/env python3
"""
Test domain detection for specific files
"""

import json
from pathlib import Path

def test_domain_detection():
    """Test domain detection for specific files"""
    
    # Load the model
    with open('project_model_registry.json', 'r') as f:
        model_data = json.load(f)
    
    # Test files
    test_files = [
        'src/ghostbusters/ghostbusters_orchestrator.py',
        'src/streamlit/openflow_quickstart_app.py',
        'src/mcp_integration/github_mcp_client.py',
        'src/ghostbusters_gcp/embedded_ghostbusters_main.py'
    ]
    
    print("🔍 Testing Domain Detection")
    print("=" * 50)
    
    for file_path in test_files:
        print(f"\n📁 Testing: {file_path}")
        
        # Check if file exists
        if not Path(file_path).exists():
            print(f"❌ File does not exist: {file_path}")
            continue
        
        # Test pattern matching with scoring
        best_match = None
        best_score = 0
        best_pattern = None
        
        for domain_name, domain_config in model_data['domains'].items():
            patterns = domain_config.get('patterns', [])
            
            for pattern in patterns:
                if matches_pattern(file_path, pattern):
                    score = calculate_pattern_score(pattern)
                    if score > best_score:
                        best_score = score
                        best_match = domain_name
                        best_pattern = pattern
        
        if best_match:
            print(f"✅ Matched pattern '{best_pattern}' (score: {best_score}) -> domain: {best_match}")
        else:
            print(f"❌ No domain matched for {file_path}")
            
            # Show available patterns
            print("Available patterns:")
            for domain_name, domain_config in model_data['domains'].items():
                patterns = domain_config.get('patterns', [])
                if patterns:
                    print(f"  {domain_name}: {patterns}")

def calculate_pattern_score(pattern: str) -> int:
    """Calculate pattern specificity score"""
    if pattern == '*.py':
        return 1  # Lowest priority for generic Python pattern
    elif '*' in pattern:
        # Count path segments for specificity
        parts = pattern.split('/')
        return len([p for p in parts if p != '*'])
    else:
        # Exact match gets highest priority
        return 100

def matches_pattern(file_path: str, pattern: str) -> bool:
    """Simple pattern matching"""
    if '*' in pattern:
        # Convert glob pattern to simple matching
        pattern_parts = pattern.replace('*', '').split('/')
        file_parts = file_path.split('/')
        
        # Check if pattern parts are in file parts
        pattern_idx = 0
        for part in file_parts:
            if pattern_idx < len(pattern_parts) and pattern_parts[pattern_idx] in part:
                pattern_idx += 1
                if pattern_idx >= len(pattern_parts):
                    return True
        return pattern_idx >= len(pattern_parts)
    else:
        return pattern in file_path

if __name__ == "__main__":
    test_domain_detection()
