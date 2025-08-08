#!/usr/bin/env python3
"""
Test script for the SVG visualization system
"""

import sys
from pathlib import Path


def test_visualization_system():
    """Test the visualization system components"""
    print("🧪 Testing SVG Visualization System...")
    
    # Test 1: Check if SVG files exist
    svg_dir = Path("data/visualizations")
    if svg_dir.exists():
        svg_files = list(svg_dir.glob("*.svg"))
        print(f"✅ Found {len(svg_files)} SVG files:")
        for svg_file in svg_files:
            print(f"   - {svg_file.name}")
    else:
        print("❌ SVG directory not found")
        return False
    
    # Test 2: Check if visualization modules exist
    viz_modules = [
        "src/visualization/svg_engine.py",
        "src/visualization/comprehensive_dashboard.py",
        "src/visualization/dashboard.py",
        "run_visualization_dashboard.py"
    ]
    
    for module in viz_modules:
        if Path(module).exists():
            print(f"✅ {module} exists")
        else:
            print(f"❌ {module} missing")
            return False
    
    # Test 3: Test SVG engine import
    try:
        from src.visualization.svg_engine import SVGVisualizationEngine
        print("✅ SVG engine imports successfully")
    except ImportError as e:
        print(f"❌ SVG engine import failed: {e}")
        return False
    
    # Test 4: Test dashboard import
    try:
        from src.visualization.comprehensive_dashboard import ComprehensiveDashboard
        print("✅ Dashboard imports successfully")
        # Use the import to avoid unused import warning
        dashboard_class = ComprehensiveDashboard
        print(f"✅ Dashboard class: {dashboard_class}")
    except ImportError as e:
        print(f"❌ Dashboard import failed: {e}")
        return False
    
    # Test 5: Test SVG generation
    try:
        engine = SVGVisualizationEngine()
        data_sources = engine.load_project_data()
        print(f"✅ Loaded {len(data_sources)} data sources")
        
        # Generate one visualization to test
        result = engine.create_system_architecture_svg()
        if result:
            print("✅ SVG generation working")
        else:
            print("❌ SVG generation failed")
            return False
    except Exception as e:
        print(f"❌ SVG generation test failed: {e}")
        return False
    
    print("🎉 All visualization system tests passed!")
    return True


if __name__ == "__main__":
    success = test_visualization_system()
    sys.exit(0 if success else 1)
