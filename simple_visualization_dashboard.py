#!/usr/bin/env python3
"""
Simple SVG Visualization Dashboard
Displays the generated SVG visualizations
"""

import streamlit as st
from pathlib import Path


def main():
    st.set_page_config(
        page_title="OpenFlow Playground - SVG Visualizations",
        page_icon="🎨",
        layout="wide"
    )
    
    st.title("🎨 OpenFlow Playground - SVG Visualizations")
    st.markdown("### Vector-based visualizations of our awesome work!")
    
    # Check if SVG files exist
    svg_dir = Path("data/visualizations")
    if not svg_dir.exists():
        st.error("❌ SVG visualizations directory not found!")
        st.info("Run `python src/visualization/svg_engine.py` to generate visualizations")
        return
    
    svg_files = list(svg_dir.glob("*.svg"))
    if not svg_files:
        st.error("❌ No SVG files found!")
        st.info("Run `python src/visualization/svg_engine.py` to generate visualizations")
        return
    
    st.success(f"✅ Found {len(svg_files)} SVG visualizations!")
    
    # Display each SVG file
    for svg_file in svg_files:
        st.subheader(f"📊 {svg_file.stem.replace('_', ' ').title()}")
        
        # Read and display SVG
        try:
            with open(svg_file, 'r') as f:
                svg_content = f.read()
            
            # Display SVG
            st.markdown(f"""
            <div style="text-align: center;">
                {svg_content}
            </div>
            """, unsafe_allow_html=True)
            
            # File info
            file_size = svg_file.stat().st_size
            st.caption(f"📁 {svg_file.name} ({file_size:,} bytes)")
            
        except Exception as e:
            st.error(f"Error reading {svg_file.name}: {e}")
        
        st.divider()
    
    # Add some stats
    st.sidebar.title("📈 Project Stats")
    st.sidebar.metric("SVG Files", len(svg_files))
    st.sidebar.metric("Total Size", f"{sum(f.stat().st_size for f in svg_files):,} bytes")
    
    # Add info about the system
    st.sidebar.title("ℹ️ About")
    st.sidebar.markdown("""
    **OpenFlow Playground Visualization System**
    
    - Vector-first design
    - Print-ready quality
    - Web-optimized
    - Interactive elements
    
    Generated with Plotly + Kaleido
    """)


if __name__ == "__main__":
    main()
