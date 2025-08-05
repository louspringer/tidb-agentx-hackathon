#!/usr/bin/env python3
"""
Generate Projected Artifacts: Actually create files from the model

This script generates projected artifacts and saves them to a directory
so you can see the actual files that are created from the model.
"""

import json
import os
from pathlib import Path
from simple_projection_test import load_complete_model, get_file_nodes, project_file_simple


def generate_projected_artifacts():
    """Generate projected artifacts and save them to files."""
    print("🚀 Generating Projected Artifacts")
    print("=" * 60)
    
    # Load the complete model
    model = load_complete_model()
    
    # Create output directory
    output_dir = Path("projected_artifacts")
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating projected artifacts in: {output_dir}")
    
    # Test files to project
    test_files = [
        "pyproject.toml",
        "src/streamlit/openflow_quickstart_app.py", 
        "src/security_first/input_validator.py",
        "README.md",
        "Makefile"
    ]
    
    generated_files = []
    
    for file_path in test_files:
        if not Path(file_path).exists():
            print(f"❌ Original file not found: {file_path}")
            continue
        
        # Get nodes for this file
        nodes = get_file_nodes(model, file_path)
        if not nodes:
            print(f"❌ No nodes found for: {file_path}")
            continue
        
        print(f"\n🔍 Projecting: {file_path} ({len(nodes)} nodes)")
        
        # Project the file
        projected_content = project_file_simple(model, file_path)
        
        if not projected_content:
            print(f"❌ No content projected for: {file_path}")
            continue
        
        # Create output path
        output_path = output_dir / file_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save projected content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(projected_content)
        
        # Get original content for comparison
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Calculate similarity
            original_lines = original_content.split('\n')
            projected_lines = projected_content.split('\n')
            matching_lines = len(set(original_lines) & set(projected_lines))
            similarity = matching_lines / len(original_lines) if original_lines else 0
            
            print(f"✅ Generated: {output_path}")
            print(f"   Original lines: {len(original_lines)}")
            print(f"   Projected lines: {len(projected_lines)}")
            print(f"   Similarity: {similarity:.1%}")
            
            generated_files.append({
                "original": file_path,
                "projected": str(output_path),
                "similarity": similarity,
                "original_lines": len(original_lines),
                "projected_lines": len(projected_lines)
            })
            
        except Exception as e:
            print(f"❌ Error comparing files: {e}")
    
    # Create a summary report
    summary_path = output_dir / "PROJECTION_SUMMARY.md"
    with open(summary_path, 'w') as f:
        f.write("# Model-Driven Projection Summary\n\n")
        f.write("This directory contains artifacts projected from the complete project model.\n\n")
        f.write("## Generated Files:\n\n")
        
        for file_info in generated_files:
            f.write(f"### {file_info['original']}\n")
            f.write(f"- **Projected**: `{file_info['projected']}`\n")
            f.write(f"- **Similarity**: {file_info['similarity']:.1%}\n")
            f.write(f"- **Original lines**: {file_info['original_lines']}\n")
            f.write(f"- **Projected lines**: {file_info['projected_lines']}\n\n")
        
        f.write("## Model Information:\n\n")
        f.write(f"- **Total files in model**: {len(model['files'])}\n")
        f.write(f"- **Total nodes in model**: {len(model['nodes'])}\n")
        f.write(f"- **Model version**: {model.get('version', 'unknown')}\n")
    
    print(f"\n📋 Summary report: {summary_path}")
    
    # Show what was generated
    print(f"\n📁 Generated Files:")
    for file_info in generated_files:
        status = "✅" if file_info['similarity'] > 0.8 else "⚠️" if file_info['similarity'] > 0.5 else "❌"
        print(f"  {status} {file_info['projected']} ({file_info['similarity']:.1%})")
    
    print(f"\n🎯 Projected artifacts saved to: {output_dir}")
    print("You can now compare the original files with the projected versions!")


def show_file_comparison(original_path, projected_path):
    """Show a side-by-side comparison of original vs projected."""
    print(f"\n🔍 COMPARISON: {original_path} vs {projected_path}")
    print("=" * 80)
    
    try:
        with open(original_path, 'r') as f:
            original_content = f.read()
        
        with open(projected_path, 'r') as f:
            projected_content = f.read()
        
        original_lines = original_content.split('\n')
        projected_lines = projected_content.split('\n')
        
        # Show first 10 lines of each
        print(f"\n🔴 ORIGINAL (first 10 lines):")
        print("-" * 40)
        for i, line in enumerate(original_lines[:10], 1):
            print(f"{i:2d}: {line}")
        
        print(f"\n🟢 PROJECTED (first 10 lines):")
        print("-" * 40)
        for i, line in enumerate(projected_lines[:10], 1):
            print(f"{i:2d}: {line}")
        
        # Calculate similarity
        matching_lines = len(set(original_lines) & set(projected_lines))
        similarity = matching_lines / len(original_lines) if original_lines else 0
        
        print(f"\n📊 SIMILARITY: {similarity:.1%}")
        print(f"  Original lines: {len(original_lines)}")
        print(f"  Projected lines: {len(projected_lines)}")
        print(f"  Matching lines: {matching_lines}")
        
    except Exception as e:
        print(f"❌ Error comparing files: {e}")


def main():
    """Generate projected artifacts."""
    generate_projected_artifacts()
    
    # Show a detailed comparison of one file
    print(f"\n{'='*80}")
    print("🔍 DETAILED COMPARISON EXAMPLE")
    print("=" * 80)
    
    original_file = "pyproject.toml"
    projected_file = "projected_artifacts/pyproject.toml"
    
    if Path(original_file).exists() and Path(projected_file).exists():
        show_file_comparison(original_file, projected_file)
    else:
        print("❌ Cannot show comparison - files not found")


if __name__ == "__main__":
    main() 