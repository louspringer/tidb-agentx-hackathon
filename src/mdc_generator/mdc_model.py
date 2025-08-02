#!/usr/bin/env python3
"""
MDC File Model and Generator
Uses standard Python libraries to model and generate .mdc files
"""

import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

@dataclass
class MDCFrontmatter:
    """Model for MDC file YAML frontmatter"""
    description: str
    globs: List[str]
    always_apply: bool = True
    
    def to_yaml(self) -> str:
        """Convert to YAML string"""
        data = {
            "description": self.description,
            "globs": self.globs,
            "alwaysApply": self.always_apply
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

@dataclass
class MDCFile:
    """Complete MDC file model"""
    frontmatter: MDCFrontmatter
    content: str
    file_path: Optional[Path] = None
    
    def to_mdc_content(self) -> str:
        """Generate complete .mdc file content"""
        yaml_content = self.frontmatter.to_yaml()
        return f"---\n{yaml_content}---\n\n{self.content}"
    
    def save(self, file_path: Optional[Path] = None) -> None:
        """Save .mdc file"""
        target_path = file_path or self.file_path
        if not target_path:
            raise ValueError("No file path specified")
            
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, 'w') as f:
            f.write(self.to_mdc_content())
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'MDCFile':
        """Load .mdc file from disk"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse YAML frontmatter
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            raise ValueError(f"Invalid .mdc file: {file_path}")
        
        # Find frontmatter end
        frontmatter_end = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end is None:
            raise ValueError(f"Invalid .mdc file structure: {file_path}")
        
        # Extract frontmatter
        frontmatter_text = '\n'.join(lines[1:frontmatter_end])
        frontmatter_data = yaml.safe_load(frontmatter_text)
        
        # Extract content
        content_lines = lines[frontmatter_end + 1:]
        content = '\n'.join(content_lines)
        
        # Create frontmatter object
        frontmatter = MDCFrontmatter(
            description=frontmatter_data.get('description', ''),
            globs=frontmatter_data.get('globs', []),
            always_apply=frontmatter_data.get('alwaysApply', True)
        )
        
        return cls(
            frontmatter=frontmatter,
            content=content,
            file_path=file_path
        )
    
    @classmethod
    def create_rule(cls, 
                   description: str,
                   globs: List[str],
                   content: str,
                   file_path: Optional[Path] = None,
                   always_apply: bool = True) -> 'MDCFile':
        """Create a new MDC rule file"""
        frontmatter = MDCFrontmatter(
            description=description,
            globs=globs,
            always_apply=always_apply
        )
        
        return cls(
            frontmatter=frontmatter,
            content=content,
            file_path=file_path
        )

class MDCGenerator:
    """Generator for MDC files"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.rules_dir = base_dir / ".cursor" / "rules"
    
    def generate_all_rules(self) -> None:
        """Generate all standard .mdc rules"""
        rules = self._get_standard_rules()
        
        for rule_name, rule_data in rules.items():
            file_path = self.rules_dir / f"{rule_name}.mdc"
            mdc_file = MDCFile.create_rule(
                description=rule_data["description"],
                globs=rule_data["globs"],
                content=rule_data["content"],
                file_path=file_path,
                always_apply=rule_data.get("always_apply", True)
            )
            mdc_file.save()
            print(f"Generated: {file_path}")
    
    def _get_standard_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get standard rule definitions"""
        return {
            "deterministic-editing": {
                "description": "Use deterministic tools for file editing",
                "globs": ["**/*.yaml", "**/*.yml", "**/*.json", "**/*.toml", "**/*.ini", "**/*.cfg", "**/*.mdc", "**/*.py", "**/*.xml", "**/*.properties", "**/*.env"],
                "always_apply": True,
                "content": """# Deterministic File Editing

## BANNED: Stochastic/Fuzzy Editors
- NEVER use `edit_file` for structured files
- NEVER use fuzzy editing tools
- NEVER use tools that can introduce random formatting

## REQUIRED: Deterministic Tools

