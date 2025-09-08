# Model Manager Guide - Safe JSON Model Manipulation

## 🛡️ **Problem Solved**

You're absolutely right about the risk of corrupting fragile JSON models! Every time we manually edit JSON files, we risk:
- **Syntax errors** from missing commas, brackets, etc.
- **Structural corruption** from improper nesting
- **Data loss** from incomplete edits
- **Version control issues** from corrupted files

## 🎯 **Solution: ModelManager**

The `ModelManager` class provides safe, programmatic manipulation of JSON models with:

### **✅ Safety Features:**
- **Automatic backups** before any modification
- **JSON validation** before saving
- **Atomic writes** using temporary files
- **Error handling** with rollback capability
- **Structure validation** against schemas

### **✅ Key Methods:**

#### **Safe Loading:**
```python
from src.model_manager import ModelManager

manager = ModelManager()
data = manager.load_model("project_model_registry")
```

#### **Safe Field Updates:**
```python
# Update a specific field safely
success = manager.update_model_field(
    "project_model_registry",
    ["domains", "python", "linter"],
    "flake8"
)
```

#### **Safe Entry Addition:**
```python
# Add a new domain safely
success = manager.add_model_entry(
    "project_model_registry",
    ["domains"],
    {
        "new_domain": {
            "patterns": ["*.new"],
            "linter": "custom_linter"
        }
    }
)
```

#### **Safe Entry Removal:**
```python
# Remove an entry safely
success = manager.remove_model_entry(
    "project_model_registry",
    ["domains", "old_domain"]
)
```

#### **Backup Management:**
```python
# List available backups
backups = manager.list_backups()
for backup in backups:
    print(f"Backup: {backup.original_path.name} ({backup.timestamp})")

# Restore from backup
success = manager.restore_backup(backup)
```

#### **Structure Validation:**
```python
# Validate model structure
schema = {
    "domains": dict,
    "requirements_traceability": list
}
is_valid = manager.validate_model_structure("project_model_registry", schema)
```

## 🚀 **Usage Examples**

### **Example 1: Update Model Field**
```python
from src.model_manager import ModelManager

manager = ModelManager()

# Safely update the Python linter
success = manager.update_model_field(
    "project_model_registry",
    ["domains", "python", "linter"],
    "black"
)

if success:
    print("✅ Model updated safely")
else:
    print("❌ Update failed - check logs")
```

### **Example 2: Add New Domain**
```python
# Add a new domain configuration
new_domain = {
    "typescript": {
        "patterns": ["*.ts", "*.tsx"],
        "linter": "eslint",
        "validator": "tsc",
        "formatter": "prettier"
    }
}

success = manager.add_model_entry(
    "project_model_registry",
    ["domains"],
    new_domain
)
```

### **Example 3: Backup and Restore**
```python
# List all backups
backups = manager.list_backups()
print(f"Available backups: {len(backups)}")

# Restore from most recent backup
if backups:
    latest_backup = backups[0]
    success = manager.restore_backup(latest_backup)
    if success:
        print("✅ Model restored from backup")
```

## 🛡️ **Safety Guarantees**

### **1. Automatic Backups**
- Every modification creates a timestamped backup
- Backups stored in `.model_backups/` directory
- Original file never directly modified

### **2. Atomic Writes**
- Uses temporary files for writing
- Atomic move operation ensures consistency
- No partial writes possible

### **3. JSON Validation**
- Validates JSON structure before saving
- Prevents syntax errors from reaching files
- Detailed error logging

### **4. Error Recovery**
- Failed operations don't corrupt files
- Automatic rollback on errors
- Backup restoration available

## 📋 **Best Practices**

### **✅ Do:**
- Use ModelManager for all JSON model modifications
- Always check return values for success/failure
- Use backup restoration when needed
- Validate model structure after changes

### **❌ Don't:**
- Edit JSON files manually in text editors
- Modify models without backups
- Ignore validation errors
- Skip error checking

## 🔧 **Integration with Existing Workflow**

### **Before (Risky):**
```bash
# Manual editing - risky!
vim project_model_registry.json
# Risk of syntax errors, corruption, etc.
```

### **After (Safe):**
```python
# Programmatic editing - safe!
from src.model_manager import ModelManager

manager = ModelManager()
success = manager.update_model_field(
    "project_model_registry",
    ["domains", "python", "linter"],
    "black"
)
```

## 🎯 **Next Steps**

1. **Replace manual JSON editing** with ModelManager calls
2. **Add model validation** to CI/CD pipeline
3. **Create model schemas** for structure validation
4. **Automate model updates** in scripts

**The ModelManager ensures your fragile JSON models stay intact while allowing safe, programmatic manipulation!** 🛡️ 