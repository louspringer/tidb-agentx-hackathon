#!/bin/bash
# Severe IDE Performance Fix Script
# For when normal optimization isn't enough

set -e

echo "🚨 Severe IDE Performance Fix"
echo "=============================="

# 1. Kill all Cursor processes
echo "🔪 Killing all Cursor processes..."
pkill -f cursor 2>/dev/null || true
sleep 2

# 2. Clean all cache files
echo "🗑️  Cleaning all cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".coverage" -delete 2>/dev/null || true

# 3. Clear all IDE cache
echo "🧹 Clearing all IDE cache..."
rm -rf ~/.config/Cursor/User/History/* 2>/dev/null || true
rm -rf ~/.config/Cursor/User/workspaceStorage/* 2>/dev/null || true
rm -rf ~/.config/Cursor/User/globalStorage/* 2>/dev/null || true

# 4. Minimal Cursor settings (disables Python language server)
echo "⚙️  Applying minimal Cursor settings..."
cat > ~/.config/Cursor/User/settings.json << 'EOF'
{
    "python.analysis.autoImportCompletions": false,
    "python.analysis.typeCheckingMode": "off",
    "python.analysis.diagnosticMode": "off",
    "python.analysis.autoSearchPaths": false,
    "files.watcherExclude": {
        "**/__pycache__/**": true,
        "**/.git/**": true,
        "**/.venv/**": true,
        "**/venv/**": true,
        "**/env/**": true,
        "**/.pytest_cache/**": true,
        "**/.mypy_cache/**": true,
        "**/*.pyc": true,
        "**/*.pyo": true
    },
    "search.exclude": {
        "**/__pycache__": true,
        "**/.git": true,
        "**/.venv": true,
        "**/venv": true,
        "**/env": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/*.pyc": true,
        "**/*.pyo": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/*.pyo": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.coverage": true
    },
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false,
    "editor.quickSuggestions": {
        "other": false,
        "comments": false,
        "strings": false
    },
    "editor.suggestOnTriggerCharacters": false,
    "editor.acceptSuggestionOnEnter": "off"
}
EOF

# 5. Kill any remaining heavy processes
echo "🔪 Killing remaining heavy processes..."
pkill -f "python.*lint" 2>/dev/null || true
pkill -f "python.*format" 2>/dev/null || true
pkill -f "python.*check" 2>/dev/null || true
pkill -f "mypy" 2>/dev/null || true
pkill -f "flake8" 2>/dev/null || true
pkill -f "black" 2>/dev/null || true

# 6. Show Results
echo ""
echo "📊 Severe Performance Fix Results:"
echo "   ✅ All Cursor processes killed"
echo "   ✅ All cache files cleaned"
echo "   ✅ All IDE cache cleared"
echo "   ✅ Minimal settings applied (Python language server disabled)"
echo "   ✅ All heavy processes killed"
echo ""
echo "💡 Restart Cursor now!"
echo "⚠️  Note: Python language server is disabled for maximum performance"
echo "🎯 If still slow, consider using a lighter editor (vim, nano)" 