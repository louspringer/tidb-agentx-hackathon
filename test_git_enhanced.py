#!/usr/bin/env python3
"""
Test Git-Enhanced AST Fixer
Demonstrates the Git-enhanced approach with files that have Git history
"""

from git_enhanced_ast_fixer import GitEnhancedASTFixer
from pathlib import Path


def test_git_enhanced_fixer():
    """Test the Git-enhanced AST fixer with files that have Git history"""
    print("🧪 Testing Git-Enhanced AST Fixer")
    print("=" * 50)
    
    fixer = GitEnhancedASTFixer()
    
    # Test with files that have Git history
    test_files = [
        'scripts/mdc-linter.py',  # This has Git history
        'broken_python_interpreter.py',  # This should have Git history
        'semantic_reconstructor.py'  # This should have Git history
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Testing Git-enhanced fixing: {file_path}")
            
            # Check if file has Git history
            import subprocess
            result = subprocess.run(
                ['git', 'log', '--oneline', '--follow', '--', file_path],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"  ✅ File has Git history")
                
                # Test the Git-enhanced fixer
                fixed_content = fixer.fix_file_with_git_history(file_path)
                
                if fixed_content:
                    print(f"  ✅ Git-enhanced fixing completed")
                    
                    # Test if it's valid Python
                    try:
                        import ast
                        ast.parse(fixed_content)
                        print(f"  ✅ Fixed content is valid Python")
                    except Exception as e:
                        print(f"  ⚠️  Fixed content still has issues: {e}")
                else:
                    print(f"  ❌ Git-enhanced fixing failed")
            else:
                print(f"  ⚠️  File has no Git history")
    
    # Cleanup
    fixer.cleanup_temp_dir()


if __name__ == "__main__":
    test_git_enhanced_fixer() 