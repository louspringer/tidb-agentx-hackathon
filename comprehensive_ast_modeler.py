#!/usr/bin/env python3
"""Comprehensive AST Modeler for ALL artifact types - Python, MDC, Markdown, SQL, YAML, JSON, XML, HTML, CSS, JS, Docker, K8s, CloudFormation, etc."""

import ast
import json
import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import yaml
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


@dataclass
class ASTModel:
    """AST model for any file type"""
    file_path: str
    file_type: str  # 'python', 'mdc', 'markdown'
    model_type: str  # 'ast', 'interpretation', 'basic'
    model_data: Dict[str, Any]
    complexity_score: float
    structure_hash: str
    lines_of_code: int
    created_at: str
    commit_hash: Optional[str] = None


@dataclass
class EvolutionPattern:
    """Evolution pattern across commits"""
    file_path: str
    generation_count: int
    trend_data: Dict[str, Any]
    stability_score: float
    best_template_generation: Optional[int] = None


@dataclass
class ConsistencyCheck:
    """Model consistency check result"""
    file_path: str
    current_model_hash: str
    committed_model_hash: Optional[str]
    persisted_model_hash: Optional[str]
    similarity_score: float
    model_leak_detected: bool
    created_at: str


class PythonASTModeler:
    """Proper Python AST modeler using correct AST parsing techniques"""
    
    def model_python_file(self, file_path: str) -> ASTModel:
        """Model Python file using proper AST parsing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST (like Python kernel does)
            tree = ast.parse(content)
            
            # Extract semantic information using proper AST traversal
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            variables = self._extract_variables(tree)
            dependencies = self._extract_dependencies(tree)
            docstrings = self._extract_docstrings(tree)
            error_handling = self._extract_error_handling(tree)
            type_hints = self._extract_type_hints(tree)
            
            # Calculate complexity metrics
            complexity_metrics = self._calculate_complexity_metrics(tree)
            nesting_depth = self._calculate_nesting_depth(tree)
            
            # Generate structure hash
            structure_hash = hashlib.md5(str(tree).encode()).hexdigest()
            
            return ASTModel(
                file_path=file_path,
                file_type="python",
                model_type="ast",
                model_data={
                    "imports": imports,
                    "functions": functions,
                    "classes": classes,
                    "variables": variables,
                    "dependencies": dependencies,
                    "docstrings": docstrings,
                    "error_handling": error_handling,
                    "type_hints": type_hints,
                    "complexity_metrics": complexity_metrics,
                    "nesting_depth": nesting_depth,
                    "ast_nodes": len(list(ast.walk(tree))),
                    "structure_hash": structure_hash
                },
                complexity_score=complexity_metrics.get('cyclomatic', 1),
                structure_hash=structure_hash,
                lines_of_code=len(content.split('\n')),
                created_at=datetime.now().isoformat(),
                commit_hash=self._get_commit_hash(file_path)
            )
            
        except Exception as e:
            # Fallback to basic modeling if AST parsing fails
            return self._create_basic_model(file_path, str(e))
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all imports from AST (like linters do)"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if alias.name == "*":
                        imports.append(f"from {module} import *")
                    else:
                        imports.append(f"from {module} import {alias.name}")
        
        return imports
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions with semantic info"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "parameters": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                    "lineno": getattr(node, 'lineno', 0),
                    "col_offset": getattr(node, 'col_offset', 0),
                    "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    "returns": self._extract_return_type(node),
                    "has_async": isinstance(node, ast.AsyncFunctionDef)
                }
                functions.append(func_info)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions with semantic info"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "bases": [self._get_base_name(base) for base in node.bases],
                    "docstring": ast.get_docstring(node),
                    "lineno": getattr(node, 'lineno', 0),
                    "col_offset": getattr(node, 'col_offset', 0),
                    "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    "attributes": [n.targets[0].id for n in node.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
                }
                classes.append(class_info)
        
        return classes
    
    def _extract_variables(self, tree: ast.AST) -> List[str]:
        """Extract variable assignments"""
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
        
        return variables
    
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract external dependencies from imports"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module.split('.')[0])
        
        return list(set(dependencies))
    
    def _extract_docstrings(self, tree: ast.AST) -> List[str]:
        """Extract all docstrings"""
        docstrings = []
        
        for node in ast.walk(tree):
            # Only certain node types can have docstrings
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                try:
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(docstring)
                except:
                    pass  # Skip if docstring extraction fails
        
        return docstrings
    
    def _extract_error_handling(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract error handling patterns"""
        error_handling = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                handlers = []
                for handler in node.handlers:
                    handlers.append({
                        "type": self._get_exception_type(handler.type) if handler.type else "Exception",
                        "lineno": getattr(handler, 'lineno', 0)
                    })
                error_handling.append({
                    "type": "try_except",
                    "handlers": handlers,
                    "lineno": getattr(node, 'lineno', 0)
                })
        
        return error_handling
    
    def _extract_type_hints(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract type hints and annotations"""
        type_hints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check return type annotation
                if node.returns:
                    type_hints.append({
                        "type": "return_annotation",
                        "function": node.name,
                        "annotation": self._get_annotation_name(node.returns)
                    })
                
                # Check parameter type annotations
                for arg in node.args.args:
                    if arg.annotation:
                        type_hints.append({
                            "type": "parameter_annotation",
                            "function": node.name,
                            "parameter": arg.arg,
                            "annotation": self._get_annotation_name(arg.annotation)
                        })
        
        return type_hints
    
    def _calculate_complexity_metrics(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate complexity metrics like linters do"""
        cyclomatic = 1  # Base complexity
        cognitive = 0
        nesting = 0
        statements = 0
        
        for node in ast.walk(tree):
            # Cyclomatic complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                cyclomatic += 1
            elif isinstance(node, ast.ExceptHandler):
                cyclomatic += 1
            elif isinstance(node, ast.With):
                cyclomatic += 1
            
            # Cognitive complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                cognitive += 1
            elif isinstance(node, ast.ExceptHandler):
                cognitive += 1
            elif isinstance(node, ast.BoolOp):
                cognitive += len(node.values) - 1
            
            # Nesting depth
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try, ast.With)):
                nesting = max(nesting, self._calculate_node_depth(node))
            
            # Statement count
            if isinstance(node, (ast.Assign, ast.Expr, ast.Return, ast.Raise, ast.Assert)):
                statements += 1
        
        return {
            "cyclomatic": cyclomatic,
            "cognitive": cognitive,
            "nesting": nesting,
            "statements": statements
        }
    
    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        
        def visit_node(node, depth):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, depth + 1)
        
        visit_node(tree, 0)
        return max_depth
    
    def _calculate_node_depth(self, node: ast.AST) -> int:
        """Calculate depth of a specific node"""
        depth = 0
        current = node
        while hasattr(current, 'parent'):
            current = current.parent
            depth += 1
        return depth
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return "unknown"
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Extract base class name"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{self._get_base_name(base.value)}.{base.attr}"
        return "unknown"
    
    def _get_exception_type(self, exc_type: ast.expr) -> str:
        """Extract exception type name"""
        if isinstance(exc_type, ast.Name):
            return exc_type.id
        elif isinstance(exc_type, ast.Attribute):
            return f"{self._get_base_name(exc_type.value)}.{exc_type.attr}"
        return "Exception"
    
    def _get_annotation_name(self, annotation: ast.expr) -> str:
        """Extract type annotation name"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_base_name(annotation.value)}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            return f"{self._get_annotation_name(annotation.value)}[{self._get_annotation_name(annotation.slice)}]"
        return "unknown"
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation"""
        if node.returns:
            return self._get_annotation_name(node.returns)
        return None
    
    def _get_commit_hash(self, file_path: str) -> str:
        """Get git commit hash for file"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _create_basic_model(self, file_path: str, error: str) -> ASTModel:
        """Create basic model when AST parsing fails"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ASTModel(
                file_path=file_path,
                file_type="python",
                model_type="basic",
                model_data={
                    "basic_error": error,
                    "file_size": len(content),
                    "lines_of_code": len(content.split('\n')),
                    "complexity_metrics": {"cyclomatic": 1, "cognitive": 0, "nesting": 0, "statements": 0}
                },
                complexity_score=1,
                structure_hash="",
                lines_of_code=len(content.split('\n')),
                created_at=datetime.now().isoformat(),
                commit_hash="unknown"
            )
        except Exception as e:
            return ASTModel(
                file_path=file_path,
                file_type="python",
                model_type="error",
                model_data={"error": str(e)},
                complexity_score=0,
                structure_hash="",
                lines_of_code=0,
                created_at=datetime.now().isoformat(),
                commit_hash="unknown"
            )


