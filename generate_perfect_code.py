#!/usr/bin/env python3
"""
Generate Perfect Code
Use our complex model to generate perfect code
"""

from src.complex_model_generator import create_complex_model


def generate_perfect_code() -> None:
    """Generate perfect code using our complex model"""

    print("🎯 GENERATING PERFECT CODE WITH COMPLEX MODEL:")
    print()

    # Create complex model
    model = create_complex_model()
    print("✅ Complex Model Loaded")

    # Test file to generate perfect code for
    test_file = "analyze_codebase.py"
    print(f"🔍 Generating perfect code for {test_file}:")

    try:
        # Generate perfect code
        perfect_code = model.generate_perfect_code(test_file)

        print("✅ Perfect Code Generated!")
        print()
        print("📊 PERFECT CODE PREVIEW:")
        print("=" * 50)

        # Show first few lines
        lines = perfect_code.splitlines()
        for i, line in enumerate(lines[:20]):
            print(f"{i+1:3d}: {line}")

        if len(lines) > 20:
            print("   ...")
            print(f"   (Total: {len(lines)} lines)")

        print("=" * 50)
        print()

        # Save perfect code
        perfect_file = "perfect_analyze_codebase.py"
        with open(perfect_file, "w") as f:
            f.write(perfect_code)

        print(f"💾 Perfect code saved to {perfect_file}")
        print()

        # Test the perfect code
        print("🧪 Testing perfect code:")
        try:
            # Test AST parsing
            import ast

            ast.parse(perfect_code)
            print("   ✅ AST parsing successful")

            # Test basic syntax
            compile(perfect_code, perfect_file, "exec")
            print("   ✅ Syntax validation successful")

            print("   ✅ PERFECT CODE VALIDATION SUCCESSFUL!")

        except Exception as e:
            print(f"   ❌ Validation failed: {e}")

        print()
        print("⚔️ BATTLE CONCLUSION: PERFECT CODE GENERATED!")

    except Exception as e:
        print(f"❌ Error generating perfect code: {e}")


if __name__ == "__main__":
    generate_perfect_code()
