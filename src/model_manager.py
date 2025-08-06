#!/usr/bin/env python3
"""
Model Manager - Safe JSON Model Manipulation
Prevents corruption of fragile JSON models by using proper Python packages
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass
import logging
from datetime import datetime
import shutil
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelBackup:
    """Backup information for model files"""
    original_path: Path
    backup_path: Path
    timestamp: datetime
    checksum: str


class ModelManager:
    """Safe JSON model manipulation with backup and validation"""
    
    def __init__(self, models_dir: Path = Path(".")):
        self.models_dir = Path(models_dir)
        self.backup_dir = self.models_dir / ".model_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def _create_backup(self, file_path: Path) -> ModelBackup:
        """Create a backup of a model file before modification"""
        timestamp = datetime.now()
        backup_name = f"{file_path.stem}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = self.backup_dir / backup_name
        
        # Create backup
        shutil.copy2(file_path, backup_path)
        
        # Calculate checksum
        import hashlib
        with open(file_path, 'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest()
            
        return ModelBackup(
            original_path=file_path,
            backup_path=backup_path,
            timestamp=timestamp,
            checksum=checksum
        )
    
    def _validate_json(self, data: Any) -> bool:
        """Validate JSON structure"""
        try:
            # Test serialization
            json.dumps(data, indent=2)
            return True
        except (TypeError, ValueError) as e:
            logger.error(f"JSON validation failed: {e}")
            return False
    
    def _safe_load_json(self, file_path: Path) -> Dict[str, Any]:
        """Safely load JSON with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {file_path}")
            return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def _safe_save_json(self, file_path: Path, data: Dict[str, Any], backup: bool = True) -> bool:
        """Safely save JSON with backup and validation"""
        if backup:
            backup_info = self._create_backup(file_path)
            logger.info(f"Created backup: {backup_info.backup_path}")
        
        # Validate data before saving
        if not self._validate_json(data):
            logger.error(f"Invalid JSON data for {file_path}")
            return False
        
        # Use temporary file for atomic write
        temp_file = Path(tempfile.mktemp(suffix='.json'))
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic move
            shutil.move(str(temp_file), str(file_path))
            logger.info(f"Successfully saved {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {e}")
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a model file safely"""
        file_path = self.models_dir / f"{model_name}.json"
        return self._safe_load_json(file_path)
    
    def save_model(self, model_name: str, data: Dict[str, Any], backup: bool = True) -> bool:
        """Save a model file safely with backup"""
        file_path = self.models_dir / f"{model_name}.json"
        return self._safe_save_json(file_path, data, backup)
    
    def update_model_field(self, model_name: str, field_path: List[str], value: Any) -> bool:
        """Safely update a specific field in a model"""
        try:
            # Load current model
            data = self.load_model(model_name)
            
            # Navigate to field
            current = data
            for field in field_path[:-1]:
                if field not in current:
                    current[field] = {}
                current = current[field]
            
            # Update field
            current[field_path[-1]] = value
            
            # Save with backup
            return self.save_model(model_name, data, backup=True)
            
        except Exception as e:
            logger.error(f"Failed to update model field: {e}")
            return False
    
    def add_model_entry(self, model_name: str, entry_path: List[str], entry_data: Dict[str, Any]) -> bool:
        """Safely add a new entry to a model"""
        try:
            data = self.load_model(model_name)
            
            # Navigate to entry location
            current = data
            for field in entry_path[:-1]:
                if field not in current:
                    current[field] = {}
                current = current[field]
            
            # Add entry
            if entry_path[-1] not in current:
                current[entry_path[-1]] = {}
            current[entry_path[-1]].update(entry_data)
            
            return self.save_model(model_name, data, backup=True)
            
        except Exception as e:
            logger.error(f"Failed to add model entry: {e}")
            return False
    
    def remove_model_entry(self, model_name: str, entry_path: List[str]) -> bool:
        """Safely remove an entry from a model"""
        try:
            data = self.load_model(model_name)
            
            # Navigate to entry location
            current = data
            for field in entry_path[:-1]:
                if field not in current:
                    logger.warning(f"Path {entry_path} not found in model")
                    return False
                current = current[field]
            
            # Remove entry
            if entry_path[-1] in current:
                del current[entry_path[-1]]
                return self.save_model(model_name, data, backup=True)
            else:
                logger.warning(f"Entry {entry_path[-1]} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove model entry: {e}")
            return False
    
    def validate_model_structure(self, model_name: str, schema: Dict[str, Any]) -> bool:
        """Validate model structure against a schema"""
        try:
            data = self.load_model(model_name)
            return self._validate_against_schema(data, schema)
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return False
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any]) -> bool:
        """Recursively validate data against schema"""
        if not isinstance(data, type(schema)):
            return False
        
        if isinstance(schema, dict):
            for key, expected_type in schema.items():
                if key not in data:
                    return False
                if not self._validate_against_schema(data[key], expected_type):
                    return False
            return True
        
        elif isinstance(schema, list):
            if not isinstance(data, list):
                return False
            for item in data:
                if not self._validate_against_schema(item, schema[0]):
                    return False
            return True
        
        return True
    
    def list_backups(self) -> List[ModelBackup]:
        """List all available backups"""
        backups = []
        for backup_file in self.backup_dir.glob("*.json"):
            # Parse backup info from filename
            parts = backup_file.stem.split('_')
            if len(parts) >= 3:
                timestamp_str = f"{parts[-2]}_{parts[-1]}"
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    original_name = '_'.join(parts[:-2])
                    original_path = self.models_dir / f"{original_name}.json"
                    
                    backup = ModelBackup(
                        original_path=original_path,
                        backup_path=backup_file,
                        timestamp=timestamp,
                        checksum=""  # Would need to calculate
                    )
                    backups.append(backup)
                except ValueError:
                    continue
        
        return sorted(backups, key=lambda b: b.timestamp, reverse=True)
    
    def restore_backup(self, backup: ModelBackup) -> bool:
        """Restore a model from backup"""
        try:
            if not backup.backup_path.exists():
                logger.error(f"Backup file not found: {backup.backup_path}")
                return False
            
            # Create backup of current file if it exists
            if backup.original_path.exists():
                self._create_backup(backup.original_path)
            
            # Restore from backup
            shutil.copy2(backup.backup_path, backup.original_path)
            logger.info(f"Restored {backup.original_path} from backup")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Initialize model manager
    manager = ModelManager()
    
    # Example: Safely update a model
    success = manager.update_model_field(
        "project_model_registry",
        ["domains", "python", "linter"],
        "flake8"
    )
    
    if success:
        print("✅ Model updated successfully")
    else:
        print("❌ Model update failed")
    
    # List available backups
    backups = manager.list_backups()
    print(f"📦 Found {len(backups)} backups") 