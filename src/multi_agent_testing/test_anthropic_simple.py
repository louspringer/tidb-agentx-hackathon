#!/usr/bin/env python3
"""
Simple test to replicate the smoke test Anthropic API call
"""

import os
import json
import requests

def test_anthropic_smoke_test():
    """Test the exact same request as the smoke test"""
    
    # Get API key from 1Password using environment variable or secure method
    # DEMO ONLY: This uses environment variables for demonstration purposes
    # In production, consider using 1Password SDK or secure credential management
    # For healthcare compliance, implement proper credential rotation and audit trails
    # Allow for mocking in test environments
    api_key = os.getenv('ANTHROPIC_API_KEY')
    mock_api_key = os.getenv('MOCK_ANTHROPIC_API_KEY')
    if mock_api_key:
        print("⚠️ Using MOCK_ANTHROPIC_API_KEY for testing purposes.")
        api_key = mock_api_key
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("💡 Consider using 1Password CLI or SDK instead of subprocess")
        return
    # Validate API key format (example: Anthropic keys often start with 'sk-' and are 40+ chars)
    if not re.match(r'^sk-[A-Za-z0-9]{32,}$', api_key):
        print("❌ API key format invalid. Please check your key.")
        return
    print(f"🔑 API Key: [REDACTED] (length: {len(api_key)})")
    
    # Replicate the exact smoke test request
    prompt = """
You are a partner LLM helping to detect blind spots and unknown unknowns.

Context: I'm implementing OAuth2 for our healthcare application.
I assume using the standard library will be secure enough.
Probably I don't need to worry about token refresh.
Obviously the Snowflake integration will handle the rest.

Jeopardy Question: What assumptions am I making about OAuth2 security and token management?

Generate 5 probing questions that would reveal blind spots, assumptions, or unknown unknowns. 
Focus on questions that challenge the approach and reveal what might be missing.

Format as JSON:
{
    "questions": ["question1", "question2", ...],
    "confidence": 0.0-1.0,
    "blind_spots": ["blind_spot1", "blind_spot2", ...],
    "recommendation": "ASK_HUMAN|INVESTIGATE|PROCEED"
}
"""
    
    print(f"\n🧪 Testing exact smoke test request...")
    print(f"URL: https://api.anthropic.com/v1/messages")
    print(f"Model: claude-3-5-sonnet-20241022")
    print(f"Prompt length: {len(prompt)} characters")
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["content"][0]["text"]
            print(f"✅ Success! Content length: {len(content)}")
            print(f"Content preview: {content[:200]}...")
            
            # Try to parse JSON
            try:
                parsed = json.loads(content)
                print(f"✅ JSON parsed successfully!")
                print(f"Questions: {len(parsed.get('questions', []))}")
                print(f"Confidence: {parsed.get('confidence', 'N/A')}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print(f"Raw content: {content}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_anthropic_smoke_test() 