#!/usr/bin/env python3
"""Checkpointed AST Modeler with logging and recovery"""

import ast
import json
import os
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class ASTModel:
    """AST model for a Python file"""
    file_path: str
    file_type: str = "python"
    model_type: str = "ast"
    complexity_score: float = 0.0
    line_count: int = 0
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    error_count: int = 0
    model_data: Dict[str, Any] = None

class CheckpointedASTModeler:
    """AST modeler with checkpointing and recovery"""
    
    def __init__(self, database_file: str = "ast_models.json"):
        self.database_file = database_file
        self.checkpoint_dir = Path("checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        self.database = {
            "file_models": {},
            "summary": {
                "total_files": 0,
                "valid_files": 0,
                "error_files": 0,
                "model_type_counts": {}
            },
            "metadata": {
                "last_updated": "",
                "checkpoint_count": 0,
                "version": "1.0"
            }
        }
        
        # Exclude patterns for generated/temporary files
        self.exclude_patterns = [
            ".venv", "venv", "__pycache__", ".git", "node_modules",
            ".pytest_cache", ".mypy_cache", "build", "dist", "*.pyc",
            "*.pyo", "*.pyd", "*.so", "*.dll", "*.dylib",
            "backup*", "*.backup*", "*.tmp", "*.temp",
            "comprehensive_ast_modeler.py", "enhanced_python_modeler.py",
            "broken_python_interpreter.py", "semantic_reconstructor.py",
            "git_enhanced_ast_fixer.py", "aggressive_syntax_fixer.py",
            "comprehensive_syntax_fixer.py", "python_ast_fixer.py",
            "fix_*.py", "test_*.py", "*_test.py"
        ]
        
        # Load existing database if it exists
        self.load_database()
    
    def load_database(self):
        """Load existing database or create new one"""
        if Path(self.database_file).exists():
            try:
                with open(self.database_file, 'r') as f:
                    self.database = json.load(f)
                print(f"📂 Loaded existing database: {self.database_file}")
                print(f"📊 Current files: {len(self.database['file_models'])}")
            except Exception as e:
                print(f"⚠️ Failed to load database: {e}")
                print("🔄 Creating new database")
                self.database = {
                    "file_models": {},
                    "summary": {"total_files": 0, "valid_files": 0, "error_files": 0, "model_type_counts": {}},
                    "metadata": {"last_updated": "", "checkpoint_count": 0, "version": "1.0"}
                }
        else:
            print("🆕 Creating new database")
    
    def save_database(self, checkpoint: bool = False):
        """Save database with optional checkpointing"""
        try:
            # Update metadata
            self.database["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save main database
            with open(self.database_file, 'w') as f:
                json.dump(self.database, f, indent=2)
            
            print(f"💾 Saved database: {self.database_file}")
            
            # Create checkpoint if requested
            if checkpoint:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                checkpoint_file = self.checkpoint_dir / f"ast_models_{timestamp}.json"
                
                with open(checkpoint_file, 'w') as f:
                    json.dump(self.database, f, indent=2)
                
                self.database["metadata"]["checkpoint_count"] += 1
                print(f"📦 Created checkpoint: {checkpoint_file}")
                
                # Keep only last 5 checkpoints
                self.cleanup_old_checkpoints()
            
            print(f"📊 Summary: {self.database['summary']}")
            
        except Exception as e:
            print(f"❌ Failed to save database: {e}")
            raise
    
    def cleanup_old_checkpoints(self, keep_count: int = 5):
        """Keep only the most recent checkpoints"""
        checkpoint_files = sorted(self.checkpoint_dir.glob("ast_models_*.json"))
        
        if len(checkpoint_files) > keep_count:
            files_to_delete = checkpoint_files[:-keep_count]
            for file in files_to_delete:
                file.unlink()
                print(f"🗑️ Deleted old checkpoint: {file}")
    
    def list_checkpoints(self):
        """List available checkpoints"""
        checkpoint_files = sorted(self.checkpoint_dir.glob("ast_models_*.json"))
        print(f"📦 Available checkpoints ({len(checkpoint_files)}):")
        for file in checkpoint_files:
            size = file.stat().st_size
            print(f"  {file.name} ({size} bytes)")
    
    def restore_from_checkpoint(self, checkpoint_name: str):
        """Restore database from checkpoint"""
        checkpoint_file = self.checkpoint_dir / checkpoint_name
        
        if not checkpoint_file.exists():
            print(f"❌ Checkpoint not found: {checkpoint_file}")
            return False
        
        try:
            with open(checkpoint_file, 'r') as f:
                self.database = json.load(f)
            
            # Save as current database
            with open(self.database_file, 'w') as f:
                json.dump(self.database, f, indent=2)
            
            print(f"✅ Restored from checkpoint: {checkpoint_name}")
            print(f"📊 Files in restored database: {len(self.database['file_models'])}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore checkpoint: {e}")
            return False
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded"""
        file_path_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            if pattern in file_path_str:
                return True
        
        return False
    
    def find_python_files(self, directory: str) -> List[str]:
        """Find Python files to model, excluding generated/temporary files"""
        python_files = []
        
        for file_path in Path(directory).rglob("*.py"):
            if not self.should_exclude_file(file_path):
                python_files.append(str(file_path))
        
        return python_files
    
    def model_python_file(self, file_path: str) -> ASTModel:
        """Model a Python file using AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST
            tree = ast.parse(content)
            
            # Extract information
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            # Calculate complexity (simple line-based for now)
            lines = content.split('\n')
            complexity = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Extract docstrings
            docstrings = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(docstring)
            
            # Extract imports
            import_names = []
            for imp in imports:
                if isinstance(imp, ast.Import):
                    for alias in imp.names:
                        import_names.append(alias.name)
                elif isinstance(imp, ast.ImportFrom):
                    module = imp.module or ""
                    for alias in imp.names:
                        import_names.append(f"{module}.{alias.name}")
            
            model_data = {
                "docstrings": docstrings,
                "imports": import_names,
                "functions": [{"name": func.name, "docstring": ast.get_docstring(func)} for func in functions],
                "classes": [{"name": cls.name, "docstring": ast.get_docstring(cls)} for cls in classes],
                "variables": [],
                "line_count": len(lines)
            }
            
            return ASTModel(
                file_path=file_path,
                model_type="ast",
                complexity_score=complexity,
                line_count=len(lines),
                function_count=len(functions),
                class_count=len(classes),
                import_count=len(imports),
                error_count=0,
                model_data=model_data
            )
            
        except Exception as e:
            # Create error model
            return ASTModel(
                file_path=file_path,
                model_type="error",
                error_count=1,
                model_data={"error": str(e)}
            )
    
    def model_directory(self, directory: str, checkpoint_interval: int = 10) -> Dict[str, Any]:
        """Model all Python files in directory with checkpointing"""
        print(f"🔍 Finding Python files in {directory}")
        
        python_files = self.find_python_files(directory)
        print(f"📁 Found {len(python_files)} Python files to model")
        
        for i, file_path in enumerate(python_files, 1):
            print(f"  [{i}/{len(python_files)}] Modeling {file_path}")
            
            model = self.model_python_file(file_path)
            self.database["file_models"][file_path] = asdict(model)
            
            # Update summary
            self.database["summary"]["total_files"] += 1
            if model.model_type == "ast":
                self.database["summary"]["valid_files"] += 1
            else:
                self.database["summary"]["error_files"] += 1
            
            # Update model type counts
            model_type = model.model_type
            self.database["summary"]["model_type_counts"][model_type] = \
                self.database["summary"]["model_type_counts"].get(model_type, 0) + 1
            
            # Checkpoint every N files
            if i % checkpoint_interval == 0:
                print(f"📦 Creating checkpoint at file {i}")
                self.save_database(checkpoint=True)
        
        return self.database
    
    def incremental_update(self, directory: str):
        """Update only files that have changed"""
        print("🔄 Performing incremental update")
        
        python_files = self.find_python_files(directory)
        updated_count = 0
        
        for file_path in python_files:
            # Check if file has changed (simple file modification time check)
            file_stat = Path(file_path).stat()
            file_mtime = file_stat.st_mtime
            
            existing_model = self.database["file_models"].get(file_path)
            
            if existing_model:
                # Check if file was modified since last model
                last_model_time = existing_model.get("metadata", {}).get("mtime", 0)
                if file_mtime <= last_model_time:
                    continue  # Skip unchanged files
            
            print(f"🔄 Updating {file_path}")
            model = self.model_python_file(file_path)
            model_dict = asdict(model)
            model_dict["metadata"] = {"mtime": file_mtime}
            
            self.database["file_models"][file_path] = model_dict
            updated_count += 1
        
        print(f"✅ Updated {updated_count} files")
        self.save_database(checkpoint=True)

def main():
    """Model the project with checkpointing"""
    modeler = CheckpointedASTModeler()
    
    print("🚀 Starting Checkpointed AST Modeling")
    print("=" * 50)
    
    # List existing checkpoints
    modeler.list_checkpoints()
    
    # Model the current directory with checkpointing every 10 files
    database = modeler.model_directory(".", checkpoint_interval=10)
    
    # Save final database with checkpoint
    modeler.save_database(checkpoint=True)
    
    print("✅ Checkpointed AST modeling complete!")

if __name__ == "__main__":
    main() 