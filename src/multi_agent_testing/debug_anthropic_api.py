#!/usr/bin/env python3
"""
Debug Anthropic API Issues
"""

import os

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found in environment")
        return

    # Test different configurations
    configs = [
        {
            "name": "Current Config",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "x-api-key": api_key,
                "Content-Type": "application/json",

            },
            "json": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 100,

        },
        {
            "name": "Updated API Version",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "x-api-key": api_key,
                "Content-Type": "application/json",

            },
            "json": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 100,

        },
        {
            "name": "Different Model",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "x-api-key": api_key,
                "Content-Type": "application/json",

            },
            "json": {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 100,

        },
        {
            "name": "Simplified Request",
            "url": "https://api.anthropic.com/v1/messages",

    for config in configs:
        print(f"\n🧪 Testing: {config['name']}")
        print(f"URL: {config['url']}")
        print(f"Headers: {config['headers']}")
        print(f"Model: {config['json']['model']}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Response: {result}")
            else:
                print(f"❌ Error: {response.text}")

