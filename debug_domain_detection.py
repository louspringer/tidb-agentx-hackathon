#!/usr/bin/env python3
"""
Debug domain detection issues
"""

import json
from pathlib import Path

def debug_domain_detection():
    """Debug why domain detection isn't working"""
    
    # Load the model
    with open('project_model_registry.json', 'r') as f:
        model_data = json.load(f)
    
    # Test specific files that should be detected
    test_files = [
        'src/mcp_integration/github_mcp_client.py',
        'src/ghostbusters/agents/mcp_expert.py',
        'data/.cursor/rules/data-management.mdc',
        'tests/test_ghostbusters_gcp.py'
    ]
    
    print("🔍 Debug Domain Detection")
    print("=" * 50)
    
    for file_path in test_files:
        print(f"\n📁 Testing: {file_path}")
        
        # Check if file exists
        if not Path(file_path).exists():
            print(f"❌ File does not exist: {file_path}")
            continue
        
        # Test pattern matching for each domain
        best_match = None
        best_score = 0
        best_pattern = None
        best_domain = None
        
        for domain_name, domain_config in model_data['domains'].items():
            patterns = domain_config.get('patterns', [])
            
            for pattern in patterns:
                if matches_pattern(file_path, pattern):
                    score = calculate_pattern_score(pattern)
                    if score > best_score:
                        best_score = score
                        best_match = pattern
                        best_domain = domain_name
        
        if best_domain:
            print(f"✅ Matched pattern '{best_match}' (score: {best_score}) -> domain: {best_domain}")
        else:
            print(f"❌ No domain matched for {file_path}")
            
            # Show what patterns exist for missing domains
            missing_domains = ['mcp_integration', 'mdc_generator', 'ghostbusters_gcp']
            for domain in missing_domains:
                if domain in model_data['domains']:
                    patterns = model_data['domains'][domain].get('patterns', [])
                    print(f"  {domain} patterns: {patterns}")

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

def calculate_pattern_score(pattern: str) -> int:
    """Calculate pattern specificity score"""
    if pattern == '*.py':
        return 1  # Lowest priority for generic Python pattern
    elif pattern == '*.mdc':
        return 1  # Lowest priority for generic MDC pattern
    elif '*' in pattern:
        # Count path segments for specificity
        parts = pattern.split('/')
        # More specific patterns (with more path segments) get higher scores
        specificity = len([p for p in parts if p != '*'])
        # Exact path matches get bonus points
        if pattern.count('*') == 1 and pattern.endswith('*.py'):
            specificity += 10
        # Domain-specific patterns get higher priority
        if any(domain in pattern for domain in ['mcp', 'ghostbusters', 'streamlit', 'healthcare']):
            specificity += 20
        return specificity
    else:
        # Exact match gets highest priority
        return 100

if __name__ == "__main__":
    debug_domain_detection()
