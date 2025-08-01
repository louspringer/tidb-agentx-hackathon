#!/usr/bin/env python3
"""
Regenerate all .mdc files using the Python model
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mdc_generator import MDCGenerator

def main():
    """Regenerate all .mdc files"""
    base_dir = Path(__file__).parent.parent
    generator = MDCGenerator(base_dir)
    
    print("Regenerating all .mdc files...")
    generator.generate_all_rules()
    
    print("\nValidating all .mdc files...")
    results = generator.validate_all_mdc_files()
    
    valid_files = [f for f, valid in results.items() if valid]
    invalid_files = [f for f, valid in results.items() if not valid]
    
    print(f"\nResults:")
    print(f"  Valid files: {len(valid_files)}")
    print(f"  Invalid files: {len(invalid_files)}")
    
    if invalid_files:
        print("\nInvalid files:")
        for file in invalid_files:
            print(f"  - {file}")
    else:
        print("\n✅ All .mdc files are valid!")

if __name__ == "__main__":
    main() 