class MDCModeler:
    """Modeler for MDC files (Markdown with YAML frontmatter)"""
    
    def model_mdc_file(self, file_path: str) -> ASTModel:
        """Create model for MDC file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter and markdown content
            frontmatter, markdown_content = self._parse_mdc_content(content)
            
            model_data = {
                'frontmatter': frontmatter,
                'markdown_analysis': self._analyze_markdown(markdown_content),
                'yaml_structure': self._analyze_yaml_structure(frontmatter),
                'content_metrics': self._calculate_content_metrics(content),
                'lines_of_code': len(content.splitlines()),
                'rule_compliance': self._check_rule_compliance(frontmatter, markdown_content)
            }
            
            complexity_score = self._calculate_mdc_complexity(model_data)
            structure_hash = self._generate_mdc_structure_hash(model_data)
            
            return ASTModel(
                file_path=file_path,
                file_type='mdc',
                model_type='ast',
                model_data=model_data,
                complexity_score=complexity_score,
                structure_hash=structure_hash,
                lines_of_code=model_data['lines_of_code'],
                created_at=datetime.now().isoformat(),
                commit_hash=self._get_commit_hash(file_path)
            )
            
        except Exception as e:
            return self._create_mdc_basic_model(file_path, str(e))
    
    def _parse_mdc_content(self, content: str) -> tuple:
        """Parse MDC content into frontmatter and markdown"""
        lines = content.splitlines()
        
        if not lines or lines[0].strip() != '---':
            return {}, content
        
        # Find frontmatter end
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return {}, content
        
        # Extract frontmatter and markdown
        frontmatter_lines = lines[1:end_index]
        markdown_lines = lines[end_index + 1:]
        
        frontmatter_text = '\n'.join(frontmatter_lines)
        markdown_content = '\n'.join(markdown_lines)
        
        # Parse YAML frontmatter
        try:
            import yaml
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except:
            frontmatter = {}
        
        return frontmatter, markdown_content
    
    def _analyze_markdown(self, content: str) -> Dict[str, Any]:
        """Analyze markdown content structure"""
        lines = content.splitlines()
        
        # Count different markdown elements
        headers = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        code_blocks = len(re.findall(r'```', content))
        lists = len(re.findall(r'^[\s]*[-*+]\s+', content, re.MULTILINE))
        links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        emphasis = len(re.findall(r'\*\*([^*]+)\*\*|\*([^*]+)\*', content))
        
        return {
            'headers': headers,
            'code_blocks': code_blocks,
            'lists': lists,
            'links': links,
            'emphasis': emphasis,
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()])
        }
    
    def _analyze_yaml_structure(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze YAML frontmatter structure"""
        return {
            'keys': list(frontmatter.keys()),
            'depth': self._calculate_yaml_depth(frontmatter),
            'has_description': 'description' in frontmatter,
            'has_globs': 'globs' in frontmatter,
            'has_always_apply': 'alwaysApply' in frontmatter
        }
    
    def _calculate_yaml_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of YAML structure"""
        if isinstance(obj, dict):
            return max(current_depth, max(
                self._calculate_yaml_depth(v, current_depth + 1) 
                for v in obj.values()
            ))
        elif isinstance(obj, list):
            return max(current_depth, max(
                self._calculate_yaml_depth(item, current_depth + 1) 
                for item in obj
            ))
        else:
            return current_depth
    
    def _calculate_content_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate content metrics"""
        lines = content.splitlines()
        return {
            'total_chars': len(content),
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'avg_line_length': sum(len(l) for l in lines) / max(len(lines), 1),
            'max_line_length': max(len(l) for l in lines) if lines else 0
        }
    
    def _check_rule_compliance(self, frontmatter: Dict[str, Any], markdown_content: str) -> Dict[str, Any]:
        """Check rule compliance"""
        return {
            'has_description': 'description' in frontmatter,
            'has_globs': 'globs' in frontmatter,
            'has_content': len(markdown_content.strip()) > 0,
            'has_headers': bool(re.findall(r'^#{1,6}\s+', markdown_content, re.MULTILINE)),
            'has_code_blocks': '```' in markdown_content
        }
    
    def _calculate_mdc_complexity(self, model_data: Dict[str, Any]) -> float:
        """Calculate complexity for MDC file"""
        markdown_analysis = model_data['markdown_analysis']
        yaml_structure = model_data['yaml_structure']
        
        complexity = 1.0  # Base complexity
        complexity += markdown_analysis['headers'] * 0.2
        complexity += markdown_analysis['code_blocks'] * 0.5
        complexity += yaml_structure['depth'] * 0.3
        complexity += len(yaml_structure['keys']) * 0.1
        
        return min(10.0, complexity)
    
    def _generate_mdc_structure_hash(self, model_data: Dict[str, Any]) -> str:
        """Generate structure hash for MDC file"""
        structure_elements = {
            'yaml_keys': model_data['yaml_structure']['keys'],
            'markdown_headers': model_data['markdown_analysis']['headers'],
            'code_blocks': model_data['markdown_analysis']['code_blocks']
        }
        return hashlib.sha256(json.dumps(structure_elements, sort_keys=True).encode()).hexdigest()[:16]
    
    def _get_commit_hash(self, file_path: str) -> Optional[str]:
        """Get current commit hash for file"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _create_mdc_basic_model(self, file_path: str, error: str) -> ASTModel:
        """Create basic model for broken MDC files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = ""
        
        model_data = {
            'basic_error': error,
            'file_size': len(content),
            'lines_of_code': len(content.splitlines()),
            'markdown_analysis': {'headers': 0, 'code_blocks': 0, 'lists': 0, 'links': 0, 'emphasis': 0},
            'yaml_structure': {'keys': [], 'depth': 0, 'has_description': False, 'has_globs': False, 'has_always_apply': False}
        }
        
        return ASTModel(
            file_path=file_path,
            file_type='mdc',
            model_type='basic',
            model_data=model_data,
            complexity_score=1.0,
            structure_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
            lines_of_code=len(content.splitlines()),
            created_at=datetime.now().isoformat()
        )


