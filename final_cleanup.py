#!/usr/bin/env python3
"""
Final cleanup script to remove remaining temporary files and directories.
"""

import os
import shutil
from typing import List


def get_files_to_remove() -> List[str]:
    """Get list of files to remove."""
    return [
        # Log files
        "final_test_fix.log",
        "ghostbusters_profile.prof",
        "ghostbusters_test_results.log",
        "pr_creation.log",
        "quality_enforcement_test.log",
        "targeted_test_fix.log",
        "test_all_fix.log",
        "test_results_final.log",
        "test_results.log",
        "test_results_main.log",
        "test_results_updated.log",
        # Temporary files
        "organize_root_files.py",
        # Temporary directories
        "context_aware_projected_artifacts",
        "__pycache__",
    ]


def cleanup_files() -> None:
    """Remove temporary files and directories."""

    files_to_remove = get_files_to_remove()

    print("🧹 Final cleanup of temporary files...")
    print(f"📋 Found {len(files_to_remove)} items to remove")

    removed_count = 0
    for item in files_to_remove:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"🗑️  Removed directory: {item}")
                else:
                    os.remove(item)
                    print(f"🗑️  Removed file: {item}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {item}: {e}")
        else:
            print(f"⚠️  {item} not found, skipping")

    print(f"\n✅ Cleanup complete! Removed {removed_count} items")


def main() -> None:
    """Main cleanup function."""

    # Show what will be removed
    files_to_remove = get_files_to_remove()
    print("📋 Files and directories to remove:")
    for item in files_to_remove:
        if os.path.exists(item):
            size = os.path.getsize(item) if os.path.isfile(item) else "DIR"
            print(f"  📁 {item} ({size})")
        else:
            print(f"  ⚠️  {item} (not found)")

    # Confirm before proceeding
    response = input("\nProceed with cleanup? (y/N): ")
    if response.lower() != "y":
        print("Cleanup cancelled.")
        return

    # Perform cleanup
    cleanup_files()


if __name__ == "__main__":
    main()
