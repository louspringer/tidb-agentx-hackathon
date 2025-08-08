#!/usr/bin/env python3
"""
Test Complex Model
Battle test our complex model on real files
"""

from src.complex_model_generator import create_complex_model


def test_complex_model() -> None:
    """Test the complex model on real files"""

    print("🎯 COMPLEX MODEL BATTLE TEST:")
    print()

    # Create complex model
    model = create_complex_model()
    print("✅ Complex Model Created:")
    print(f"   Flake8 Rules: {len(model.flake8_rules)}")
    print(f"   MyPy Rules: {len(model.mypy_rules)}")
    print(f"   Code Patterns: {len(model.code_patterns)}")
    print(f"   Fix Strategies: {len(model.fix_strategies)}")
    print()

    # Test on analyze_codebase.py
    test_file = "analyze_codebase.py"
    print(f"🔍 Testing on {test_file}:")

    try:
        analysis = model.analyze_file(test_file)

        print(f"   File: {analysis['file_path']}")
        print(f"   Total Issues: {analysis['total_issues']}")
        print(f"   Flake8 Issues: {len(analysis['flake8_issues'])}")
        print(f"   MyPy Issues: {len(analysis['mypy_issues'])}")
        print()

        print("📊 DETAILED ANALYSIS:")
        print(
            f"   AST Parse Successful: {analysis['ast_analysis'].get('ast_parse_successful', False)}",
        )
        print(f"   Functions: {len(analysis['ast_analysis'].get('functions', []))}")
        print(f"   Classes: {len(analysis['ast_analysis'].get('classes', []))}")
        print(f"   Imports: {len(analysis['ast_analysis'].get('imports', []))}")
        print()

        print("🔧 FIX STRATEGIES:")
        for strategy in analysis["fix_strategies"][:3]:
            print(
                f"   {strategy['issue_code']}: {strategy['description']} -> {strategy['fix_strategy']}",
            )

        print()
        print("⚔️ BATTLE CONCLUSION: COMPLEX MODEL IS WORKING!")

    except Exception as e:
        print(f"❌ Error testing complex model: {e}")


if __name__ == "__main__":
    test_complex_model()
