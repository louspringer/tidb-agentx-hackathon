#!/bin/bash

# Live Smoke Test with Direct 1Password Integration
# Uses specific item IDs we found in your 1Password vault

echo "🔐 LIVE SMOKE TEST WITH DIRECT 1PASSWORD"
echo "========================================="

# Check if 1Password CLI is available
if ! command -v op &> /dev/null; then
    echo "❌ 1Password CLI not found. Please install it first:"
    echo "   https://1password.com/downloads/command-line/"
    exit 1
fi

# Check if user is signed in to 1Password
if ! op account list &> /dev/null; then
    echo "❌ Not signed in to 1Password CLI"
    echo "Please run: op signin"
    exit 1
fi

echo "✅ 1Password CLI available and signed in"

# Try to get Anthropic API key from the specific item we found
echo ""
echo "🔑 Getting Anthropic API key from 'Anthropic Cursor AI'..."
ANTHROPIC_API_KEY=$(op item get "Anthropic Cursor AI" --fields credential --reveal 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ Found Anthropic API key in 1Password"
    export ANTHROPIC_API_KEY
else
    echo "❌ Could not get Anthropic API key"
    ANTHROPIC_API_KEY=""
fi

# Try to get OpenAI API key - let's check if there's a more specific item
echo ""
echo "🔑 Looking for OpenAI API key..."
OPENAI_API_KEY=""

# Try a few common patterns
for item_name in "OpenAI API Key" "OpenAI" "GPT API Key"; do
    echo "  Trying: $item_name"
    credential=$(op item get "$item_name" --fields credential --reveal 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$credential" ]; then
        echo "  ✅ Found OpenAI API key in '$item_name'"
        OPENAI_API_KEY="$credential"
        export OPENAI_API_KEY
        break
    fi
done

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Could not find OpenAI API key"
fi

# Check if we have any credentials
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "❌ No API credentials found in 1Password"
    echo ""
    echo "Found items in your vault:"
    echo "  - Anthropic Cursor AI (API credential)"
    echo "  - Openai (login item)"
    echo "  - Claude (login item)"
    echo ""
    echo "To add API keys to 1Password:"
    echo "  op item create --category=api-credential --title='OpenAI API Key'"
    exit 1
fi

echo ""
echo "🎯 Credentials Status:"
echo "   OpenAI API Key: ${OPENAI_API_KEY:+✅ SET}"
echo "   Anthropic API Key: ${ANTHROPIC_API_KEY:+✅ SET}"

echo ""
echo "🧪 Running live smoke test with 1Password credentials..."
echo ""

# Run the live smoke test
python live_smoke_test.py

echo ""
echo "📊 Test completed!"
echo ""
echo "💡 If you want to add more API keys:"
echo "  1. Create them in 1Password as API Credentials"
echo "  2. Use descriptive names like 'OpenAI API Key'"
echo "  3. Put the key in the 'credential' field" 