#!/usr/bin/env python3
"""
Test pattern matching for specific files
"""


def matches_pattern(file_path: str, pattern: str) -> bool:
    """Check if file path matches pattern"""
    if "*" in pattern:
        # Convert glob pattern to simple matching
        pattern_parts = pattern.replace("*", "").split("/")
        file_parts = file_path.split("/")

        # Check if pattern parts are in file parts
        pattern_idx = 0
        for part in file_parts:
            if pattern_idx < len(pattern_parts) and pattern_parts[pattern_idx] in part:
                pattern_idx += 1
                if pattern_idx >= len(pattern_parts):
                    return True
        return pattern_idx >= len(pattern_parts)
    return pattern in file_path


def test_specific_patterns():
    """Test specific pattern matching"""

    test_cases = [
        ("src/mcp_integration/github_mcp_client.py", "src/mcp_integration/*.py"),
        (
            "src/ghostbusters_gcp/embedded_ghostbusters_main.py",
            "src/ghostbusters_gcp/*.py",
        ),
        ("src/mdc_generator/mdc_model.py", "src/mdc_generator/*.py"),
        ("tests/test_ghostbusters_gcp.py", "tests/test_ghostbusters_gcp*.py"),
        ("data/.cursor/rules/data-management.mdc", "**/*.mdc"),
    ]

    print("🔍 Testing Pattern Matching")
    print("=" * 50)

    for file_path, pattern in test_cases:
        result = matches_pattern(file_path, pattern)
        print(f"📁 {file_path}")
        print(f"   Pattern: {pattern}")
        print(f"   Match: {'✅' if result else '❌'}")
        print()


if __name__ == "__main__":
    test_specific_patterns()