### YAML Files
- Use `ruamel.yaml` for parsing and serializing
- Use `PyYAML` with schema validation
- Use `search_replace` with exact string matching

### JSON Files  
- Use `json` library with proper formatting
- Use `orjson` for performance
- Use `pydantic` for validation

### Python Files
- Use `ast` for structural edits
- Use `libcst` for code transformations
- Use `black` for formatting

### MDC Files
- Parse YAML frontmatter with `ruamel.yaml`
- Handle markdown content separately
- Use exact string replacement

### Other Formats
- TOML: Use `tomlkit` or `tomli`
- INI: Use `configparser`
- Markdown: Use `markdown-it-py` or `mistune`

## Validation Steps:
- [ ] Used appropriate library for file type
- [ ] Preserved original structure and formatting
- [ ] Validated syntax after editing
- [ ] Used exact string matching for replacements
- [ ] No random formatting changes introduced

## Remember:
If you don't have a deterministic tool for a format, acknowledge the limitation and use the best available approach.
Always validate file structure after editing."""
            },
            "security": {
                "description": "Security guidelines and credential management",
                "globs": ["**/*"],
                "always_apply": True,
                "content": """# Security Guidelines

## NEVER Hardcode These:
- API keys, tokens, secrets, passwords
- AWS access keys, private keys, certificates  
- OAuth client IDs, client secrets, access tokens
- Database connection strings with real credentials
- Account-specific URLs, UUIDs, or identifiers
- Real organization names, account IDs, or resource names

## ALWAYS Use These Instead:
- Environment variables: `$API_KEY`
- Placeholder values: `YOUR_API_KEY`, `YOUR_SECRET`
- Parameter stores or secrets managers
- Configuration files with placeholders

## Validation Checklist:
- [ ] No hardcoded credentials in code
- [ ] No real values in examples or documentation
- [ ] All sensitive parameters are required (no defaults)
- [ ] Placeholder values are clearly marked
- [ ] Security warnings in documentation
- [ ] Configuration is parameterized

## File Types to Check:
- YAML/JSON config files
- Shell scripts
- Python files
- Documentation (README, MD files)
- Environment files
- Infrastructure templates

## Remember:
If you see hardcoded credentials, FIX THEM IMMEDIATELY.
If you're not sure, DON'T HARDCODE IT.
Treat every codebase as if it will be shared publicly."""
            },
            "yaml-type-specific": {
                "description": "YAML file type-specific rules and validation strategies",
                "globs": ["**/*.yaml", "**/*.yml"],
                "always_apply": True,
                "content": """# YAML File Type-Specific Rules

## Core Principle: Heuristic Evaluation Over Enumeration

**When encountering YAML files, evaluate their purpose and apply appropriate rules rather than trying to predict every possible format quirk.**

## Evaluation Strategy

### 1. File Purpose Detection
**Ask yourself: "What is this YAML file trying to accomplish?"**

- **Infrastructure/CloudFormation**: AWS resources, CloudFormation templates
- **Configuration**: App settings, environment configs, feature flags
- **CI/CD**: GitHub Actions, GitLab CI, Azure Pipelines, Jenkins
- **Container Orchestration**: Kubernetes, Docker Compose, Helm charts
- **Application Config**: App-specific settings, database configs
- **Schema/API**: OpenAPI specs, GraphQL schemas, data models

### 2. Tool Selection by Purpose
**Choose validation tools based on the file's purpose, not just its extension:**

```bash
# Infrastructure files
cfn-lint *.yaml                    # CloudFormation
kubectl validate -f *.yaml         # Kubernetes
docker-compose config              # Docker Compose

# Configuration files
yamllint *.yaml                    # General YAML
jsonschema -i schema.json *.yaml   # Schema validation

# CI/CD files
# GitHub Actions: Built-in validation
# GitLab CI: gitlab-ci-lint
# Azure Pipelines: az pipelines validate
```

### 3. When You Hit a New YAML Quirk

**Follow this heuristic process:**