class MarkdownModeler:
    """Modeler for regular Markdown files"""
    
    def model_markdown_file(self, file_path: str) -> ASTModel:
        """Create model for Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            model_data = {
                'markdown_analysis': self._analyze_markdown_content(content),
                'content_metrics': self._calculate_content_metrics(content),
                'lines_of_code': len(content.splitlines()),
                'documentation_quality': self._assess_documentation_quality(content)
            }
            
            complexity_score = self._calculate_markdown_complexity(model_data)
            structure_hash = self._generate_markdown_structure_hash(model_data)
            
            return ASTModel(
                file_path=file_path,
                file_type='markdown',
                model_type='ast',
                model_data=model_data,
                complexity_score=complexity_score,
                structure_hash=structure_hash,
                lines_of_code=model_data['lines_of_code'],
                created_at=datetime.now().isoformat(),
                commit_hash=self._get_commit_hash(file_path)
            )
            
        except Exception as e:
            return self._create_markdown_basic_model(file_path, str(e))
    
    def _analyze_markdown_content(self, content: str) -> Dict[str, Any]:
        """Analyze markdown content structure"""
        lines = content.splitlines()
        
        # Count different markdown elements
        headers = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        code_blocks = len(re.findall(r'```', content))
        lists = len(re.findall(r'^[\s]*[-*+]\s+', content, re.MULTILINE))
        links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        emphasis = len(re.findall(r'\*\*([^*]+)\*\*|\*([^*]+)\*', content))
        tables = len(re.findall(r'\|.*\|', content))
        images = len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content))
        
        return {
            'headers': headers,
            'code_blocks': code_blocks,
            'lists': lists,
            'links': links,
            'emphasis': emphasis,
            'tables': tables,
            'images': images,
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()])
        }
    
    def _calculate_content_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate content metrics"""
        lines = content.splitlines()
        return {
            'total_chars': len(content),
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'avg_line_length': sum(len(l) for l in lines) / max(len(lines), 1),
            'max_line_length': max(len(l) for l in lines) if lines else 0
        }
    
    def _assess_documentation_quality(self, content: str) -> Dict[str, Any]:
        """Assess documentation quality"""
        lines = content.splitlines()
        
        # Check for common documentation patterns
        has_toc = any('table of contents' in line.lower() for line in lines)
        has_examples = '```' in content
        has_links = bool(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        has_headers = bool(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        
        return {
            'has_table_of_contents': has_toc,
            'has_examples': has_examples,
            'has_links': has_links,
            'has_headers': has_headers,
            'structure_score': sum([has_toc, has_examples, has_links, has_headers])
        }
    
    def _calculate_markdown_complexity(self, model_data: Dict[str, Any]) -> float:
        """Calculate complexity for Markdown file"""
        markdown_analysis = model_data['markdown_analysis']
        doc_quality = model_data['documentation_quality']
        
        complexity = 1.0  # Base complexity
        complexity += markdown_analysis['headers'] * 0.2
        complexity += markdown_analysis['code_blocks'] * 0.3
        complexity += markdown_analysis['tables'] * 0.5
        complexity += doc_quality['structure_score'] * 0.2
        
        return min(10.0, complexity)
    
    def _generate_markdown_structure_hash(self, model_data: Dict[str, Any]) -> str:
        """Generate structure hash for Markdown file"""
        structure_elements = {
            'headers': model_data['markdown_analysis']['headers'],
            'code_blocks': model_data['markdown_analysis']['code_blocks'],
            'tables': model_data['markdown_analysis']['tables'],
            'structure_score': model_data['documentation_quality']['structure_score']
        }
        return hashlib.sha256(json.dumps(structure_elements, sort_keys=True).encode()).hexdigest()[:16]
    
    def _get_commit_hash(self, file_path: str) -> Optional[str]:
        """Get current commit hash for file"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _create_markdown_basic_model(self, file_path: str, error: str) -> ASTModel:
        """Create basic model for broken Markdown files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = ""
        
        model_data = {
            'basic_error': error,
            'file_size': len(content),
            'lines_of_code': len(content.splitlines()),
            'markdown_analysis': {'headers': 0, 'code_blocks': 0, 'lists': 0, 'links': 0, 'emphasis': 0, 'tables': 0, 'images': 0},
            'documentation_quality': {'has_table_of_contents': False, 'has_examples': False, 'has_links': False, 'has_headers': False, 'structure_score': 0}
        }
        
        return ASTModel(
            file_path=file_path,
            file_type='markdown',
            model_type='basic',
            model_data=model_data,
            complexity_score=1.0,
            structure_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
            lines_of_code=len(content.splitlines()),
            created_at=datetime.now().isoformat()
        )


class UniversalArtifactModeler:
    """Universal artifact modeler for ALL file types"""
    
    def __init__(self):
        # Use the improved PythonASTModeler that properly extracts semantic information
        self.python_modeler = PythonASTModeler()
        self.mdc_modeler = MDCModeler()
        self.markdown_modeler = MarkdownModeler()
        
    def model_any_file(self, file_path: str) -> ASTModel:
        """Model ANY file type based on extension and content"""
        file_path = str(Path(file_path).resolve())
        
        # Python files
        if file_path.endswith('.py'):
            return self.python_modeler.model_python_file(file_path)
        
        # Markdown variants
        elif file_path.endswith('.mdc'):
            return self.mdc_modeler.model_mdc_file(file_path)
        elif file_path.endswith('.md'):
            return self.markdown_modeler.model_markdown_file(file_path)
        
        # Data formats
        elif file_path.endswith('.json'):
            return self._model_json_file(file_path)
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return self._model_yaml_file(file_path)
        elif file_path.endswith('.xml'):
            return self._model_xml_file(file_path)
        elif file_path.endswith('.sql'):
            return self._model_sql_file(file_path)
        
        # Web technologies
        elif file_path.endswith('.html'):
            return self._model_html_file(file_path)
        elif file_path.endswith('.css'):
            return self._model_css_file(file_path)
        elif file_path.endswith('.js') or file_path.endswith('.ts'):
            return self._model_javascript_file(file_path)
        
        # Infrastructure
        elif file_path.endswith('.tf'):
            return self._model_terraform_file(file_path)
        elif file_path.endswith('.dockerfile'):
            return self._model_dockerfile(file_path)
        elif file_path.endswith('.yml') and 'k8s' in file_path.lower():
            return self._model_kubernetes_file(file_path)
        elif file_path.endswith('.yml') and 'cloudformation' in file_path.lower():
            return self._model_cloudformation_file(file_path)
        
        # Configuration
        elif file_path.endswith('.toml'):
            return self._model_toml_file(file_path)
        elif file_path.endswith('.ini'):
            return self._model_ini_file(file_path)
        elif file_path.endswith('.env'):
            return self._model_env_file(file_path)
        
        # Documentation
        elif file_path.endswith('.rst'):
            return self._model_rst_file(file_path)
        elif file_path.endswith('.txt'):
            return self._model_text_file(file_path)
        
        # Shell scripts
        elif file_path.endswith('.sh') or file_path.endswith('.bash') or file_path.endswith('.zsh'):
            return self._model_shell_file(file_path)
        
        # Unknown - try content-based detection
        else:
            return self._model_unknown_file(file_path)
    
    def _model_json_file(self, file_path: str) -> ASTModel:
        """Model JSON files"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            model_data = {
                "json_type": type(data).__name__,
                "json_size": len(str(data)),
                "json_keys": list(data.keys()) if isinstance(data, dict) else [],
                "json_depth": self._calculate_json_depth(data),
                "json_keys_list": self._extract_json_keys(data)
            }
            
            return ASTModel(
                file_path=file_path,
                file_type="JSON",
                model_type="ast",
                model_data=model_data,
                complexity_score=1.0,
                structure_hash=hashlib.md5(str(data).encode()).hexdigest(),
                lines_of_code=len(str(data).split('\n')),
                created_at=datetime.now().isoformat(),
                commit_hash=None
            )
        except Exception as e:
            return self._create_error_model(file_path, "JSON", str(e))
    
    def _model_yaml_file(self, file_path: str) -> ASTModel:
        """Model YAML files"""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            model_data = {
                "yaml_type": type(data).__name__,
                "yaml_size": len(str(data)),
                "yaml_keys": list(data.keys()) if isinstance(data, dict) else [],
                "yaml_depth": self._calculate_yaml_depth(data),
                "yaml_keys_list": self._extract_yaml_keys(data)
            }
            
            return ASTModel(
                file_path=file_path,
                file_type="YAML",
                model_type="ast",
                model_data=model_data,
                complexity_score=1.0,
                structure_hash=hashlib.md5(str(data).encode()).hexdigest(),
                lines_of_code=len(str(data).split('\n')),
                created_at=datetime.now().isoformat(),
                commit_hash=None
            )
        except Exception as e:
            return self._create_error_model(file_path, "YAML", str(e))
    
    def _model_sql_file(self, file_path: str) -> ASTModel:
        """Model SQL files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic SQL parsing
            statements = [s.strip() for s in content.split(';') if s.strip()]
            tables = re.findall(r'CREATE TABLE (\w+)', content, re.IGNORECASE)
            views = re.findall(r'CREATE VIEW (\w+)', content, re.IGNORECASE)
            functions = re.findall(r'CREATE FUNCTION (\w+)', content, re.IGNORECASE)
            
            model_data = {
                "sql_statements": len(statements),
                "sql_tables": tables,
                "sql_views": views,
                "sql_functions": functions,
                "sql_content": content
            }
            
            return ASTModel(
                file_path=file_path,
                file_type="SQL",
                model_type="ast",
                model_data=model_data,
                complexity_score=float(len(statements)),
                structure_hash=hashlib.md5(content.encode()).hexdigest(),
                lines_of_code=len(content.split('\n')),
                created_at=datetime.now().isoformat(),
                commit_hash=None
            )
        except Exception as e:
            return self._create_error_model(file_path, "SQL", str(e))
    
    def _model_html_file(self, file_path: str) -> ASTModel:
        """Model HTML files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic HTML parsing
            tags = re.findall(r'<(\w+)', content)
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            styles = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
            
            return ASTModel(
                file_path=file_path,
                file_type="HTML",
                lines_of_code=len(content.split('\n')),
                complexity=len(tags),
                imports=[],
                functions=[],
                classes=[],
                variables=tags,
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(tags),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "html_tags": len(tags),
                    "html_scripts": len(scripts),
                    "html_styles": len(styles),
                    "html_forms": len(re.findall(r'<form', content))
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "HTML", str(e))
    
    def _model_css_file(self, file_path: str) -> ASTModel:
        """Model CSS files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic CSS parsing
            rules = re.findall(r'([^{]+)\s*{([^}]+)}', content)
            selectors = [rule[0].strip() for rule in rules]
            properties = re.findall(r'([^:]+):\s*([^;]+);', content)
            
            return ASTModel(
                file_path=file_path,
                file_type="CSS",
                lines_of_code=len(content.split('\n')),
                complexity=len(rules),
                imports=[],
                functions=[],
                classes=selectors,
                variables=properties,
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(rules),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "css_rules": len(rules),
                    "css_selectors": len(selectors),
                    "css_properties": len(properties)
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "CSS", str(e))
    
    def _model_javascript_file(self, file_path: str) -> ASTModel:
        """Model JavaScript/TypeScript files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic JS parsing
            functions = re.findall(r'function\s+(\w+)', content)
            functions.extend(re.findall(r'(\w+)\s*[:=]\s*function', content))
            functions.extend(re.findall(r'(\w+)\s*[:=]\s*\([^)]*\)\s*=>', content))
            
            classes = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            imports.extend(re.findall(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]', content))
            
            return ASTModel(
                file_path=file_path,
                file_type="JAVASCRIPT",
                lines_of_code=len(content.split('\n')),
                complexity=len(functions) + len(classes),
                imports=imports,
                functions=functions,
                classes=classes,
                variables=[],
                dependencies=imports,
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(content.split()),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "js_functions": len(functions),
                    "js_classes": len(classes),
                    "js_imports": len(imports)
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "JAVASCRIPT", str(e))
    
    def _model_terraform_file(self, file_path: str) -> ASTModel:
        """Model Terraform files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic Terraform parsing
            resources = re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', content)
            data_sources = re.findall(r'data\s+"([^"]+)"\s+"([^"]+)"', content)
            variables = re.findall(r'variable\s+"([^"]+)"', content)
            
            return ASTModel(
                file_path=file_path,
                file_type="TERRAFORM",
                lines_of_code=len(content.split('\n')),
                complexity=len(resources) + len(data_sources),
                imports=[],
                functions=[],
                classes=[],
                variables=variables,
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(resources) + len(data_sources),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "tf_resources": len(resources),
                    "tf_data_sources": len(data_sources),
                    "tf_variables": len(variables)
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "TERRAFORM", str(e))
    
    def _model_dockerfile(self, file_path: str) -> ASTModel:
        """Model Dockerfile"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic Dockerfile parsing
            instructions = re.findall(r'^(\w+)', content, re.MULTILINE)
            from_images = re.findall(r'FROM\s+([^\s]+)', content)
            copy_instructions = re.findall(r'COPY\s+([^\s]+)', content)
            
            return ASTModel(
                file_path=file_path,
                file_type="DOCKERFILE",
                lines_of_code=len(content.split('\n')),
                complexity=len(instructions),
                imports=[],
                functions=[],
                classes=[],
                variables=from_images,
                dependencies=from_images,
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(instructions),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "docker_instructions": len(instructions),
                    "docker_from_images": from_images,
                    "docker_copy_files": copy_instructions
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "DOCKERFILE", str(e))
    
    def _model_unknown_file(self, file_path: str) -> ASTModel:
        """Model unknown file types based on content analysis"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Content-based type detection
            file_type = self._detect_file_type(content, file_path)
            
            return ASTModel(
                file_path=file_path,
                file_type=file_type,
                lines_of_code=len(content.split('\n')),
                complexity=1,
                imports=[],
                functions=[],
                classes=[],
                variables=[],
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(content.split()),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "detected_type": file_type,
                    "content_size": len(content),
                    "content_preview": content[:200]
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "UNKNOWN", str(e))
    
    def _model_text_file(self, file_path: str) -> ASTModel:
        """Model text files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            return ASTModel(
                file_path=file_path,
                file_type="TEXT",
                lines_of_code=len(content.split('\n')),
                complexity=1,
                imports=[],
                functions=[],
                classes=[],
                variables=[],
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(content.split()),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "text_size": len(content),
                    "text_lines": len(content.split('\n')),
                    "text_preview": content[:200]
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "TEXT", str(e))
    
    def _model_toml_file(self, file_path: str) -> ASTModel:
        """Model TOML files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic TOML parsing
            sections = re.findall(r'^\[([^\]]+)\]', content, re.MULTILINE)
            keys = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
            
            return ASTModel(
                file_path=file_path,
                file_type="TOML",
                lines_of_code=len(content.split('\n')),
                complexity=len(sections),
                imports=[],
                functions=[],
                classes=sections,
                variables=keys,
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(sections) + len(keys),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "toml_sections": sections,
                    "toml_keys": keys,
                    "toml_size": len(content)
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "TOML", str(e))
    
    def _model_shell_file(self, file_path: str) -> ASTModel:
        """Model shell script files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic shell parsing
            functions = re.findall(r'^(\w+)\s*\(\)', content, re.MULTILINE)
            variables = re.findall(r'^(\w+)=', content, re.MULTILINE)
            commands = re.findall(r'^(\w+)\s+', content, re.MULTILINE)
            
            return ASTModel(
                file_path=file_path,
                file_type="SHELL",
                lines_of_code=len(content.split('\n')),
                complexity=len(functions),
                imports=[],
                functions=functions,
                classes=[],
                variables=variables,
                dependencies=commands,
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(functions) + len(variables),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "shell_functions": functions,
                    "shell_variables": variables,
                    "shell_commands": commands
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "SHELL", str(e))
    
    def _model_xml_file(self, file_path: str) -> ASTModel:
        """Model XML files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic XML parsing
            tags = re.findall(r'<(\w+)', content)
            attributes = re.findall(r'(\w+)="[^"]*"', content)
            
            return ASTModel(
                file_path=file_path,
                file_type="XML",
                lines_of_code=len(content.split('\n')),
                complexity=len(tags),
                imports=[],
                functions=[],
                classes=[],
                variables=tags,
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(tags),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "xml_tags": len(tags),
                    "xml_attributes": len(attributes),
                    "xml_size": len(content)
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "XML", str(e))
    
    def _model_kubernetes_file(self, file_path: str) -> ASTModel:
        """Model Kubernetes YAML files"""
        return self._model_yaml_file(file_path)
    
    def _model_cloudformation_file(self, file_path: str) -> ASTModel:
        """Model CloudFormation YAML files"""
        return self._model_yaml_file(file_path)
    
    def _model_ini_file(self, file_path: str) -> ASTModel:
        """Model INI files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic INI parsing
            sections = re.findall(r'^\[([^\]]+)\]', content, re.MULTILINE)
            keys = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
            
            return ASTModel(
                file_path=file_path,
                file_type="INI",
                lines_of_code=len(content.split('\n')),
                complexity=len(sections),
                imports=[],
                functions=[],
                classes=sections,
                variables=keys,
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(sections) + len(keys),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "ini_sections": sections,
                    "ini_keys": keys,
                    "ini_size": len(content)
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "INI", str(e))
    
    def _model_env_file(self, file_path: str) -> ASTModel:
        """Model environment files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic ENV parsing
            variables = re.findall(r'^(\w+)=', content, re.MULTILINE)
            
            return ASTModel(
                file_path=file_path,
                file_type="ENV",
                lines_of_code=len(content.split('\n')),
                complexity=1,
                imports=[],
                functions=[],
                classes=[],
                variables=variables,
                dependencies=[],
                docstrings=[],
                error_handling=[],
                type_hints=[],
                nesting_depth=1,
                ast_nodes=len(variables),
                has_syntax_errors=False,
                error_messages=[],
                metadata={
                    "env_variables": variables,
                    "env_size": len(content)
                }
            )
        except Exception as e:
            return self._create_error_model(file_path, "ENV", str(e))
    
    def _model_rst_file(self, file_path: str) -> ASTModel:
        """Model RST files"""
        return self._model_text_file(file_path)
    
    def _detect_file_type(self, content: str, file_path: str) -> str:
        """Detect file type based on content and path"""
        path_lower = file_path.lower()
        content_lower = content.lower()
        
        # Infrastructure detection
        if 'kubernetes' in path_lower or 'k8s' in path_lower:
            return "KUBERNETES"
        elif 'cloudformation' in path_lower or 'cfn' in path_lower:
            return "CLOUDFORMATION"
        elif 'dockerfile' in path_lower:
            return "DOCKERFILE"
        elif 'terraform' in path_lower or '.tf' in path_lower:
            return "TERRAFORM"
        
        # Content-based detection
        elif content.startswith('{') or content.startswith('['):
            return "JSON"
        elif '---' in content and 'yaml' in content_lower:
            return "YAML"
        elif '<html' in content_lower or '<!DOCTYPE' in content_lower:
            return "HTML"
        elif 'function' in content_lower and 'var ' in content_lower:
            return "JAVASCRIPT"
        elif 'SELECT' in content.upper() or 'CREATE TABLE' in content.upper():
            return "SQL"
        elif 'FROM' in content.upper() and 'RUN' in content.upper():
            return "DOCKERFILE"
        
        return "TEXT"
    
    def _extract_json_keys(self, data: Any, prefix: str = "") -> List[str]:
        """Extract all keys from JSON data"""
        keys = []
        if isinstance(data, dict):
            for key, value in data.items():
                keys.append(f"{prefix}{key}")
                keys.extend(self._extract_json_keys(value, f"{prefix}{key}."))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                keys.extend(self._extract_json_keys(item, f"{prefix}[{i}]."))
        return keys
    
    def _extract_yaml_keys(self, data: Any, prefix: str = "") -> List[str]:
        """Extract all keys from YAML data"""
        return self._extract_json_keys(data, prefix)
    
    def _calculate_json_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate nesting depth of JSON data"""
        if isinstance(data, dict):
            return max([self._calculate_json_depth(v, current_depth + 1) for v in data.values()], default=current_depth)
        elif isinstance(data, list):
            return max([self._calculate_json_depth(item, current_depth + 1) for item in data], default=current_depth)
        return current_depth
    
    def _calculate_yaml_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate nesting depth of YAML data"""
        return self._calculate_json_depth(data, current_depth)
    
    def _create_error_model(self, file_path: str, file_type: str, error: str) -> ASTModel:
        """Create error model for failed parsing"""
        model_data = {
            "error": error,
            "error_type": "parsing_error",
            "has_syntax_errors": True
        }
        
        return ASTModel(
            file_path=file_path,
            file_type=file_type,
            model_type="error",
            model_data=model_data,
            complexity_score=0.0,
            structure_hash=hashlib.md5(error.encode()).hexdigest(),
            lines_of_code=0,
            created_at=datetime.now().isoformat(),
            commit_hash=None
        )


class ComprehensiveASTModeler:
    """Comprehensive AST modeler for ALL file types"""
    
    def __init__(self, database_path: str = "ast_models.json"):
        self.database_path = database_path
        self.universal_modeler = UniversalArtifactModeler()
        
        # Thread safety
        from threading import Lock
        self.database_lock = Lock()
        self.logger_lock = Lock()
        
        # Load existing database
        self.database = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load existing database"""
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'file_models': {},
            'evolution_patterns': {},
            'consistency_checks': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'total_files': 0,
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def _save_database(self):
        """Save database with frequent commits and thread safety"""
        with self.database_lock:
            self.database['metadata']['last_updated'] = datetime.now().isoformat()
            self.database['metadata']['total_files'] = len(self.database['file_models'])
            
            with open(self.database_path, 'w') as f:
                json.dump(self.database, f, indent=2, default=str)
            
            # Commit to git
            self._commit_changes()
    
    def _log_operation(self, message: str):
        """Thread-safe logging"""
        with self.logger_lock:
            timestamp = datetime.now().isoformat()
            print(f"[{timestamp}] {message}")
    
    def _safe_model_file(self, file_path: str) -> Optional[ASTModel]:
        """Thread-safe file modeling with proper error handling"""
        try:
            model = self.model_file(file_path)
            self._log_operation(f"✅ Modeled: {file_path}")
            return model
        except Exception as e:
            self._log_operation(f"❌ Failed to model {file_path}: {e}")
            return None
    
    def _commit_changes(self):
        """Commit changes to git"""
        try:
            subprocess.run(['git', 'add', self.database_path], check=True)
            subprocess.run(['git', 'commit', '-m', f'Update AST models - {datetime.now().isoformat()}'], check=True)
        except subprocess.CalledProcessError:
            pass  # Git not available or no changes
    
    def model_file(self, file_path: str) -> ASTModel:
        """Model ANY file using universal modeler"""
        file_path = str(Path(file_path).resolve())
        
        # Get model from universal modeler
        model = self.universal_modeler.model_any_file(file_path)
        
        # Store in database
        self.database['file_models'][file_path] = asdict(model)
        
        return model
    
    def model_directory(self, directory_path: str, file_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[ASTModel]:
        """Model ALL files in a directory with universal support"""
        if file_patterns is None:
            # Support ALL file types
            file_patterns = [
                '*.py', '*.mdc', '*.md', '*.json', '*.yaml', '*.yml', 
                '*.xml', '*.sql', '*.html', '*.css', '*.js', '*.ts',
                '*.tf', '*.dockerfile', '*.toml', '*.ini', '*.env',
                '*.rst', '*.txt', '*.sh', '*.bash', '*.zsh'
            ]
        
        if exclude_patterns is None:
            exclude_patterns = ['.venv', 'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache', '.mypy_cache']
        
        models = []
        directory = Path(directory_path)
        
        # Collect all matching files
        files_to_model = []
        for pattern in file_patterns:
            for file_path in directory.rglob(pattern):
                # Check exclusions
                if any(exclude in str(file_path) for exclude in exclude_patterns):
                    continue
                files_to_model.append(file_path)
        
        print(f"🔍 Found {len(files_to_model)} files to model (ALL types)")
        
        # Process in parallel
        lock = Lock()
        results = []
        
        def model_single_file(file_path):
            return self._safe_model_file(str(file_path))
        
        # Use ThreadPoolExecutor for I/O bound operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {executor.submit(model_single_file, file_path): file_path 
                            for file_path in files_to_model}
            
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    results.append(result)
        
        # Save database once after all files are processed
        self._save_database()
        self._log_operation(f"✅ Completed modeling {len(results)} files (ALL types)")
        
        return results
    
    def get_file_model(self, file_path: str) -> Optional[ASTModel]:
        """Get existing model for a file"""
        file_path = str(Path(file_path).resolve())
        if file_path in self.database['file_models']:
            data = self.database['file_models'][file_path]
            return ASTModel(**data)
        return None
    
    def get_similar_files(self, structure_hash: str) -> List[str]:
        """Find files with similar structure"""
        similar_files = []
        for file_path, model_data in self.database['file_models'].items():
            if model_data['structure_hash'] == structure_hash:
                similar_files.append(file_path)
        return similar_files
    
    def get_evolution_patterns(self, file_path: str) -> Optional[EvolutionPattern]:
        """Get evolution patterns for a file"""
        file_path = str(Path(file_path).resolve())
        if file_path in self.database['evolution_patterns']:
            data = self.database['evolution_patterns'][file_path]
            return EvolutionPattern(**data)
        return None
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire project"""
        print("🔍 Analyzing project structure...")
        
        models = self.model_directory(project_path)
        
        # Calculate project statistics
        total_files = len(models)
        total_lines = sum(m.lines_of_code for m in models)
        avg_complexity = sum(m.complexity_score for m in models) / max(total_files, 1)
        
        # File type breakdown
        file_types = {}
        for model in models:
            file_type = model.file_type
            if file_type not in file_types:
                file_types[file_type] = {'count': 0, 'lines': 0, 'complexity': 0}
            file_types[file_type]['count'] += 1
            file_types[file_type]['lines'] += model.lines_of_code
            file_types[file_type]['complexity'] += model.complexity_score
        
        # Calculate averages
        for file_type in file_types:
            count = file_types[file_type]['count']
            file_types[file_type]['avg_lines'] = file_types[file_type]['lines'] / count
            file_types[file_type]['avg_complexity'] = file_types[file_type]['complexity'] / count
        
        analysis = {
            'total_files': total_files,
            'total_lines': total_lines,
            'avg_complexity': avg_complexity,
            'file_types': file_types,
            'models': [asdict(m) for m in models]
        }
        
        print(f"✅ Project analysis complete: {total_files} files, {total_lines} lines")
        return analysis


def main():
    """Main function for testing"""
    print("🧠 Comprehensive AST Modeler")
    print("=" * 50)
    
    modeler = ComprehensiveASTModeler()
    
    # Test with current directory
    analysis = modeler.analyze_project('.')
    
    print(f"\n📊 Project Statistics:")
    print(f"  Total Files: {analysis['total_files']}")
    print(f"  Total Lines: {analysis['total_lines']}")
    print(f"  Avg Complexity: {analysis['avg_complexity']:.2f}")
    
    print(f"\n📁 File Type Breakdown:")
    for file_type, stats in analysis['file_types'].items():
        print(f"  {file_type.upper()}: {stats['count']} files, {stats['avg_lines']:.1f} avg lines, {stats['avg_complexity']:.2f} avg complexity")
    
    print(f"\n✅ AST modeling complete! Database saved to: {modeler.database_path}")


if __name__ == "__main__":
    main() 