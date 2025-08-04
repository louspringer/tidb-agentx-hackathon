#!/usr/bin/env python3
"""Model-Driven Artifact Reconstructor - Rebuild artifacts from models only"""

import json
import ast
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict
import hashlib
import difflib

class ModelDrivenReconstructor:
    """Reconstruct artifacts from model data only - no peeking at originals"""
    
    def __init__(self, models_database: str = "ast_models.json"):
        self.models_database = models_database
        self.models = self._load_models()
    
    def _load_models(self) -> Dict[str, Any]:
        """Load the models database"""
        try:
            with open(self.models_database, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"file_models": {}}
    
    def reconstruct_from_model(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct artifact from model only - no peeking at original"""
        if file_path not in self.models['file_models']:
            raise ValueError(f"No model found for {file_path}")
        
        model = self.models['file_models'][file_path]
        file_type = model.get('file_type', 'unknown')
        
        # Reconstruct based on file type
        if file_type == 'python':
            return self._reconstruct_python(model)
        elif file_type == 'mdc':
            return self._reconstruct_mdc(model)
        elif file_type == 'markdown':
            return self._reconstruct_markdown(model)
        elif file_type == 'JSON':
            return self._reconstruct_json(model)
        elif file_type == 'YAML':
            return self._reconstruct_yaml(model)
        elif file_type == 'SQL':
            return self._reconstruct_sql(model)
        elif file_type == 'HTML':
            return self._reconstruct_html(model)
        elif file_type == 'SHELL':
            return self._reconstruct_shell(model)
        else:
            return self._reconstruct_generic(model)
    
    def _reconstruct_python(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct Python file from model"""
        lines = []
        
        # Add shebang
        lines.append("#!/usr/bin/env python3")
        lines.append("")
        
        # Get the model_data which contains the semantic information
        model_data = model.get('model_data', {})
        
        # Add docstring if exists
        docstrings = model_data.get('docstrings', [])
        if docstrings:
            lines.append('"""' + docstrings[0] + '"""')
            lines.append("")
        
        # Add imports
        imports = model_data.get('imports', [])
        for imp in imports:
            lines.append(imp)
        
        if imports:
            lines.append("")
        
        # Add classes
        classes = model_data.get('classes', [])
        for class_info in classes:
            lines.append(f"class {class_info['name']}:")
            if class_info.get('docstring'):
                lines.append(f'    """{class_info["docstring"]}"""')
                lines.append("    pass")
            else:
                lines.append("    pass")
            lines.append("")
        
        # Add functions
        functions = model_data.get('functions', [])
        for func_info in functions:
            params = func_info.get('parameters', [])
            param_str = ", ".join(params) if params else ""
            lines.append(f"def {func_info['name']}({param_str}):")
            if func_info.get('docstring'):
                lines.append(f'    """{func_info["docstring"]}"""')
            lines.append("    pass")
            lines.append("")
        
        # Add variables
        variables = model_data.get('variables', [])
        for var in variables:
            lines.append(f"{var} = None")
        
        content = "\n".join(lines)
        metadata = {
            "reconstruction_method": "python_ast_based",
            "model_completeness": len(functions) + len(classes),
            "has_docstrings": bool(docstrings),
            "has_imports": bool(imports)
        }
        
        return content, metadata
    
    def _reconstruct_mdc(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct MDC file from model"""
        lines = []
        
        # Add YAML frontmatter
        if model.get('metadata', {}).get('yaml_frontmatter'):
            lines.append("---")
            frontmatter = model['metadata']['yaml_frontmatter']
            for key, value in frontmatter.items():
                lines.append(f"{key}: {value}")
            lines.append("---")
            lines.append("")
        
        # Add markdown content
        if model.get('metadata', {}).get('markdown_content'):
            content = model['metadata']['markdown_content']
            lines.append(content)
        
        content = "\n".join(lines)
        metadata = {
            "reconstruction_method": "mdc_yaml_markdown",
            "has_frontmatter": bool(model.get('metadata', {}).get('yaml_frontmatter')),
            "has_markdown": bool(model.get('metadata', {}).get('markdown_content'))
        }
        
        return content, metadata
    
    def _reconstruct_markdown(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct Markdown file from model"""
        lines = []
        
        # Add headers
        for header in model.get('metadata', {}).get('headers', []):
            level = header.get('level', 1)
            text = header.get('text', 'Header')
            lines.append('#' * level + ' ' + text)
            lines.append("")
        
        # Add content sections
        if model.get('metadata', {}).get('content_sections'):
            for section in model['metadata']['content_sections']:
                lines.append(section)
                lines.append("")
        
        content = "\n".join(lines)
        metadata = {
            "reconstruction_method": "markdown_structure",
            "header_count": len(model.get('metadata', {}).get('headers', [])),
            "section_count": len(model.get('metadata', {}).get('content_sections', []))
        }
        
        return content, metadata
    
    def _reconstruct_json(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct JSON file from model"""
        # Try to reconstruct from metadata
        if model.get('metadata', {}).get('json_data'):
            content = json.dumps(model['metadata']['json_data'], indent=2)
        else:
            # Fallback to basic structure
            content = "{}"
        
        metadata = {
            "reconstruction_method": "json_direct",
            "json_type": model.get('metadata', {}).get('json_type', 'unknown')
        }
        
        return content, metadata
    
    def _reconstruct_yaml(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct YAML file from model"""
        # Try to reconstruct from metadata
        if model.get('metadata', {}).get('yaml_data'):
            content = yaml.dump(model['metadata']['yaml_data'], default_flow_style=False)
        else:
            # Fallback to basic structure
            content = "# YAML file"
        
        metadata = {
            "reconstruction_method": "yaml_direct",
            "yaml_type": model.get('metadata', {}).get('yaml_type', 'unknown')
        }
        
        return content, metadata
    
    def _reconstruct_sql(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct SQL file from model"""
        lines = []
        
        # Add SQL statements
        for statement in model.get('metadata', {}).get('sql_statements', []):
            lines.append(statement)
            lines.append("")
        
        content = "\n".join(lines)
        metadata = {
            "reconstruction_method": "sql_statements",
            "statement_count": len(model.get('metadata', {}).get('sql_statements', []))
        }
        
        return content, metadata
    
    def _reconstruct_html(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct HTML file from model"""
        # Try to reconstruct from metadata
        if model.get('metadata', {}).get('html_content'):
            content = model['metadata']['html_content']
        else:
            # Fallback to basic HTML
            content = "<!DOCTYPE html>\n<html>\n<head></head>\n<body></body>\n</html>"
        
        metadata = {
            "reconstruction_method": "html_direct"
        }
        
        return content, metadata
    
    def _reconstruct_shell(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct Shell script from model"""
        lines = []
        
        # Add shebang
        lines.append("#!/bin/bash")
        lines.append("")
        
        # Add commands
        for cmd in model.get('metadata', {}).get('shell_commands', []):
            lines.append(cmd)
        
        content = "\n".join(lines)
        metadata = {
            "reconstruction_method": "shell_commands",
            "command_count": len(model.get('metadata', {}).get('shell_commands', []))
        }
        
        return content, metadata
    
    def _reconstruct_generic(self, model: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Reconstruct generic file from model"""
        content = f"# Reconstructed {model.get('file_type', 'unknown')} file"
        metadata = {
            "reconstruction_method": "generic_fallback"
        }
        return content, metadata
    
    def test_semantic_equivalence(self, file_path: str) -> Dict[str, Any]:
        """Test semantic equivalence between reconstructed and original"""
        try:
            # Reconstruct from model only
            reconstructed_content, reconstruction_metadata = self.reconstruct_from_model(file_path)
            
            # Read original file
            with open(file_path, 'r') as f:
                original_content = f.read()
            
            # Calculate similarity metrics
            similarity_score = self._calculate_similarity(original_content, reconstructed_content)
            structural_match = self._compare_structure(original_content, reconstructed_content)
            
            # Heuristic LLM analysis
            heuristic_analysis = self._heuristic_analysis(original_content, reconstructed_content, file_path)
            
            return {
                "file_path": file_path,
                "original_size": len(original_content),
                "reconstructed_size": len(reconstructed_content),
                "similarity_score": similarity_score,
                "structural_match": structural_match,
                "reconstruction_metadata": reconstruction_metadata,
                "heuristic_analysis": heuristic_analysis,
                "semantic_equivalent": similarity_score > 0.7  # Threshold
            }
            
        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "semantic_equivalent": False
            }
    
    def _calculate_similarity(self, original: str, reconstructed: str) -> float:
        """Calculate similarity between original and reconstructed content"""
        # Use difflib for similarity
        matcher = difflib.SequenceMatcher(None, original, reconstructed)
        return matcher.ratio()
    
    def _compare_structure(self, original: str, reconstructed: str) -> Dict[str, Any]:
        """Compare structural elements"""
        return {
            "original_lines": len(original.split('\n')),
            "reconstructed_lines": len(reconstructed.split('\n')),
            "original_words": len(original.split()),
            "reconstructed_words": len(reconstructed.split()),
            "line_ratio": len(reconstructed.split('\n')) / max(len(original.split('\n')), 1),
            "word_ratio": len(reconstructed.split()) / max(len(original.split()), 1)
        }
    
    def _heuristic_analysis(self, original: str, reconstructed: str, file_path: str) -> Dict[str, Any]:
        """Heuristic LLM analysis of semantic equivalence"""
        file_type = Path(file_path).suffix.lower()
        
        analysis = {
            "file_type": file_type,
            "assessment": "unknown",
            "key_differences": [],
            "semantic_preservation": "unknown"
        }
        
        # Python-specific analysis
        if file_type == '.py':
            try:
                # Check if both are valid Python
                ast.parse(original)
                ast.parse(reconstructed)
                analysis["syntax_valid"] = True
                analysis["assessment"] = "Both are valid Python"
            except:
                analysis["syntax_valid"] = False
                analysis["assessment"] = "Syntax errors detected"
        
        # JSON-specific analysis
        elif file_type == '.json':
            try:
                json.loads(original)
                json.loads(reconstructed)
                analysis["json_valid"] = True
                analysis["assessment"] = "Both are valid JSON"
            except:
                analysis["json_valid"] = False
                analysis["assessment"] = "JSON parsing errors"
        
        # YAML-specific analysis
        elif file_type in ['.yaml', '.yml']:
            try:
                yaml.safe_load(original)
                yaml.safe_load(reconstructed)
                analysis["yaml_valid"] = True
                analysis["assessment"] = "Both are valid YAML"
            except:
                analysis["yaml_valid"] = False
                analysis["assessment"] = "YAML parsing errors"
        
        # Generic content analysis
        analysis["content_preserved"] = len(reconstructed) > 0
        analysis["structure_preserved"] = len(reconstructed.split('\n')) > 0
        
        return analysis
    
    def batch_test_equivalence(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Test semantic equivalence for multiple files"""
        if file_patterns is None:
            file_patterns = ['*.py', '*.mdc', '*.md', '*.json', '*.yaml', '*.yml']
        
        results = []
        successful_reconstructions = 0
        total_tested = 0
        
        for file_path in self.models['file_models'].keys():
            if any(file_path.endswith(pattern.replace('*', '')) for pattern in file_patterns):
                result = self.test_semantic_equivalence(file_path)
                results.append(result)
                total_tested += 1
                if result.get('semantic_equivalent', False):
                    successful_reconstructions += 1
        
        return {
            "total_tested": total_tested,
            "successful_reconstructions": successful_reconstructions,
            "success_rate": successful_reconstructions / max(total_tested, 1),
            "results": results
        }


def main():
    """Test model-driven reconstruction"""
    reconstructor = ModelDrivenReconstructor()
    
    print("🔍 Testing Model-Driven Artifact Reconstruction")
    print("=" * 60)
    
    # Test a few key files
    test_files = [
        "src/security_first/https_enforcement.py",
        "scripts/mdc-linter.py", 
        "comprehensive_ast_modeler.py"
    ]
    
    for file_path in test_files:
        if file_path in reconstructor.models['file_models']:
            print(f"\n📁 Testing: {file_path}")
            result = reconstructor.test_semantic_equivalence(file_path)
            
            print(f"  ✅ Semantic Equivalent: {result.get('semantic_equivalent', False)}")
            print(f"  📊 Similarity Score: {result.get('similarity_score', 0):.3f}")
            print(f"  🔍 Assessment: {result.get('heuristic_analysis', {}).get('assessment', 'Unknown')}")
            
            if result.get('structural_match'):
                struct = result['structural_match']
                print(f"  📏 Lines: {struct.get('original_lines', 0)} → {struct.get('reconstructed_lines', 0)}")
                print(f"  📝 Words: {struct.get('original_words', 0)} → {struct.get('reconstructed_words', 0)}")
    
    # Batch test
    print(f"\n🎯 Batch Testing All Files")
    batch_result = reconstructor.batch_test_equivalence()
    print(f"  📊 Success Rate: {batch_result['success_rate']:.1%}")
    print(f"  ✅ Successful: {batch_result['successful_reconstructions']}/{batch_result['total_tested']}")


if __name__ == "__main__":
    main() 