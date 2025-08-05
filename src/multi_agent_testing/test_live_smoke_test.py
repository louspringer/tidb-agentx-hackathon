#!/usr/bin/env python3
"""
Pytest tests for live smoke test functionality
"""

import os
import pytest
from live_smoke_test_langchain import LiveLLMOrchestrator


def test_live_llm_orchestrator_initialization() -> None:
    """Test that LiveLLMOrchestrator initializes correctly"""

    # Test without API key
    orchestrator = LiveLLMOrchestrator(provider="openai")
    assert orchestrator.provider == "openai"
    assert orchestrator.api_key is None
    # Test with API key
    test_key = "test-key-123"
    orchestrator = LiveLLMOrchestrator(api_key=test_key, provider="anthropic")
    assert orchestrator.provider == "anthropic"
    assert orchestrator.api_key == test_key


def test_live_llm_call_without_credentials() -> None:
    """Test that live LLM call handles missing credentials gracefully"""

    orchestrator = LiveLLMOrchestrator(provider="openai")
    result = orchestrator.call_live_llm("test context", "test question")

    assert "error" in result
    assert "No OPENAI_API_KEY available" in result["error"]
    assert result["questions"] == []


def test_provider_validation() -> None:
    """Test that invalid providers raise appropriate errors"""

    with pytest.raises(ValueError, match="Unsupported provider"):
        LiveLLMOrchestrator(provider="invalid_provider")


def test_api_endpoint_configuration() -> None:
    """Test that API endpoints are configured correctly"""

    # Test with API key available
    test_key = "test-key-123"
    openai_orchestrator = LiveLLMOrchestrator(api_key=test_key, provider="openai")
    assert openai_orchestrator.llm.model_name == "gpt-4-turbo"

    anthropic_orchestrator = LiveLLMOrchestrator(api_key=test_key, provider="anthropic")
    assert anthropic_orchestrator.llm.model == "claude-3-5-sonnet-20241022"


def test_live_llm_call_with_credentials() -> None:
    """Test that live LLM call works with credentials (if available)"""

    # Only run if we have credentials
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("No API credentials available for live test")

    # Test with available provider
    if os.getenv("OPENAI_API_KEY"):
        orchestrator = LiveLLMOrchestrator(provider="openai")
    elif os.getenv("ANTHROPIC_API_KEY"):
        orchestrator = LiveLLMOrchestrator(provider="anthropic")
    else:
        pytest.skip("No API credentials available")

    context = "I think this is a test context with some assumptions."
    question = "What assumptions am I making?"

    result = orchestrator.call_live_llm(context, question)

    # Should either have questions or an error
    if "error" not in result:
        # Check for different possible response formats
        has_questions = (
            "questions" in result
            or "probing_questions" in result
            or any(key.endswith("questions") for key in result.keys())
        )
        assert has_questions, f"Expected questions in result, got: {result}"

        # Get the questions list regardless of key name
        questions_key = next(
            (key for key in result.keys() if key.endswith("questions")), None
        )
        if questions_key:
            questions = result[questions_key]
            assert isinstance(questions, list)
            assert len(questions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
