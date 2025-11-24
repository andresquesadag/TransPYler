#!/usr/bin/env python3
"""
Standalone CSV Visualizer
Generate beautiful charts and HTML reports from existing benchmark CSV files
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.benchmarks.csv_visualizer import BenchmarkVisualizer


def main():
    """Main function for standalone visualizer"""
    parser = argparse.ArgumentParser(description='TransPYler CSV Visualizer - Generate beautiful charts from benchmark results')
    parser.add_argument('--input', '-i', type=str, default="benchmark_results",
                       help='Directory containing CSV result files (default: benchmark_results)')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Output directory for visualizations (default: input_dir/visualizations)')
    parser.add_argument('--show', action='store_true',
                       help='Display charts in addition to saving them')
    
    args = parser.parse_args()
    
    # Setup paths
    input_dir = Path(args.input)
    
    if not input_dir.exists():
        print(f"❌ Input directory '{input_dir}' not found!")
        print("Run benchmarks first or specify correct directory with --input")
        return 1
    
    # Check for CSV files
    csv_files = list(input_dir.glob("*_results.csv"))
    if not csv_files:
        print(f"❌ No CSV result files found in '{input_dir}'!")
        print("Make sure the directory contains files ending with '_results.csv'")
        return 1
    
    print("🎨 TransPYler CSV Visualizer")
    print("=" * 50)
    print(f"📁 Input directory: {input_dir}")
    print(f"📊 Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        print(f"   - {csv_file.name}")
    
    try:
        # Create visualizer
        visualizer = BenchmarkVisualizer(input_dir)
        
        if not visualizer.data:
            print("❌ No valid data loaded from CSV files!")
            return 1
        
        # Generate visualizations
        if args.output:
            output_dir = Path(args.output)
        else:
            output_dir = input_dir / "visualizations"
        
        output_dir.mkdir(exist_ok=True)
        print(f"💾 Output directory: {output_dir}")
        
        visualizer.generate_all_visualizations(str(output_dir))
        
        # Show charts if requested
        if args.show:
            print("\n🖼️  Displaying charts...")
            import matplotlib.pyplot as plt
            
            print("📊 Displaying execution time comparison...")
            visualizer.create_execution_time_comparison()
            
            print("🚀 Displaying speedup comparison...")
            visualizer.create_speedup_comparison()
            
            print("🎯 Displaying comprehensive dashboard...")
            visualizer.create_comprehensive_dashboard()
            
            print("📋 Displaying summary table...")
            visualizer.create_summary_table()
        
        print("\n✅ Visualization generation completed successfully!")
        print(f"📂 All files saved to: {output_dir}")
        print(f"🌐 Open '{output_dir}/benchmark_report.html' to view the complete report")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())