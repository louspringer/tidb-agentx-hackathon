#!/usr/bin/env python3
"""
Create Ghostbusters Battle Analysis Notebook
Using nbformat to create a proper Jupyter notebook
"""

import nbformat as nbf


def create_ghostbusters_notebook() -> None:
    """Create a Jupyter notebook for Ghostbusters battle analysis"""

    # Create a new notebook
    nb = nbf.v4.new_notebook()

    # Add title cell
    title_cell = nbf.v4.new_markdown_cell(
        """# 🎯 Ghostbusters Battle Analysis Notebook

Exploring all the interesting data in the Ghostbusters state!""",
    )

    # Add imports cell
    imports_cell = nbf.v4.new_code_cell(
        """import asyncio
import json
from dataclasses import asdict
from typing import Any, Dict

# Import Ghostbusters
from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters""",
    )

    # Add running analysis cell
    run_cell = nbf.v4.new_markdown_cell("""## 🔍 Running Ghostbusters Analysis""")

    # Add analysis code cell
    analysis_cell = nbf.v4.new_code_cell(
        """# Run Ghostbusters and get the state
print("🚀 Running Ghostbusters analysis...")
state = await run_ghostbusters(".")
print(f"✅ Ghostbusters completed with confidence: {state.confidence_score}")""",
    )

    # Add state structure cell
    structure_cell = nbf.v4.new_markdown_cell("""## 📊 State Structure Analysis""")

    # Add structure analysis code
    structure_code = nbf.v4.new_code_cell(
        """# Explore the state structure
print("🎯 GHOSTBUSTERS STATE STRUCTURE:")
print(f"   Type: {type(state)}")
print(f"   Attributes: {dir(state)}")
print()

# Show all state attributes
for attr in dir(state):
    if not attr.startswith('_'):
        value = getattr(state, attr)
        if hasattr(value, '__len__'):
            print(f"   {attr}: {len(value)} items")
        else:
            print(f"   {attr}: {value}")""",
    )

    # Add delusions analysis cell
    delusions_cell = nbf.v4.new_markdown_cell("""## 👻 Delusions Analysis""")

    # Add delusions code
    delusions_code = nbf.v4.new_code_cell(
        """# Analyze delusions detected
print(f"👻 TOTAL DELUSIONS DETECTED: {len(state.delusions_detected):,}")
print()

# Show first few delusions
if state.delusions_detected:
    print("📋 SAMPLE DELUSIONS:")
    for i, delusion in enumerate(state.delusions_detected[:5]):
        print(f"   {i+1}. {delusion}")

    # Analyze delusion types
    delusion_types = {}
    for delusion in state.delusions_detected:
        if isinstance(delusion, dict):
            delusion_type = delusion.get('type', 'unknown')
            delusion_types[delusion_type] = delusion_types.get(delusion_type, 0) + 1

    print(f"\\n📊 DELUSION TYPES:")
    for delusion_type, count in delusion_types.items():
        print(f"   {delusion_type}: {count:,}")""",
    )

    # Add recovery actions cell
    recovery_cell = nbf.v4.new_markdown_cell("""## 🔧 Recovery Actions Analysis""")

    # Add recovery code
    recovery_code = nbf.v4.new_code_cell(
        """# Analyze recovery actions
print(f"🔧 TOTAL RECOVERY ACTIONS: {len(state.recovery_actions):,}")
print()

# Show first few recovery actions
if state.recovery_actions:
    print("📋 SAMPLE RECOVERY ACTIONS:")
    for i, action in enumerate(state.recovery_actions[:5]):
        print(f"   {i+1}. {action}")

    # Analyze recovery action types
    action_types = {}
    for action in state.recovery_actions:
        if isinstance(action, dict):
            action_type = action.get('engine', 'unknown')
            action_types[action_type] = action_types.get(action_type, 0) + 1

    print(f"\\n📊 RECOVERY ACTION TYPES:")
    for action_type, count in action_types.items():
        print(f"   {action_type}: {count:,}")""",
    )

    # Add validation results cell
    validation_cell = nbf.v4.new_markdown_cell("""## 📈 Validation Results Analysis""")

    # Add validation code
    validation_code = nbf.v4.new_code_cell(
        """# Analyze validation results
print("📈 VALIDATION RESULTS:")
print(f"   Type: {type(state.validation_results)}")
print(f"   Keys: {list(state.validation_results.keys()) if isinstance(state.validation_results, dict) else 'Not a dict'}")
print()

if isinstance(state.validation_results, dict):
    for key, value in state.validation_results.items():
        print(f"   {key}: {value}")""",
    )

    # Add recovery results cell
    recovery_results_cell = nbf.v4.new_markdown_cell(
        """## 🚀 Recovery Results Analysis""",
    )

    # Add recovery results code
    recovery_results_code = nbf.v4.new_code_cell(
        """# Analyze recovery results
print("🚀 RECOVERY RESULTS:")
print(f"   Type: {type(state.recovery_results)}")
print(f"   Keys: {list(state.recovery_results.keys()) if isinstance(state.recovery_results, dict) else 'Not a dict'}")
print()

if isinstance(state.recovery_results, dict):
    for key, value in state.recovery_results.items():
        print(f"   {key}: {value}")""",
    )

    # Add metadata cell
    metadata_cell = nbf.v4.new_markdown_cell("""## 📊 Metadata Analysis""")

    # Add metadata code
    metadata_code = nbf.v4.new_code_cell(
        """# Analyze metadata
print("📊 METADATA:")
print(f"   Type: {type(state.metadata)}")
print(f"   Keys: {list(state.metadata.keys()) if isinstance(state.metadata, dict) else 'Not a dict'}")
print()

if isinstance(state.metadata, dict):
    for key, value in state.metadata.items():
        print(f"   {key}: {value}")""",
    )

    # Add battle readiness cell
    battle_cell = nbf.v4.new_markdown_cell("""## 🎯 Battle Readiness Summary""")

    # Add battle code
    battle_code = nbf.v4.new_code_cell(
        """# Create battle readiness summary
print("🎯" + "="*60 + "🎯")
print("           GHOSTBUSTERS BATTLE READINESS SUMMARY")
print("🎯" + "="*60 + "🎯")
print()
print(f"🎯 Confidence Score: {state.confidence_score:.2f}")
print(f"👻 Delusions Detected: {len(state.delusions_detected):,}")
print(f"🔧 Recovery Actions: {len(state.recovery_actions):,}")
print(f"📊 Current Phase: {state.current_phase}")
print(f"❌ Errors: {len(state.errors)}")
print(f"⚠️  Warnings: {len(state.warnings)}")
print()
print("🎯 BATTLE ASSESSMENT:")
if len(state.delusions_detected) > 0:
    print("   ✅ MASSIVE DETECTION CAPACITY")
if len(state.recovery_actions) > 0:
    print("   ✅ COMPREHENSIVE RECOVERY PLANNING")
if len(state.errors) == 0:
    print("   ✅ CLEAN OPERATION")
if len(state.warnings) == 0:
    print("   ✅ ZERO WARNINGS")
print("   ✅ READY FOR HACKATHON COMBAT!")
print()
print("🎯" + "="*60 + "🎯")""",
    )

    # Add deep dive cell
    deep_dive_cell = nbf.v4.new_markdown_cell(
        """## 🔍 Deep Dive: State Object Exploration""",
    )

    # Add deep dive code
    deep_dive_code = nbf.v4.new_code_cell(
        """# Deep dive into state object
print("🔍 DEEP DIVE INTO STATE OBJECT:")
print()

# Convert state to dict for easier exploration
try:
    state_dict = asdict(state)
    print("✅ State converted to dictionary successfully")
    print(f"   Keys: {list(state_dict.keys())}")

    # Show detailed breakdown
    for key, value in state_dict.items():
        if isinstance(value, (list, dict)):
            print(f"   {key}: {len(value)} items")
        else:
            print(f"   {key}: {value}")

except Exception as e:
    print(f"❌ Could not convert state to dict: {e}")
    print("   State object structure:")
    for attr in dir(state):
        if not attr.startswith('_'):
            try:
                value = getattr(state, attr)
                print(f"   {attr}: {type(value)}")
            except Exception as e:
                print(f"   {attr}: Error accessing - {e}")""",
    )

    # Add all cells to notebook
    nb.cells = [
        title_cell,
        imports_cell,
        run_cell,
        analysis_cell,
        structure_cell,
        structure_code,
        delusions_cell,
        delusions_code,
        recovery_cell,
        recovery_code,
        validation_cell,
        validation_code,
        recovery_results_cell,
        recovery_results_code,
        metadata_cell,
        metadata_code,
        battle_cell,
        battle_code,
        deep_dive_cell,
        deep_dive_code,
    ]

    # Write the notebook
    nbf.write(nb, "ghostbusters_battle_analysis.ipynb")

    print("✅ Created ghostbusters_battle_analysis.ipynb")
    print(
        "🎯 You can now open this notebook in Jupyter to explore the Ghostbusters state!",
    )


if __name__ == "__main__":
    create_ghostbusters_notebook()
