
#!/usr/bin/env python3
"""
Regenerate all .mdc files using the Python model
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mdc_generator import MDCGenerator


    if invalid_files:
        print("\nInvalid files:")
        for file in invalid_files:
            print(f"  - {file}")
    else:
        print("\n✅ All .mdc files are valid!")


