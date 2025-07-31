#!/usr/bin/env python3
"""
Pytest tests for live smoke test functionality
"""

import os
import pytest
from live_smoke_test import LiveLLMOrchestrator

def test_live_llm_orchestrator_initialization():
    """Test that LiveLLMOrchestrator initializes correctly"""
    
    # Test without API key
    orchestrator = LiveLLMOrchestrator(provider="openai")
    assert orchestrator.provider == "openai"
    assert orchestrator.api_key is None
    assert orchestrator.base_url == "https://api.openai.com/v1/chat/completions"
    assert orchestrator.model == "gpt-4-turbo"
    
    # Test with API key
    test_key = "test-key-123"
    orchestrator = LiveLLMOrchestrator(api_key=test_key, provider="anthropic")
    assert orchestrator.provider == "anthropic"
    assert orchestrator.api_key == test_key
    assert orchestrator.base_url == "https://api.anthropic.com/v1/messages"
    assert orchestrator.model == "claude-3-sonnet-20240229"

def test_live_llm_call_without_credentials():
    """Test that live LLM call handles missing credentials gracefully"""
    
    orchestrator = LiveLLMOrchestrator(provider="openai")
    result = orchestrator.call_live_llm("test context", "test question")
    
    assert "error" in result
    assert "No OPENAI_API_KEY available" in result["error"]
    assert result["questions"] == []

def test_provider_validation():
    """Test that invalid providers raise appropriate errors"""
    
    with pytest.raises(ValueError, match="Unsupported provider"):
        LiveLLMOrchestrator(provider="invalid_provider")

def test_api_endpoint_configuration():
    """Test that API endpoints are configured correctly"""
    
    openai_orchestrator = LiveLLMOrchestrator(provider="openai")
    assert openai_orchestrator.base_url == "https://api.openai.com/v1/chat/completions"
    assert openai_orchestrator.model == "gpt-4-turbo"
    
    anthropic_orchestrator = LiveLLMOrchestrator(provider="anthropic")
    assert anthropic_orchestrator.base_url == "https://api.anthropic.com/v1/messages"
    assert anthropic_orchestrator.model == "claude-3-sonnet-20240229"

def test_live_llm_call_with_credentials():
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
        assert "questions" in result
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 