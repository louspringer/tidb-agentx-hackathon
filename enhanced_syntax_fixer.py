#!/usr/bin/env python3
"""
Enhanced Syntax Fixer using ArtifactForge
Systematically fixes all syntax errors to achieve 100% test pass rate
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.artifact_forge.agents.artifact_detector import ArtifactDetector
from src.artifact_forge.agents.artifact_parser import ArtifactParser
from src.artifact_forge.agents.artifact_optimizer import ArtifactOptimizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SyntaxFixResult:
    """Result of a syntax fix operation"""
    file_path: str
    success: bool
    error_message: Optional[str] = None
    blocks_fixed: int = 0
    lines_fixed: int = 0
    original_ast_parse: bool = False
    final_ast_parse: bool = False

class EnhancedSyntaxFixer:
    """Enhanced syntax fixer using ArtifactForge components"""
    
    def __init__(self):
        self.detector = ArtifactDetector()
        self.parser = ArtifactParser()
        self.optimizer = ArtifactOptimizer()
        self.fix_results = []
    
    def fix_all_syntax_errors(self, root_path: str = ".") -> List[SyntaxFixResult]:
        """Fix all syntax errors in the codebase"""
        logger.info("🔧 **ENHANCED SYNTAX FIXER STARTING**")
        logger.info("=" * 50)
        
        # Step 1: Detect all Python artifacts
        logger.info("🔍 **STEP 1: DETECTING PYTHON ARTIFACTS**")
        artifacts = self.detector.detect_artifacts(root_path)
        python_artifacts = [a for a in artifacts if a.artifact_type == 'python']
        logger.info(f"  Found {len(python_artifacts)} Python artifacts")
        
        # Step 2: Identify files with syntax errors
        logger.info("📝 **STEP 2: IDENTIFYING SYNTAX ERRORS**")
        problematic_files = []
        
        for artifact in python_artifacts:
            try:
                # Test if file parses correctly
                with open(artifact.path, 'r') as f:
                    content = f.read()
                ast.parse(content)
                logger.info(f"  ✅ {artifact.path}: No syntax errors")
            except SyntaxError as e:
                logger.warning(f"  ❌ {artifact.path}: {e}")
                problematic_files.append(artifact.path)
            except Exception as e:
                logger.error(f"  ⚠️  {artifact.path}: {e}")
        
        logger.info(f"  Found {len(problematic_files)} files with syntax errors")
        
        # Step 3: Fix each problematic file
        logger.info("🔧 **STEP 3: APPLYING INTELLIGENT FIXES**")
        
        for file_path in problematic_files:
            fix_result = self._fix_file_syntax(file_path)
            self.fix_results.append(fix_result)
            
            if fix_result.success:
                logger.info(f"  ✅ {file_path}: Fixed successfully")
            else:
                logger.error(f"  ❌ {file_path}: {fix_result.error_message}")
        
        # Step 4: Validate all fixes
        logger.info("✅ **STEP 4: VALIDATING FIXES**")
        self._validate_all_fixes()
        
        return self.fix_results
    
    def _fix_file_syntax(self, file_path: str) -> SyntaxFixResult:
        """Fix syntax errors in a single file using enhanced parser"""
        try:
            # Test original AST parsing
            original_ast_parse = False
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                ast.parse(content)
                original_ast_parse = True
            except SyntaxError:
                original_ast_parse = False
            
            # Use enhanced parser to get block analysis
            parsed = self.parser.parse_artifact(file_path, "python")
            
            if not parsed.block_analysis:
                return SyntaxFixResult(
                    file_path=file_path,
                    success=False,
                    error_message="No block analysis available",
                    original_ast_parse=original_ast_parse
                )
            
            # Apply intelligent fixes based on block analysis
            blocks_fixed = 0
            lines_fixed = 0
            
            block_analysis = parsed.block_analysis
            blocks = block_analysis.get('blocks', [])
            indentation_issues = block_analysis.get('indentation_issues', [])
            
            logger.info(f"  Analyzing {file_path}: {len(blocks)} blocks, {len(indentation_issues)} indentation issues")
            
            if indentation_issues:
                # Fix indentation issues
                fix_success = self._fix_indentation_issues(file_path, indentation_issues)
                if fix_success:
                    blocks_fixed = len(blocks)
                    lines_fixed = len(indentation_issues)
                    logger.info(f"  Fixed {lines_fixed} indentation issues in {blocks_fixed} blocks")
            
            # Test final AST parsing
            final_ast_parse = False
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                ast.parse(content)
                final_ast_parse = True
                logger.info(f"  ✅ {file_path}: Now parses successfully")
            except SyntaxError as e:
                final_ast_parse = False
                logger.warning(f"  ❌ {file_path}: Still has syntax errors: {e}")
            
            return SyntaxFixResult(
                file_path=file_path,
                success=final_ast_parse,
                error_message=None if final_ast_parse else f"Still has syntax errors after fix attempt",
                blocks_fixed=blocks_fixed,
                lines_fixed=lines_fixed,
                original_ast_parse=original_ast_parse,
                final_ast_parse=final_ast_parse
            )
            
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            return SyntaxFixResult(
                file_path=file_path,
                success=False,
                error_message=str(e)
            )
    
    def _fix_indentation_issues(self, file_path: str, issues: List[Dict[str, Any]]) -> bool:
        """Fix indentation issues in a file"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Group issues by line number
            line_issues = {}
            for issue in issues:
                line_num = issue['line']
                if line_num not in line_issues:
                    line_issues[line_num] = []
                line_issues[line_num].append(issue)
            
            # Track changes
            changes_made = False
            
            # Fix each line with issues
            for line_num, line_issues_list in line_issues.items():
                if line_num <= len(lines):
                    line_idx = line_num - 1  # Convert to 0-based
                    line = lines[line_idx]
                    
                    # Fix indentation
                    if line.strip() and not line.startswith('#'):
                        stripped = line.strip()
                        current_indent = len(line) - len(line.lstrip())
                        
                        # Determine proper indentation level
                        # Look at surrounding context to determine correct indentation
                        proper_indent = self._determine_proper_indentation(lines, line_idx)
                        
                        if proper_indent is not None and proper_indent != current_indent:
                            # Apply the fix
                            new_line = ' ' * proper_indent + stripped + '\n'
                            lines[line_idx] = new_line
                            changes_made = True
                            logger.info(f"    Fixed line {line_num}: {current_indent} -> {proper_indent} spaces")
            
            # Write back the fixed content
            if changes_made:
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                logger.info(f"  ✅ Applied {len(line_issues)} indentation fixes to {file_path}")
                return True
            else:
                logger.info(f"  ⚠️  No indentation fixes applied to {file_path}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to fix indentation for {file_path}: {e}")
            return False
    
    def _determine_proper_indentation(self, lines: List[str], line_idx: int) -> Optional[int]:
        """Determine the proper indentation level for a line based on context"""
        try:
            line = lines[line_idx]
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                return None
            
            # Look at the previous non-empty line to determine context
            prev_line_idx = line_idx - 1
            while prev_line_idx >= 0:
                prev_line = lines[prev_line_idx].strip()
                if prev_line and not prev_line.startswith('#'):
                    break
                prev_line_idx -= 1
            
            if prev_line_idx < 0:
                # First non-empty line, should be at level 0
                return 0
            
            prev_line = lines[prev_line_idx]
            prev_indent = len(prev_line) - len(prev_line.lstrip())
            
            # Determine indentation based on context
            if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
                # New block starts, should be at same level as previous
                return prev_indent
            elif stripped.startswith(('elif ', 'else:', 'except', 'finally:')):
                # Control flow continuation, same level as previous
                return prev_indent
            elif stripped.endswith(':'):
                # Block start, increase indentation
                return prev_indent + 4
            elif prev_line.strip().endswith(':'):
                # Inside a block, increase indentation
                return prev_indent + 4
            else:
                # Regular line, same level as previous
                return prev_indent
                
        except Exception as e:
            logger.error(f"Error determining indentation: {e}")
            return None
    
    def _validate_all_fixes(self):
        """Validate that all fixes were successful"""
        logger.info("🔍 **VALIDATING ALL FIXES**")
        
        total_files = len(self.fix_results)
        successful_fixes = len([r for r in self.fix_results if r.success])
        failed_fixes = total_files - successful_fixes
        
        logger.info(f"  Total files processed: {total_files}")
        logger.info(f"  Successful fixes: {successful_fixes}")
        logger.info(f"  Failed fixes: {failed_fixes}")
        
        if failed_fixes > 0:
            logger.warning("  ⚠️  Some files still have syntax errors:")
            for result in self.fix_results:
                if not result.success:
                    logger.warning(f"    ❌ {result.file_path}: {result.error_message}")
        
        # Final validation: run all tests
        logger.info("🧪 **RUNNING FINAL TEST VALIDATION**")
        self._run_test_validation()
    
    def _run_test_validation(self):
        """Run tests to validate the fixes"""
        try:
            import subprocess
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("  ✅ All tests passing!")
            else:
                logger.warning(f"  ⚠️  Some tests still failing: {result.stderr}")
                
        except Exception as e:
            logger.error(f"  ❌ Test validation failed: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of the fix operation"""
        total_files = len(self.fix_results)
        successful_fixes = len([r for r in self.fix_results if r.success])
        failed_fixes = total_files - successful_fixes
        
        total_blocks_fixed = sum(r.blocks_fixed for r in self.fix_results)
        total_lines_fixed = sum(r.lines_fixed for r in self.fix_results)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_files_processed': total_files,
            'successful_fixes': successful_fixes,
            'failed_fixes': failed_fixes,
            'success_rate': successful_fixes / total_files if total_files > 0 else 0,
            'total_blocks_fixed': total_blocks_fixed,
            'total_lines_fixed': total_lines_fixed,
            'fix_results': [
                {
                    'file_path': r.file_path,
                    'success': r.success,
                    'error_message': r.error_message,
                    'blocks_fixed': r.blocks_fixed,
                    'lines_fixed': r.lines_fixed,
                    'original_ast_parse': r.original_ast_parse,
                    'final_ast_parse': r.final_ast_parse
                }
                for r in self.fix_results
            ]
        }

