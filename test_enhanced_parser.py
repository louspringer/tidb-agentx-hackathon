#!/usr/bin/env python3
"""Test the enhanced parser on files with syntax errors"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from artifact_forge.agents.artifact_parser import ArtifactParser

def test_enhanced_parser():
    """Test enhanced parser on problematic files"""
    parser = ArtifactParser()
    
    # Test files that had issues in the workflow
    test_files = [
        "src/artifact_forge/workflows/basic_workflow.py",
        "src/artifact_forge/agents/artifact_detector.py",
        "comprehensive_ast_modeler.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n🔍 **TESTING ENHANCED PARSER ON: {test_file}**")
            
            # First try standard AST parsing
            try:
                import ast
                with open(test_file, 'r') as f:
                    content = f.read()
                ast.parse(content)
                print(f"✅ Standard AST parsing: SUCCESS")
            except SyntaxError as e:
                print(f"❌ Standard AST parsing: FAILED - {e}")
            
            # Now test enhanced parser
            parsed = parser.parse_artifact(test_file, "python")
            print(f"🔧 Enhanced parser: AST Parse Successful: {parsed.parsed_data.get('ast_parse_successful', False)}")
            print(f"📊 Functions found: {len(parsed.parsed_data.get('functions', []))}")
            print(f"📊 Classes found: {len(parsed.parsed_data.get('classes', []))}")
            
            if parsed.block_analysis:
                print(f"🔍 Blocks found: {parsed.block_analysis.get('total_blocks', 0)}")
                print(f"🔍 Block types: {parsed.block_analysis.get('block_types', {})}")
                print(f"⚠️  Indentation issues: {len(parsed.block_analysis.get('indentation_issues', []))}")
            
            if parsed.parsing_errors:
                print(f"❌ Parsing errors: {len(parsed.parsing_errors)}")
        else:
            print(f"⚠️  File not found: {test_file}")

if __name__ == "__main__":
    test_enhanced_parser() 