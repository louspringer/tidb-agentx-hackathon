#!/usr/bin/env python3
"""
Quick State Explorer
Explore the actual content of Ghostbusters state object
"""

import asyncio

from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters


async def explore_state() -> None:
    """Quick exploration of Ghostbusters state"""

    print("🔍 Running quick Ghostbusters to explore state...")

    try:
        # Run Ghostbusters
        state = await run_ghostbusters(".")

        print("\n🎯 STATE OBJECT EXPLORATION:")
        print(f"   Type: {type(state)}")
        print(
            f"   Attributes: {[attr for attr in dir(state) if not attr.startswith('_')]}",
        )

        print("\n📊 DETAILED ANALYSIS:")
        for attr in [attr for attr in dir(state) if not attr.startswith("_")]:
            value = getattr(state, attr)
            if hasattr(value, "__len__"):
                print(f"   {attr}: {len(value)} items")
                # Show first few items if it's a list
                if isinstance(value, list) and value:
                    print(f"      Sample: {value[0]}")
            else:
                print(f"   {attr}: {value}")

        print("\n🔍 SAMPLE DATA EXPLORATION:")

        # Explore delusions
        if hasattr(state, "delusions_detected") and state.delusions_detected:
            print(f"   First delusion: {state.delusions_detected[0]}")
            if len(state.delusions_detected) > 1:
                print(f"   Second delusion: {state.delusions_detected[1]}")

        # Explore recovery actions
        if hasattr(state, "recovery_actions") and state.recovery_actions:
            print(f"   First recovery action: {state.recovery_actions[0]}")
            if len(state.recovery_actions) > 1:
                print(f"   Second recovery action: {state.recovery_actions[1]}")

        # Explore validation results
        if hasattr(state, "validation_results"):
            if isinstance(state.validation_results, dict):
                print(
                    f"   Validation results keys: {list(state.validation_results.keys())}",
                )
                for key, value in list(state.validation_results.items())[:3]:
                    print(f"      {key}: {value}")
            else:
                print(f"   Validation results: {state.validation_results}")

        # Explore recovery results
        if hasattr(state, "recovery_results"):
            if isinstance(state.recovery_results, dict):
                print(
                    f"   Recovery results keys: {list(state.recovery_results.keys())}",
                )
                for key, value in list(state.recovery_results.items())[:3]:
                    print(f"      {key}: {value}")
            else:
                print(f"   Recovery results: {state.recovery_results}")

        # Explore metadata
        if hasattr(state, "metadata"):
            if isinstance(state.metadata, dict):
                print(f"   Metadata keys: {list(state.metadata.keys())}")
                for key, value in list(state.metadata.items())[:3]:
                    print(f"      {key}: {value}")
            else:
                print(f"   Metadata: {state.metadata}")

        print("\n🎯 BATTLE READINESS SUMMARY:")
        print(f"   Confidence: {state.confidence_score}")
        print(f"   Delusions: {len(state.delusions_detected):,}")
        print(f"   Recovery Actions: {len(state.recovery_actions):,}")
        print(f"   Phase: {state.current_phase}")
        print(f"   Errors: {len(state.errors)}")
        print(f"   Warnings: {len(state.warnings)}")

    except Exception as e:
        print(f"💥 Error exploring state: {e}")


if __name__ == "__main__":
    asyncio.run(explore_state())