def main():
    """Run the enhanced syntax fixer"""
    print("🚀 **ENHANCED SYNTAX FIXER**")
    print("Goal: Achieve 100% test pass rate")
    print("=" * 50)
    
    fixer = EnhancedSyntaxFixer()
    results = fixer.fix_all_syntax_errors(".")
    
    # Generate and display report
    report = fixer.generate_report()
    
    print(f"\n📊 **FIX OPERATION REPORT**")
    print(f"Total files processed: {report['total_files_processed']}")
    print(f"Successful fixes: {report['successful_fixes']}")
    print(f"Failed fixes: {report['failed_fixes']}")
    print(f"Success rate: {report['success_rate']:.1%}")
    print(f"Total blocks fixed: {report['total_blocks_fixed']}")
    print(f"Total lines fixed: {report['total_lines_fixed']}")
    
    if report['success_rate'] == 1.0:
        print(f"\n🎉 **SUCCESS! 100% SYNTAX FIX RATE ACHIEVED!**")
    else:
        print(f"\n⚠️  **PARTIAL SUCCESS: {report['success_rate']:.1%} FIX RATE**")
    
    # Save detailed report
    import json
    with open('enhanced_syntax_fix_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: enhanced_syntax_fix_report.json")

if __name__ == "__main__":
    main() 