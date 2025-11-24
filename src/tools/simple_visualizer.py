"""
Simple CSV Visualizer
Generates essential comparison charts from benchmark CSV files
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set simple style
plt.style.use('seaborn-v0_8')
sns.set_palette("Set2")


def visualize_benchmark_csv(csv_dir="benchmark_results"):
    """Generate simple comparison charts from CSV files"""
    
    csv_dir = Path(csv_dir)
    output_dir = csv_dir / "charts"
    output_dir.mkdir(exist_ok=True)
    
    # Find CSV files
    csv_files = list(csv_dir.glob("*_results.csv"))
    if not csv_files:
        print("No CSV files found!")
        return
    
    print(f"Found {len(csv_files)} CSV files. Generating charts...")
    
    # 1. Execution Time Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        algorithm = csv_file.stem.replace("_python_results", "").replace("_", " ").title()
        
        ax.plot(df['n'], df['python_ms'], 'o-', label=f'{algorithm} Python', linewidth=2)
        ax.plot(df['n'], df['cpp_transpiled_ms'], 's-', label=f'{algorithm} C++ Transpiled', linewidth=2)
        ax.plot(df['n'], df['cpp_manual_ms'], '^-', label=f'{algorithm} C++ Manual', linewidth=2)
    
    ax.set_xlabel('Input Size (n)')
    ax.set_ylabel('Execution Time (ms)')
    ax.set_title('Execution Time Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'execution_times.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ execution_times.png")
    
    # 2. Speedup Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        algorithm = csv_file.stem.replace("_python_results", "").replace("_", " ").title()
        
        ax.plot(df['n'], df['speedup_transpiled'], 'o-', label=f'{algorithm} Transpiled', linewidth=2)
        ax.plot(df['n'], df['speedup_manual'], 's-', label=f'{algorithm} Manual', linewidth=2)
    
    ax.set_xlabel('Input Size (n)')
    ax.set_ylabel('Speedup Factor (x)')
    ax.set_title('Performance Speedup vs Python')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='No Speedup')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'speedup.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ speedup.png")
    
    # 3. Bar Chart Comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    algorithms = []
    avg_transpiled = []
    avg_manual = []
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        algorithm = csv_file.stem.replace("_python_results", "").replace("_", " ").title()
        algorithms.append(algorithm)
        avg_transpiled.append(df['speedup_transpiled'].mean())
        avg_manual.append(df['speedup_manual'].mean())
    
    # Average speedup
    x_pos = range(len(algorithms))
    ax1.bar([p - 0.2 for p in x_pos], avg_transpiled, 0.4, label='Transpiled', alpha=0.8)
    ax1.bar([p + 0.2 for p in x_pos], avg_manual, 0.4, label='Manual', alpha=0.8)
    ax1.set_xlabel('Algorithm')
    ax1.set_ylabel('Average Speedup (x)')
    ax1.set_title('Average Performance Speedup')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(algorithms, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Max speedup
    max_transpiled = []
    max_manual = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        max_transpiled.append(df['speedup_transpiled'].max())
        max_manual.append(df['speedup_manual'].max())
    
    ax2.bar([p - 0.2 for p in x_pos], max_transpiled, 0.4, label='Transpiled', alpha=0.8)
    ax2.bar([p + 0.2 for p in x_pos], max_manual, 0.4, label='Manual', alpha=0.8)
    ax2.set_xlabel('Algorithm')
    ax2.set_ylabel('Maximum Speedup (x)')
    ax2.set_title('Peak Performance Speedup')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(algorithms, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ comparison.png")
    
    print(f"\nCharts saved in: {output_dir}")


if __name__ == "__main__":
    import sys
    csv_dir = sys.argv[1] if len(sys.argv) > 1 else "benchmark_results"
    visualize_benchmark_csv(csv_dir)