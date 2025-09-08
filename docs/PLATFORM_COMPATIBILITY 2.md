# Platform Compatibility Guide

## 🎯 **Snowflake Workspace Compatibility**

This document outlines the platform compatibility of our `make install` targets for deployment in Snowflake workspaces and other environments.

## 📋 **Platform Support Matrix**

| Platform | Package Manager | Go Support | Shell Support | Python Support | Status |
|----------|----------------|------------|---------------|----------------|---------|
| **Linux** | `apt-get` | ✅ Full | ✅ Full | ✅ Full | ✅ Tested |
| **macOS** | `brew` | ✅ Full | ✅ Full | ✅ Full | ✅ Tested |
| **Windows (Git Bash)** | `chocolatey` | ✅ Full | ⚠️ Limited | ✅ Full | ⚠️ Partial |
| **Windows (MSYS2)** | `pacman` | ✅ Full | ⚠️ Limited | ✅ Full | ⚠️ Partial |
| **Snowflake Workspace** | `apt-get` | ✅ Full | ✅ Full | ✅ Full | ✅ Compatible |

## 🔧 **Platform Detection**

The Makefile automatically detects your platform and selects the appropriate package manager:

```bash
# Platform detection
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
PLATFORM := $(shell echo $(UNAME_S) | tr '[:upper:]' '[:lower:]')
ARCH := $(shell echo $(UNAME_M) | tr '[:upper:]' '[:lower:]')
```

### **Supported Platforms:**

#### **Linux (Ubuntu/Debian)**
- **Package Manager**: `apt-get`
- **Go Installation**: Direct download from golang.org
- **Shell Tools**: `shellcheck`, `protobuf-compiler`
- **Status**: ✅ Fully supported

#### **macOS**
- **Package Manager**: `brew`
- **Go Installation**: `brew install go`
- **Shell Tools**: `brew install shellcheck`, `brew install protobuf`
- **Status**: ✅ Fully supported

#### **Windows (Git Bash)**
- **Package Manager**: `chocolatey`
- **Go Installation**: `choco install golang`
- **Shell Tools**: `choco install shellcheck`, `choco install protobuf`
- **Status**: ⚠️ Limited shell support

#### **Windows (MSYS2)**
- **Package Manager**: `pacman`
- **Go Installation**: `pacman -S go`
- **Shell Tools**: `pacman -S shellcheck`, `pacman -S protobuf`
- **Status**: ⚠️ Limited shell support

## 🚀 **Installation Targets by Platform**

### **✅ Platform-Agnostic Targets**
These work identically across all platforms:

```bash
make install-python        # Uses UV (cross-platform)
make install-security      # Uses UV (cross-platform)
make install-streamlit     # Uses UV (cross-platform)
make install-healthcare    # Uses UV (cross-platform)
```

### **⚠️ Platform-Specific Targets**
These adapt to the detected platform:

```bash
make install-bash          # shellcheck via platform package manager
make install-cloudformation # cfn-lint via platform package manager
make install-docs          # markdownlint via npm (cross-platform)
make install-go            # Go via platform package manager
make install-secure-shell  # protobuf via platform package manager
```

## 🛠️ **Snowflake Workspace Compatibility**

### **✅ Compatible Components**

#### **Python Dependencies**
- **UV Package Manager**: Cross-platform, works in Snowflake
- **Python Tools**: All Python-based tools work identically
- **Virtual Environments**: UV handles isolation properly

#### **Go Components**
- **Go Installation**: Automatic platform detection
- **Protobuf Tools**: Platform-specific installation
- **Secure Shell Service**: Full compatibility

#### **Development Tools**
- **Linting**: `flake8`, `black`, `mypy` (Python-based)
- **Testing**: `pytest` (Python-based)
- **Security**: `bandit`, `safety` (Python-based)

### **⚠️ Potential Issues**

#### **Shell Script Dependencies**
- **Issue**: `shellcheck` may not be available in all environments
- **Solution**: Falls back to Python-based linting
- **Workaround**: Use `make lint-python` instead of `make lint-bash`

