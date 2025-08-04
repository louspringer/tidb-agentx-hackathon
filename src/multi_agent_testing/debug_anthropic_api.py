#!/usr/bin/env python3
"""
Debug Anthropic API Issues
"""

import os
import requests


def test_anthropic_api() -> None:
    """Test Anthropic API with different configurations"""

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found in environment")
        return

    print(f"🔑 API Key: {api_key[:10]}...{api_key[-10:]}")

    # Test different configurations
    configs = [
        {
            "name": "Current Config",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            "json": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Hello"}],
            },
        },
        {
            "name": "Updated API Version",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2024-01-01",
            },
            "json": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Hello"}],
            },
        },
        {
            "name": "Different Model",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            "json": {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Hello"}],
            },
        },
        {
            "name": "Simplified Request",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {"x-api-key": api_key, "Content-Type": "application/json"},
            "json": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Hello"}],
            },
        },
    ]

    for config in configs:
        print(f"\n🧪 Testing: {config['name']}")
        print(f"URL: {config['url']}")
        print(f"Headers: {config['headers']}")
        print(f"Model: {config['json']['model']}")

        try:
            response = requests.post(
                config["url"],
                headers=config["headers"],
                json=config["json"],
                timeout=30,
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Response: {result}")
            else:
                print(f"❌ Error: {response.text}")

        except Exception as e:
            print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_anthropic_api()
