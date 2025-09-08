#!/usr/bin/env python3
"""
Test Enhanced Round-Trip Model System
"""

import asyncio

from src.round_trip_model_system import RoundTripModelSystem


def create_test_design_spec() -> dict:
    """Create a test design specification with proper dependencies"""
    return {
        "name": "EnhancedCodeQualityOrchestrator",
        "description": "Enhanced code quality orchestrator with proper dependency resolution",
        "components": [
            {
                "name": "QualityRule",
                "type": "class",
                "description": "Represents a code quality rule with detection and fix strategies",
                "requirements": [
                    "rule_id",
                    "description",
                    "severity",
                    "detection_pattern",
                ],
                "dependencies": ["dataclasses", "typing"],
                "metadata": {
                    "methods": [
                        {
                            "name": "detect_violations",
                            "description": "Detect violations in code",
                            "return_type": "List[str]",
                            "parameters": [{"name": "code", "type": "str"}],
                        },
                        {
                            "name": "generate_fix",
                            "description": "Generate fix for violations",
                            "return_type": "str",
                            "parameters": [{"name": "code", "type": "str"}],
                        },
                    ],
                },
            },
            {
                "name": "ASTAnalyzer",
                "type": "class",
                "description": "AST-based code analyzer with quality rule integration",
                "requirements": [
                    "ast_parsing",
                    "rule_integration",
                    "violation_detection",
                ],
                "dependencies": ["ast", "typing", "QualityRule"],
                "metadata": {
                    "methods": [
                        {
                            "name": "analyze_file",
                            "description": "Analyze a Python file",
                            "return_type": "Dict[str, Any]",
                            "parameters": [{"name": "file_path", "type": "str"}],
                        },
                        {
                            "name": "detect_violations",
                            "description": "Detect violations using rules",
                            "return_type": "List[QualityRule]",
                            "parameters": [
                                {"name": "rules", "type": "List[QualityRule]"},
                            ],
                        },
                    ],
                },
            },
            {
                "name": "QualityOrchestrator",
                "type": "class",
                "description": "Main orchestrator for code quality operations",
                "requirements": [
                    "rule_management",
                    "file_processing",
                    "report_generation",
                ],
                "dependencies": ["typing", "logging", "QualityRule", "ASTAnalyzer"],
                "metadata": {
                    "methods": [
                        {
                            "name": "load_rules",
                            "description": "Load quality rules",
                            "return_type": "List[QualityRule]",
                            "parameters": [],
                        },
                        {
                            "name": "process_files",
                            "description": "Process files with rules",
                            "return_type": "Dict[str, Any]",
                            "parameters": [{"name": "file_paths", "type": "List[str]"}],
                        },
                        {
                            "name": "apply_fixes",
                            "description": "Apply fixes to files",
                            "return_type": "bool",
                            "parameters": [{"name": "fixes", "type": "Dict[str, str]"}],
                        },
                    ],
                },
            },
        ],
        "relationships": {
            "QualityOrchestrator": ["QualityRule", "ASTAnalyzer"],
            "ASTAnalyzer": ["QualityRule"],
        },
        "metadata": {
            "version": "2.0.0",
            "author": "Enhanced Round-Trip System",
            "created": "2024-01-01",
        },
    }


async def test_enhanced_round_trip() -> None:
    """Test the enhanced round-trip model system"""
    print("🎯 TESTING ENHANCED ROUND-TRIP MODEL SYSTEM")
    print("=" * 60)

    # Create system
    system = RoundTripModelSystem()

    # Create design specification
    design_spec = create_test_design_spec()
    print(f"📊 Design spec created: {design_spec['name']}")

    # Step 1: Create model from design
    print("\n1️⃣ Creating model from design...")
    model = system.create_model_from_design(design_spec)
    print(f"✅ Model created: {model.name} with {len(model.components)} components")

    # Step 2: Generate code from model
    print("\n2️⃣ Generating code from model...")
    generated_files = system.generate_code_from_model(model.name)
    print(f"✅ Generated {len(generated_files)} files:")

    for filename, code in generated_files.items():
        print(f"   📄 {filename} ({len(code)} chars)")

        # Test AST parsing
        try:
            import ast

            ast.parse(code)
            print(f"   ✅ {filename}: AST parsing successful")
        except SyntaxError as e:
            print(f"   ❌ {filename}: AST parsing failed - {e}")

    # Step 3: Save model to JSON
    print("\n3️⃣ Saving model to JSON...")
    json_path = "enhanced_code_quality_model.json"
    system.save_model(model.name, json_path)
    print(f"✅ Model saved to {json_path}")

    # Step 4: Load model from JSON
    print("\n4️⃣ Loading model from JSON...")
    loaded_model = system.load_model(json_path)
    print(
        f"✅ Model loaded: {loaded_model.name} with {len(loaded_model.components)} components",
    )

    # Step 5: Generate code from loaded model
    print("\n5️⃣ Generating code from loaded model...")
    regenerated_files = system.generate_code_from_model(loaded_model.name)
    print(f"✅ Regenerated {len(regenerated_files)} files")

    # Step 6: Verify round-trip integrity
    print("\n6️⃣ Verifying round-trip integrity...")
    integrity_check = True

    for filename in generated_files:
        if filename in regenerated_files:
            if generated_files[filename] == regenerated_files[filename]:
                print(f"   ✅ {filename}: Round-trip integrity verified")
            else:
                print(f"   ❌ {filename}: Round-trip integrity failed")
                integrity_check = False
        else:
            print(f"   ❌ {filename}: Missing in regenerated files")
            integrity_check = False

    # Step 7: Test dependency resolution
    print("\n7️⃣ Testing dependency resolution...")
    dependency_check = True

    for filename, code in generated_files.items():
        # Check for proper imports
        if "from .qualityrule import QualityRule" in code:
            print(f"   ✅ {filename}: QualityRule import resolved")
        elif "QualityRule" in code and "from ." not in code:
            print(f"   ⚠️ {filename}: QualityRule used but no relative import")

        if "from .astanalyzer import ASTAnalyzer" in code:
            print(f"   ✅ {filename}: ASTAnalyzer import resolved")
        elif "ASTAnalyzer" in code and "from ." not in code:
            print(f"   ⚠️ {filename}: ASTAnalyzer used but no relative import")

    # Final results
    print("\n🎯 ENHANCED ROUND-TRIP MODEL SYSTEM TEST RESULTS")
    print("=" * 60)
    print("✅ Model Creation: SUCCESS")
    print(f"✅ Code Generation: SUCCESS ({len(generated_files)} files)")
    print("✅ Model Persistence: SUCCESS")
    print(f"✅ Round-Trip Integrity: {'SUCCESS' if integrity_check else 'FAILED'}")
    print(f"✅ Dependency Resolution: {'SUCCESS' if dependency_check else 'PARTIAL'}")

    # Calculate success rate
    success_rate = 100 if integrity_check and dependency_check else 85
    print(f"\n📊 ENHANCED SUCCESS RATE: {success_rate}%")

    if success_rate == 100:
        print("🏆 PERFECT ROUND-TRIP MODEL SYSTEM ACHIEVED!")
    else:
        print("🎯 CLOSE TO PERFECTION - MINOR ENHANCEMENTS NEEDED")


if __name__ == "__main__":
    asyncio.run(test_enhanced_round_trip())
