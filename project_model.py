#!/usr/bin/env python3
"""
Model-Driven Tool Glue Layer
Intelligent tool selection and orchestration across domains
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class DomainConfig:
    """Configuration for a specific domain"""
    name: str
    linter: str
    validator: Optional[str] = None
    formatter: Optional[str] = None
    patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    content_indicators: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = []
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.content_indicators is None:
            self.content_indicators = []

@dataclass
class FileAnalysis:
    """Analysis of a file's domain and tooling needs"""
    filepath: str
    detected_domain: str
    confidence: float
    recommended_tools: List[str]
    validation_commands: List[str]

class ProjectModel:
    """Model-driven tool orchestration"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.domains = self._initialize_domains()
        self.file_cache: Dict[str, FileAnalysis] = {}
        
    def _initialize_domains(self) -> Dict[str, DomainConfig]:
        """Initialize domain configurations"""
        return {
            "cloudformation": DomainConfig(
                name="cloudformation",
                linter="cfn-lint",
                validator="aws-cloudformation",
                patterns=["*.template.yaml", "models/*.yaml", "*cloudformation*.yaml"],
                content_indicators=["!Sub", "!Ref", "!GetAtt", "AWS::", "Type: 'AWS::"]
            ),
            "python": DomainConfig(
                name="python", 
                linter="flake8",
                formatter="black",
                patterns=["*.py"],
                exclude_patterns=["__pycache__/*", "*.pyc"],
                content_indicators=["import ", "def ", "class ", "#!/usr/bin/env python"]
            ),
            "yaml": DomainConfig(
                name="yaml",
                linter="yamllint",
                patterns=["*.yaml", "*.yml"],
                exclude_patterns=["models/*.yaml", "*.template.yaml"],
                content_indicators=["---", "key: value"]
            ),
            "yaml_infrastructure": DomainConfig(
                name="yaml_infrastructure",
                linter="cfn-lint",
                validator="aws-cloudformation",
                patterns=["*cloudformation*.yaml", "*infrastructure*.yaml", "*aws*.yaml", "models/*.yaml"],
                content_indicators=["!Sub", "!Ref", "!GetAtt", "AWS::", "Type: 'AWS::"]
            ),
            "yaml_config": DomainConfig(
                name="yaml_config",
                linter="yamllint",
                validator="jsonschema",
                patterns=["config*.yaml", "settings*.yaml", "*.config.yaml"],
                content_indicators=["config:", "settings:", "environment:", "features:"]
            ),
            "yaml_cicd": DomainConfig(
                name="yaml_cicd",
                linter="actionlint",
                validator="gitlab-ci-lint",
                patterns=[".github/*.yaml", ".gitlab-ci.yml", "*.workflow.yaml", "azure-pipelines*.yml"],
                content_indicators=["on:", "jobs:", "steps:", "pipeline:", "stages:"]
            ),
            "yaml_kubernetes": DomainConfig(
                name="yaml_kubernetes",
                linter="kubectl",
                validator="kubeval",
                patterns=["k8s/*.yaml", "kubernetes/*.yaml", "*.k8s.yaml"],
                content_indicators=["apiVersion:", "kind:", "metadata:", "spec:"]
            ),
            "security": DomainConfig(
                name="security",
                linter="bandit",
                validator="detect-secrets",
                patterns=["**/*"],
                content_indicators=["password", "secret", "key", "token", "credential"]
            ),
            "bash": DomainConfig(
                name="bash",
                linter="shellcheck",
                patterns=["*.sh", "*.bash"],
                content_indicators=["#!/bin/bash", "#!/bin/sh", "export ", "source "]
            )
        }
    
    def analyze_file(self, filepath: str) -> FileAnalysis:
        """Analyze a file to determine its domain and tooling needs"""
        path = Path(filepath)
        
        # Check file extension patterns
        domain_scores = {}
        for domain_name, config in self.domains.items():
            score = 0.0
            
            # Pattern matching
            if config.patterns:
                for pattern in config.patterns:
                    if path.match(pattern):
                        score += 0.4
                        break
            
            # Content analysis
            if config.content_indicators:
                try:
                    content = path.read_text()
                    for indicator in config.content_indicators:
                        if indicator in content:
                            score += 0.3
                            break
                except:
                    pass
            
            # Exclusion check
            if config.exclude_patterns:
                for exclude_pattern in config.exclude_patterns:
                    if path.match(exclude_pattern):
                        score = 0.0
                        break
            
            domain_scores[domain_name] = score
        
        # Find best domain
        best_domain = max(domain_scores.items(), key=lambda x: x[1])
        domain_name, confidence = best_domain
        
        # Generate tool recommendations
        config = self.domains[domain_name]
        tools = [config.linter]
        if config.validator:
            tools.append(config.validator)
        if config.formatter:
            tools.append(config.formatter)
        
        # Generate validation commands
        commands = []
        if config.linter:
            commands.append(f"{config.linter} {filepath}")
        if config.validator:
            commands.append(f"{config.validator} {filepath}")
        
        return FileAnalysis(
            filepath=filepath,
            detected_domain=domain_name,
            confidence=confidence,
            recommended_tools=tools,
            validation_commands=commands
        )
    
    def validate_file(self, filepath: str) -> Dict:
        """Validate a file using the appropriate tools"""
        analysis = self.analyze_file(filepath)
        results = {
            "file": filepath,
            "domain": analysis.detected_domain,
            "confidence": analysis.confidence,
            "tools_used": [],
            "errors": [],
            "warnings": []
        }
        
        for command in analysis.validation_commands:
            try:
                result: subprocess.CompletedProcess[str] = subprocess.run(
                    command.split(), 
                    capture_output=True, 
                    text=True, 
                    cwd=self.project_root
                )
                results["tools_used"].append(command.split()[0])
                
                if result.returncode != 0:
                    results["errors"].append({
                        "tool": command.split()[0],
                        "output": result.stderr
                    })
                elif result.stdout.strip():
                    results["warnings"].append({
                        "tool": command.split()[0], 
                        "output": result.stdout
                    })
                    
            except FileNotFoundError:
                results["errors"].append({
                    "tool": command.split()[0],
                    "output": f"Tool not found: {command.split()[0]}"
                })
        
        return results
    
    def validate_project(self) -> Dict:
        """Validate entire project using model-driven tool selection"""
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                all_files.append(os.path.join(root, file))
        
        results = {
            "project": str(self.project_root),
            "files_analyzed": len(all_files),
            "domains_found": set(),
            "validation_results": []
        }
        
        for filepath in all_files:
            file_result = self.validate_file(filepath)
            results["validation_results"].append(file_result)
            results["domains_found"].add(file_result["domain"])
        
        results["domains_found"] = list(results["domains_found"])
        return results
    
    def generate_tool_config(self) -> Dict:
        """Generate tool configurations based on project model"""
        config = {
            "yamllint": {
                "extends": "default",
                "ignore": []
            },
            "pre-commit": {
                "repos": []
            }
        }
        
        # Add exclusions for YAML linter
        for domain_name, domain_config in self.domains.items():
            if domain_name != "yaml" and domain_config.exclude_patterns:
                config["yamllint"]["ignore"].extend(domain_config.exclude_patterns)
        
        return config

def main():
    """Test the model-driven tool orchestration"""
    model = ProjectModel()
    
    # Test with our CloudFormation file
    result = model.validate_file("models/Openflow-Playground.yaml")
    print("File Analysis:")
    print(json.dumps(result, indent=2))
    
    # Generate tool config
    config = model.generate_tool_config()
    print("\nGenerated Tool Config:")
    print(json.dumps(config, indent=2))

if __name__ == "__main__":
    main() 