1. **Identify the quirk**: What's different about this YAML format?
2. **Determine the purpose**: What is this file trying to accomplish?
3. **Find the right tool**: What tool understands this format?
4. **Apply appropriate validation**: Use domain-specific tools, not generic YAML linters
5. **Document the pattern**: Add to this rule for future reference

### 4. Common YAML Quirks and Solutions

#### CloudFormation Intrinsic Functions
**Problem**: Generic YAML linters flag `!Ref`, `!Sub`, `!GetAtt` as errors
**Solution**: Use `cfn-lint` instead of generic YAML validators

#### Kubernetes Custom Resources
**Problem**: Generic validators don't understand CRDs
**Solution**: Use `kubectl validate` with proper API server

#### GitHub Actions Context
**Problem**: Generic YAML linters don't understand `${{ }}` expressions
**Solution**: Use GitHub's built-in validation or `actionlint`

#### Helm Templates
**Problem**: Generic linters flag `{{ }}` as invalid YAML
**Solution**: Use `helm template --validate` or `helm lint`

#### Ansible Playbooks
**Problem**: Generic linters don't understand Ansible-specific syntax
**Solution**: Use `ansible-lint` for playbook validation

## Universal YAML Principles

### Formatting Standards
- Use 2-space indentation (never tabs)
- Use consistent quoting (prefer unquoted unless needed)
- Use explicit `null` values when required
- Use YAML anchors and aliases for DRY principles

### Security Practices
- Never hardcode secrets or credentials
- Use environment variables or secret management
- Validate all external inputs
- Follow principle of least privilege

### Validation Strategy
1. **Detect file purpose** based on path, content, and context
2. **Choose appropriate tools** for that purpose
3. **Apply domain-specific validation** rather than generic YAML linting
4. **Check security and best practices** for that domain
5. **Document new patterns** when discovered

## When You Encounter New YAML Formats

**Remember: The goal is not to predict every quirk, but to have a principled approach for handling them.**

1. **Don't panic** - YAML quirks are common and expected
2. **Identify the purpose** - What domain does this YAML serve?
3. **Find the right tool** - Use domain-specific validators
4. **Apply appropriate rules** - Don't force generic YAML linting
5. **Document the pattern** - Add to this rule for future reference

**The principle: Use the right tool for the job, not a generic tool for everything.**"""
            }
        }
    
    def validate_mdc_file(self, file_path: Path) -> bool:
        """Validate a single .mdc file"""
        try:
            mdc_file = MDCFile.from_file(file_path)
            return True
        except Exception as e:
            print(f"Validation failed for {file_path}: {e}")
            return False
    
    def validate_all_mdc_files(self) -> Dict[Path, bool]:
        """Validate all .mdc files in the project"""
        results = {}
        for mdc_file in self.base_dir.rglob("*.mdc"):
            results[mdc_file] = self.validate_mdc_file(mdc_file)
        return results

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MDC File Generator and Validator")
    parser.add_argument("--generate", action="store_true", help="Generate standard rules")
    parser.add_argument("--validate", action="store_true", help="Validate all .mdc files")
    parser.add_argument("--base-dir", type=Path, default=Path("."), help="Base directory")
    
    args = parser.parse_args()
    
    generator = MDCGenerator(args.base_dir)
    
    if args.generate:
        print("Generating standard .mdc rules...")
        generator.generate_all_rules()
        print("Generation complete!")
    
    if args.validate:
        print("Validating all .mdc files...")
        results = generator.validate_all_mdc_files()
        
        valid_files = [f for f, valid in results.items() if valid]
        invalid_files = [f for f, valid in results.items() if not valid]
        
        print(f"Valid files: {len(valid_files)}")
        print(f"Invalid files: {len(invalid_files)}")
        
        if invalid_files:
            print("\nInvalid files:")
            for file in invalid_files:
                print(f"  - {file}")
        
        if not invalid_files:
            print("All .mdc files are valid!")

if __name__ == "__main__":
    main() 