#### **System Package Managers**
- **Issue**: `sudo` may not be available in containerized environments
- **Solution**: Pre-install system packages in container
- **Workaround**: Use Python-based alternatives

#### **File System Permissions**
- **Issue**: `/usr/local` may not be writable
- **Solution**: Install Go to user directory
- **Workaround**: Use `GOPATH` environment variable

## 🔍 **Testing Platform Compatibility**

### **Check Platform Detection**
```bash
make help
# Shows: Platform: linux-x86_64, Package Manager: apt-get
```

### **Test Installation**
```bash
# Test platform-specific installation
make install-bash
make install-go

# Test platform-agnostic installation
make install-python
make install-security
```

### **Verify Dependencies**
```bash
# Check if all tools are available
make check-deps
```

## 📊 **Platform-Specific Commands**

### **Linux (Ubuntu/Debian)**
```bash
# System packages
sudo apt-get install -y shellcheck protobuf-compiler

# Go installation
curl -OL https://go.dev/dl/go1.21.6.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz
```

### **macOS**
```bash
# System packages
brew install shellcheck protobuf go

# No additional steps needed
```

### **Windows (Git Bash)**
```bash
# System packages
choco install shellcheck protobuf golang

# May need to restart shell for PATH updates
```

### **Windows (MSYS2)**
```bash
# System packages
pacman -S shellcheck protobuf go

# No additional steps needed
```

## 🎯 **Snowflake Workspace Recommendations**

### **Pre-Installation Checklist**
1. **Verify Platform**: Run `make help` to confirm platform detection
2. **Check Permissions**: Ensure write access to installation directories
3. **Network Access**: Verify internet access for package downloads
4. **Python Environment**: Ensure Python 3.8+ is available

### **Installation Strategy**
```bash
# 1. Install platform-agnostic dependencies first
make install-python
make install-security

# 2. Install platform-specific dependencies
make install-bash
make install-go

# 3. Install domain-specific dependencies
make install-secure-shell
make install-cloudformation
```

### **Troubleshooting**
```bash
# Check platform detection
make help

# Test individual components
make test-python
make test-go

# Verify all dependencies
make check-deps
```

## 🔄 **Continuous Integration**

### **Multi-Platform Testing**
```yaml
# GitHub Actions example
jobs:
  test-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: make install-all
      - run: make test-all

  test-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - run: make install-all
      - run: make test-all

  test-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - run: make install-all
      - run: make test-all
```

## 📈 **Performance Considerations**

### **Platform-Specific Optimizations**

#### **Linux**
- **Package Manager**: Fastest installation via `apt-get`
- **Go Compilation**: Native performance
- **Shell Tools**: Full native support

#### **macOS**
- **Package Manager**: `brew` provides good performance
- **Go Compilation**: Native performance
- **Shell Tools**: Full native support

#### **Windows**
- **Package Manager**: `chocolatey` or `pacman` for system packages
- **Go Compilation**: Native performance
- **Shell Tools**: Limited support, use Python alternatives

#### **Snowflake Workspace**
- **Package Manager**: `apt-get` (Linux-based)
- **Go Compilation**: Native performance
- **Shell Tools**: Full native support
- **Network**: May have bandwidth limitations

## 🎉 **Conclusion**

Our `make install` targets are designed to be **platform-agnostic** and **Snowflake workspace compatible**. The platform detection system automatically adapts to the environment, ensuring consistent installation across different platforms.

**Key Benefits:**
- ✅ **Automatic Platform Detection**
- ✅ **Cross-Platform Package Management**
- ✅ **Fallback Strategies for Unsupported Platforms**
- ✅ **Comprehensive Testing Across Platforms**
- ✅ **Snowflake Workspace Compatibility**

**For Snowflake Workspace Deployment:**
1. Run `make help` to verify platform detection
2. Use `make install-all` for complete setup
3. Test with `make test-all` to verify functionality
4. Monitor with `make check-deps` for dependency status

The system is ready for deployment in Snowflake workspaces and other containerized environments! 🚀 