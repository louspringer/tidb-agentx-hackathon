#!/usr/bin/env python3
"""
Regenerate corrupted source files using AST projection system
"""

import os
import shutil

from src.model_driven_projection.final_projection_system import FinalProjectionSystem
from src.secure_shell_service.secure_executor import secure_execute


def regenerate_file(source_file: str, target_file: str) -> bool:
    """Regenerate a file using the AST projection system"""
    try:
        system = FinalProjectionSystem()

        # Generate the projected content
        projected_content = system.extract_and_project_file(source_file)

        if projected_content:
            # Create backup of original
            backup_file = f"{target_file}.backup"
            if os.path.exists(target_file):
                shutil.copy2(target_file, backup_file)
                print(f"📦 Created backup: {backup_file}")

            # Write the projected content
            with open(target_file, "w") as f:
                f.write(projected_content)

            print(f"✅ Regenerated: {target_file}")
            return True
        else:
            print(f"❌ Failed to regenerate: {target_file}")
            return False

    except Exception as e:
        print(f"❌ Error regenerating {target_file}: {e}")
        return False


def main():
    """Regenerate key corrupted files"""

    # Files to regenerate
    files_to_regenerate = [
        (
            "src/streamlit/openflow_quickstart_app.py",
            "src/streamlit/openflow_quickstart_app.py",
        ),
        (
            "src/security_first/input_validator.py",
            "src/security_first/input_validator.py",
        ),
        ("src/mdc_generator/mdc_model.py", "src/mdc_generator/mdc_model.py"),
    ]

    print("🚀 Regenerating corrupted files using AST projection system")
    print("=" * 60)

    success_count = 0
    for source_file, target_file in files_to_regenerate:
        if os.path.exists(source_file):
            if regenerate_file(source_file, target_file):
                success_count += 1
        else:
            print(f"⚠️  Source file not found: {source_file}")

    print(
        f"\n✅ Successfully regenerated {success_count}/{len(files_to_regenerate)} files",
    )

    # Test MyPy on the regenerated files
    print("\n🧪 Testing MyPy on regenerated files...")
    secure_execute("uv run mypy src/ --ignore-missing-imports")


if __name__ == "__main__":
    main()
