#!/usr/bin/env python3
"""
OpenFlow Playground - Visualization Dashboard Launcher
Simple launcher for the comprehensive SVG visualization dashboard
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the visualization dashboard"""
    print("🚀 Launching OpenFlow Playground Visualization Dashboard...")
    
    # Check if we're in the right directory
    if not Path("project_model_registry.json").exists():
        print("❌ Error: project_model_registry.json not found. Please run from the project root.")
        sys.exit(1)
    
    # Check if SVG visualizations exist
    svg_dir = Path("data/visualizations")
    if not svg_dir.exists() or not list(svg_dir.glob("*.svg")):
        print("⚠️  Warning: No SVG visualizations found. Generating them first...")
        
        # Generate SVG visualizations
        try:
            result = subprocess.run([
                "uv", "run", "python", "src/visualization/svg_engine.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ SVG visualizations generated successfully!")
            else:
                print(f"❌ Failed to generate SVG visualizations: {result.stderr}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error generating SVG visualizations: {e}")
            sys.exit(1)
    
    # Launch the dashboard
    print("🎨 Starting comprehensive visualization dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print("")
    
    try:
        subprocess.run([
            "uv", "run", "streamlit", "run", "src/visualization/comprehensive_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
