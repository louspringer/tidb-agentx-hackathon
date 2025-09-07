"""Simple test for the Ghostbusters system."""

import asyncio
from pathlib import Path

from src.ghostbusters import GhostbustersOrchestrator


async def test_ghostbusters_basic() -> bool:
    """Test basic Ghostbusters functionality."""
    # Create a simple test project
    test_dir = Path("test_project")
    test_dir.mkdir(exist_ok=True)

    # Create a test file
    test_file = test_dir / "test.py"
    test_file.write_text("def hello():\n    print('Hello, World!')\n")

    try:
        # Run Ghostbusters
        orchestrator = GhostbustersOrchestrator(str(test_dir))
        state = await orchestrator.run_ghostbusters()

        # Check results
        print("✅ Ghostbusters completed successfully!")
        print(f"   Confidence: {state.confidence_score}")
        print(f"   Delusions detected: {len(state.delusions)}")
        print(
            f"   Issues fixed: {len([r for r in state.recovery_results if r.get('success')])}",
        )

        if state.errors:
            print(f"   Errors: {state.errors}")

        return True

    except Exception as e:
        print(f"❌ Ghostbusters test failed: {e}")
        return False
    finally:
        # Cleanup
        import shutil

        if test_dir.exists():
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    success = asyncio.run(test_ghostbusters_basic())
    exit(0 if success else 1)
