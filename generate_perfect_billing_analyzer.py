#!/usr/bin/env python3
"""
Generate Perfect Billing Analyzer
Uses PerfectCodeGenerator to create linting-compliant code
"""

import logging
from pathlib import Path

from generate_billing_analyzer import generate_gemini_billing_analyzer
from perfect_code_generator import PerfectCodeGenerator


def main():
    """Generate perfect billing analyzer"""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Generating PERFECT Billing Analyzer!")
    print("🎯 Using PerfectCodeGenerator for linting-compliant code!")

    # Create perfect generator
    generator = PerfectCodeGenerator()

    # Generate the billing analyzer model
    print("📊 Creating billing analyzer model...")
    analyzer_file = generate_gemini_billing_analyzer()

    # Generate perfect code
    print("🔧 Generating perfect code with linting validation...")
    output_path = Path("perfect_billing_analyzer.py")
    success = generator.write_perfect_file(analyzer_file, output_path)

    if success:
        print("🎉 PERFECT Billing Analyzer generated successfully!")
        print(f"📁 Output: {output_path}")
        print("✅ Code passes all linting checks!")
    else:
        print("❌ Perfect generation failed!")


if __name__ == "__main__":
    main()
