"""
Simple CSV Visualizer
Generates essential comparison charts from benchmark CSV results
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Simple style
plt.style.use('seaborn-v0_8')


def visualize_benchmark_results(results_dir="benchmark_results"):
    """Generate simple comparison charts from CSV files"""
    
    results_dir = Path(results_dir)
    output_dir = results_dir / "charts"
    output_dir.mkdir(exist_ok=True)
    
    # Find CSV files
    csv_files = list(results_dir.glob("*_results.csv"))
    if not csv_files:
        print("No CSV files found!")
        return
    
    print(f"Generating charts from {len(csv_files)} CSV files...")
    
    # 1. Execution Time Chart
    plt.figure(figsize=(14, 8))
    
    colors = ['#e74c3c', '#3498db', '#2ecc71']  # Red for Python, Blue for Transpiled, Green for Manual
    markers = ['o', 's', '^']
    
    for i, csv_file in enumerate(csv_files):
        df = pd.read_csv(csv_file)
        algorithm = csv_file.stem.replace("_python_results", "").replace("_", " ").title()
        
        # Python Original (slowest, should be highest on chart)
        plt.plot(df['n'], df['python_ms'], marker=markers[0], linestyle='-', 
                label=f'{algorithm} - Python Original', linewidth=3, markersize=8, 
                color=colors[0], alpha=0.8)
        
        # C++ Transpiled (middle performance)
        plt.plot(df['n'], df['cpp_transpiled_ms'], marker=markers[1], linestyle='-', 
                label=f'{algorithm} - C++ Transpiled (TransPYler)', linewidth=3, markersize=8, 
                color=colors[1], alpha=0.8)
        
        # C++ Manual (fastest, should be lowest on chart)
        plt.plot(df['n'], df['cpp_manual_ms'], marker=markers[2], linestyle='-', 
                label=f'{algorithm} - C++ Manual', linewidth=3, markersize=8, 
                color=colors[2], alpha=0.8)
    
    plt.xlabel('Input Size (n)', fontsize=12, fontweight='bold')
    plt.ylabel('Execution Time (milliseconds)', fontsize=12, fontweight='bold')
    plt.title('Performance Comparison: Python vs C++ Transpiled vs C++ Manual', 
              fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Add annotations
    plt.text(0.02, 0.98, 'Lower is better', transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'execution_times.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ execution_times.png - Shows Python Original vs C++ Transpiled vs C++ Manual")
    
    # 2. Speedup Chart (how much faster than Python)
    plt.figure(figsize=(14, 8))
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        algorithm = csv_file.stem.replace("_python_results", "").replace("_", " ").title()
        
        # Speedup of C++ Transpiled vs Python
        plt.plot(df['n'], df['speedup_transpiled'], 'o-', 
                label=f'{algorithm} - C++ Transpiled Speedup', 
                linewidth=3, markersize=8, color='#3498db', alpha=0.8)
        
        # Speedup of C++ Manual vs Python  
        plt.plot(df['n'], df['speedup_manual'], 's-', 
                label=f'{algorithm} - C++ Manual Speedup', 
                linewidth=3, markersize=8, color='#2ecc71', alpha=0.8)
    
    plt.xlabel('Input Size (n)', fontsize=12, fontweight='bold')
    plt.ylabel('Speedup Factor (times faster than Python)', fontsize=12, fontweight='bold')
    plt.title('Performance Speedup: How much faster than Python Original', 
              fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Reference line at 1x (no speedup)
    plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, linewidth=2, 
                label='No Speedup (same as Python)')
    
    # Add annotations
    plt.text(0.02, 0.98, 'Higher is better\n(More speedup)', transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'speedup.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ speedup.png - Shows C++ Transpiled and Manual speedup vs Python Original")
    
    # 3. Bar Chart Comparison (Average and Maximum Speedups)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    algorithms = []
    avg_transpiled = []
    avg_manual = []
    max_transpiled = []
    max_manual = []
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        algorithm = csv_file.stem.replace("_python_results", "").replace("_", " ").title()
        algorithms.append(algorithm)
        avg_transpiled.append(df['speedup_transpiled'].mean())
        avg_manual.append(df['speedup_manual'].mean())
        max_transpiled.append(df['speedup_transpiled'].max())
        max_manual.append(df['speedup_manual'].max())
    
    # Average speedup comparison
    x_pos = range(len(algorithms))
    bars1 = ax1.bar([p - 0.2 for p in x_pos], avg_transpiled, 0.4, 
                    label='C++ Transpiled (TransPYler)', alpha=0.8, color='#3498db')
    bars2 = ax1.bar([p + 0.2 for p in x_pos], avg_manual, 0.4, 
                    label='C++ Manual', alpha=0.8, color='#2ecc71')
    
    ax1.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Speedup vs Python Original (x)', fontsize=12, fontweight='bold')
    ax1.set_title('Average Performance Speedup\n(Higher bars = Faster than Python)', 
                  fontsize=13, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(algorithms, rotation=45, ha='right')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Maximum speedup comparison
    bars3 = ax2.bar([p - 0.2 for p in x_pos], max_transpiled, 0.4, 
                    label='C++ Transpiled (TransPYler)', alpha=0.8, color='#3498db')
    bars4 = ax2.bar([p + 0.2 for p in x_pos], max_manual, 0.4, 
                    label='C++ Manual', alpha=0.8, color='#2ecc71')
    
    ax2.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Maximum Speedup vs Python Original (x)', fontsize=12, fontweight='bold')
    ax2.set_title('Peak Performance Speedup\n(Best case performance improvement)', 
                  fontsize=13, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(algorithms, rotation=45, ha='right')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar1, bar2, bar3, bar4) in enumerate(zip(bars1, bars2, bars3, bars4)):
        ax1.text(bar1.get_x() + bar1.get_width()/2., bar1.get_height() + 0.05,
                f'{avg_transpiled[i]:.1f}x', ha='center', va='bottom', fontsize=9)
        ax1.text(bar2.get_x() + bar2.get_width()/2., bar2.get_height() + 0.05,
                f'{avg_manual[i]:.1f}x', ha='center', va='bottom', fontsize=9)
        ax2.text(bar3.get_x() + bar3.get_width()/2., bar3.get_height() + 0.1,
                f'{max_transpiled[i]:.1f}x', ha='center', va='bottom', fontsize=9)
        ax2.text(bar4.get_x() + bar4.get_width()/2., bar4.get_height() + 0.1,
                f'{max_manual[i]:.1f}x', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ comparison.png - Bar chart comparison: Python Original vs C++ Transpiled vs C++ Manual")
    
    print(f"\nCharts saved in: {output_dir}")


if __name__ == "__main__":
    import sys
    csv_dir = sys.argv[1] if len(sys.argv) > 1 else "benchmark_results"
    visualize_benchmark_results(csv_dir)