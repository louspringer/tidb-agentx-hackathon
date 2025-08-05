#!/bin/bash
# Quick IDE Performance Fix Script
# Based on rules/ide_performance_optimization.md

set -e

echo "🚀 Quick IDE Performance Fix"
echo "=============================="

# 1. Clean Cache Files
echo "🗑️  Cleaning cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".coverage" -delete 2>/dev/null || true

# 2. Optimize Cursor Settings
echo "⚙️  Optimizing Cursor settings..."
cat > ~/.config/Cursor/User/settings.json << 'EOF'
{
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
    "python.analysis.exclude": [
        "**/__pycache__",
        "**/.venv",
        "**/venv",
        "**/env",
        "**/.pytest_cache",
        "**/.mypy_cache"
    ],
    "python.analysis.autoImportCompletions": false,
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoSearchPaths": false,
    "python.analysis.diagnosticMode": "workspace",
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false
}
EOF

# 3. Clear IDE History/Cache
echo "🧹 Clearing IDE history..."
rm -rf ~/.config/Cursor/User/History/* 2>/dev/null || true
rm -rf ~/.config/Cursor/User/workspaceStorage/* 2>/dev/null || true

# 4. Kill Heavy Background Processes
echo "🔪 Killing heavy background processes..."
pkill -f "python.*lint" 2>/dev/null || true
pkill -f "python.*format" 2>/dev/null || true
pkill -f "python.*check" 2>/dev/null || true

# 5. Show Results
echo ""
echo "📊 Performance Fix Results:"
echo "   ✅ Cache files cleaned"
echo "   ✅ Cursor settings optimized"
echo "   ✅ IDE history cleared"
echo "   ✅ Background processes killed"
echo ""
echo "💡 Restart Cursor for best results!"
echo "🎯 If still slow, run: ./fix_ide_performance_severe.sh" 