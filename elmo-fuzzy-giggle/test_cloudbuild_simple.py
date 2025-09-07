"""Simple test to verify Cloud Build dependencies."""

import sys


def test_imports() -> bool:
    """Test that all required dependencies can be imported."""
    try:
        import langchain  # noqa: F401

        print("✅ langchain imported successfully")
    except ImportError as e:
        print(f"❌ langchain import failed: {e}")
        return False

    try:
        import langgraph  # noqa: F401

        print("✅ langgraph imported successfully")
    except ImportError as e:
        print(f"❌ langgraph import failed: {e}")
        return False

    try:
        import pydantic  # noqa: F401

        print("✅ pydantic imported successfully")
    except ImportError as e:
        print(f"❌ pydantic import failed: {e}")
        return False

    try:
        import aiofiles  # noqa: F401

        print("✅ aiofiles imported successfully")
    except ImportError as e:
        print(f"❌ aiofiles import failed: {e}")
        return False

    print("✅ All dependencies imported successfully!")
    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
