# IDE Performance Optimization Rule

## Core Principle
**When IDE performance issues are reported, immediately apply systematic performance optimization before attempting other solutions.**

## Performance Issues Detection

### Symptoms to Watch For:
- **Keystroke lag**: Delayed response to typing
- **File switching slowness**: Slow tab switching or file opening
- **Search sluggishness**: Slow file search or find-in-files
- **Auto-completion delays**: Slow or missing code completion
- **High memory usage**: IDE using excessive RAM
- **Background process overload**: Too many background processes

### Quick Diagnosis Commands:
```bash
# Check IDE memory usage
ps aux | grep -E "(cursor|code|sublime|vim)" | head -10

# Check system resources
free -h && df -h /home/$USER

# Count project files (if >10,000, performance issues likely)
find . -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.json" | wc -l

# Check for cache directories
find . -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" | wc -l
```

## Immediate Performance Fixes (5-Minute Procedure)

### 1. Clean Cache Files
```bash
# Remove Python cache directories
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# Remove other cache directories
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".coverage" -delete
```

### 2. Optimize Cursor Settings
```bash
# Create optimized settings
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
```

### 3. Clear IDE History/Cache
```bash
# Clear Cursor history
rm -rf ~/.config/Cursor/User/History/*

# Clear workspace storage
rm -rf ~/.config/Cursor/User/workspaceStorage/*
```

### 4. Kill Heavy Background Processes
```bash
# Kill language servers and formatters
pkill -f "python.*lint" 2>/dev/null
pkill -f "python.*format" 2>/dev/null
pkill -f "python.*check" 2>/dev/null
```

### 5. For Severe Performance Issues
```bash
# Disable Python language server completely
cat > ~/.config/Cursor/User/settings.json << 'EOF'
{
    "python.analysis.autoImportCompletions": false,
    "python.analysis.typeCheckingMode": "off",
    "python.analysis.diagnosticMode": "off",
    "python.analysis.autoSearchPaths": false,
    "files.watcherExclude": {
        "**/__pycache__/**": true,
        "**/.git/**": true,
        "**/.venv/**": true
    },
    "search.exclude": {
        "**/__pycache__": true,
        "**/.git": true,
        "**/.venv": true
    },
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false
}
EOF
```

## Performance Monitoring

### Before/After Metrics:
- **Memory usage**: Check `ps aux | grep cursor`
- **File count**: `find . -name "*.py" | wc -l`
- **Cache directories**: `find . -name "__pycache__" | wc -l`
- **Disk space freed**: `du -sh .` before/after

### Success Indicators:
- **Typing responsiveness**: No lag on keystrokes
- **File search speed**: Quick file finding
- **Memory usage**: IDE using <1GB RAM
- **Background processes**: <10 Cursor processes

## Prevention Strategies

### 1. Add to .gitignore
```bash
# Ensure cache files are ignored
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".pytest_cache/" >> .gitignore
echo ".mypy_cache/" >> .gitignore
echo ".coverage" >> .gitignore
```

### 2. Regular Maintenance
```bash
# Weekly cache cleanup script
#!/bin/bash
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
echo "Cache cleanup completed"
```

### 3. Project Size Management
- **Monitor file count**: Keep under 10,000 files if possible
- **Use .gitignore**: Prevent cache accumulation
- **Modular structure**: Break large projects into smaller modules

## Emergency Procedures

### If IDE Becomes Unresponsive:
1. **Kill all Cursor processes**: `pkill -f cursor`
2. **Clear all cache**: Run cache cleanup script
3. **Reset settings**: Use minimal settings configuration
4. **Restart IDE**: Fresh start with optimized settings

### If Performance Issues Persist:
1. **Check system resources**: `htop` or `top`
2. **Monitor disk I/O**: `iotop`
3. **Check for other heavy processes**: `ps aux --sort=-%mem`
4. **Consider lighter editor**: Vim, Nano, or minimal VS Code

## Rule Application

### When to Apply This Rule:
- **User reports IDE sluggishness**
- **Keystroke lag complaints**
- **File search performance issues**
- **High memory usage warnings**
- **Background process overload**

### Rule Priority:
1. **Immediate**: Apply cache cleanup and settings optimization
2. **Short-term**: Monitor performance and adjust settings
3. **Long-term**: Implement prevention strategies

## Remember
**Performance optimization is always faster than debugging complex issues. Apply these fixes first, then investigate if problems persist.** 