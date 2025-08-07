#!/usr/bin/env python3
"""
Enhanced Billing Analyzer Generator with Recursive Decomposition
Uses the recursive code generator to create more robust, validated code
"""

import logging
from pathlib import Path

from generate_billing_analyzer import generate_gemini_billing_analyzer

from recursive_code_generator import RecursiveCodeGenerator


def main():
    """Generate billing analyzer with recursive decomposition"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("🚀 Generating Enhanced Billing Analyzer with Recursive Decomposition...")

    # Create recursive generator
    generator = RecursiveCodeGenerator()

    # Generate the billing analyzer model
    print("📊 Creating billing analyzer model...")
    analyzer_file = generate_gemini_billing_analyzer()

    # Generate with recursive decomposition
    print("🔍 Applying recursive decomposition...")
    result = generator.generate_with_recursion(analyzer_file)

    # Write to file
    output_path = Path("gemini_billing_analyzer_enhanced.py")
    success = generator.write_file(analyzer_file, output_path)

    if success:
        print("🎉 Enhanced Billing Analyzer generated successfully!")
        print("✅ Recursive decomposition applied!")
        print(f"📁 Output: {output_path}")

        # Show decomposition summary
        print("\n📊 Decomposition Analysis:")
        generator._log_decomposition_summary()

    else:
        print("❌ Generation failed!")


if __name__ == "__main__":
    main()
