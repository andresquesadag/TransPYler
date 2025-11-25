"""
Table Generator Module
Creates aesthetic table visualizations as PNG images from benchmark results
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import numpy as np

# Configure matplotlib for better table rendering
plt.style.use("seaborn-v0_8")

def generate_algorithm_table(csv_file, output_dir):
    """Generate a beautiful table image for a single algorithm"""
    df = pd.read_csv(csv_file)
    algorithm = csv_file.stem.replace("_results", "").replace("_", " ").title()
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, max(8, len(df) * 0.4 + 2)))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare data for table
    table_data = []
    headers = ['N', 'Result', 'Python (ms)', 'C++ Transpiled (ms)', 'C++ Manual (ms)', 'Trans Speedup', 'Manual Speedup']
    
    for _, row in df.iterrows():
        table_data.append([
            int(row['n']),
            row['result'],
            f"{row['python_ms']:.2f}",
            f"{row['cpp_transpiled_ms']:.2f}",
            f"{row['cpp_manual_ms']:.2f}" if pd.notna(row['cpp_manual_ms']) else 'N/A',
            f"{row['speedup_transpiled']:.1f}x",
            f"{row['speedup_manual']:.1f}x" if pd.notna(row['speedup_manual']) else 'N/A'
        ])
    
    # Create table
    table = ax.table(cellText=table_data, colLabels=headers, loc='center', cellLoc='center')
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.5)
    
    # Color scheme
    header_color = '#4CAF50'
    row_colors = ['#f0f0f0', '#ffffff']
    speedup_good_color = '#e8f5e8'
    speedup_great_color = '#c8e6c9'
    
    # Style headers
    for i in range(len(headers)):
        table[(0, i)].set_facecolor(header_color)
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            # Alternate row colors
            base_color = row_colors[i % 2]
            
            # Highlight speedup columns with performance-based colors
            if j in [5, 6]:  # Speedup columns
                try:
                    speedup_val = float(table_data[i-1][j].replace('x', ''))
                    if speedup_val >= 20:
                        base_color = speedup_great_color
                    elif speedup_val >= 10:
                        base_color = speedup_good_color
                except:
                    pass
            
            table[(i, j)].set_facecolor(base_color)
            
            # Bold the best performing values
            if j in [5, 6]:  # Speedup columns
                try:
                    speedup_val = float(table_data[i-1][j].replace('x', ''))
                    if speedup_val >= 15:
                        table[(i, j)].set_text_props(weight='bold')
                except:
                    pass
    
    # Add title
    plt.suptitle(f'{algorithm} - Performance Results', fontsize=16, fontweight='bold', y=0.95)
    
    # Add summary statistics
    avg_trans = df["speedup_transpiled"].mean()
    avg_manual = df["speedup_manual"].mean() if df["speedup_manual"].notna().any() else 0
    max_trans = df["speedup_transpiled"].max()
    max_manual = df["speedup_manual"].max() if df["speedup_manual"].notna().any() else 0
    
    summary_text = f"Summary: Avg Speedup - Transpiled: {avg_trans:.1f}x, Manual: {avg_manual:.1f}x | "
    summary_text += f"Max Speedup - Transpiled: {max_trans:.1f}x, Manual: {max_manual:.1f}x"
    
    plt.figtext(0.5, 0.02, summary_text, ha='center', va='bottom', fontsize=11,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    # Add legend for color coding
    legend_elements = [
        patches.Patch(color=speedup_great_color, label='Excellent Speedup (≥20x)'),
        patches.Patch(color=speedup_good_color, label='Good Speedup (≥10x)'),
        patches.Patch(color='#f0f0f0', label='Normal Performance')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.2, 1))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1, top=0.9)
    
    # Save table
    safe_name = algorithm.lower().replace(" ", "_")
    table_file = output_dir / f"{safe_name}_table.png"
    plt.savefig(table_file, dpi=300, bbox_inches="tight", facecolor='white')
    plt.close()
    
    return table_file


def generate_summary_table(csv_files, output_dir):
    """Generate a summary comparison table across all algorithms"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Collect summary data
    summary_data = []
    headers = ['Algorithm', 'Tests Run', 'Avg Trans Speedup', 'Max Trans Speedup', 
              'Avg Manual Speedup', 'Max Manual Speedup', 'Best Result']
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        algorithm = csv_file.stem.replace("_results", "").replace("_", " ").title()
        
        avg_trans = df["speedup_transpiled"].mean()
        max_trans = df["speedup_transpiled"].max()
        avg_manual = df["speedup_manual"].mean() if df["speedup_manual"].notna().any() else 0
        max_manual = df["speedup_manual"].max() if df["speedup_manual"].notna().any() else 0
        
        best_speedup = max(max_trans, max_manual)
        best_type = "Manual" if max_manual > max_trans else "Transpiled"
        
        summary_data.append([
            algorithm,
            len(df),
            f"{avg_trans:.1f}x",
            f"{max_trans:.1f}x",
            f"{avg_manual:.1f}x" if avg_manual > 0 else "N/A",
            f"{max_manual:.1f}x" if max_manual > 0 else "N/A",
            f"{best_speedup:.1f}x ({best_type})"
        ])
    
    # Create table
    table = ax.table(cellText=summary_data, colLabels=headers, loc='center', cellLoc='center')
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.3, 3)
    
    # Color scheme
    header_color = '#2196F3'
    row_colors = ['#f5f5f5', '#ffffff']
    excellent_color = '#4CAF50'
    good_color = '#8BC34A'
    
    # Style headers
    for i in range(len(headers)):
        table[(0, i)].set_facecolor(header_color)
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, len(summary_data) + 1):
        for j in range(len(headers)):
            base_color = row_colors[i % 2]
            
            # Highlight performance columns
            if j in [2, 3, 4, 5, 6]:  # Speedup columns
                cell_text = summary_data[i-1][j]
                if 'x' in cell_text and cell_text != "N/A":
                    try:
                        speedup_val = float(cell_text.split('x')[0])
                        if speedup_val >= 20:
                            base_color = excellent_color
                            table[(i, j)].set_text_props(weight='bold', color='white')
                        elif speedup_val >= 10:
                            base_color = good_color
                            table[(i, j)].set_text_props(weight='bold')
                    except:
                        pass
            
            table[(i, j)].set_facecolor(base_color)
    
    # Add title
    plt.suptitle('TransPYler Benchmark Summary - All Algorithms', fontsize=16, fontweight='bold', y=0.95)
    
    # Add legend
    legend_elements = [
        patches.Patch(color=excellent_color, label='Excellent Performance (≥20x)'),
        patches.Patch(color=good_color, label='Good Performance (≥10x)'),
        patches.Patch(color='#f5f5f5', label='Standard Performance')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.25, 1))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    # Save summary table
    summary_file = output_dir / "benchmark_summary_table.png"
    plt.savefig(summary_file, dpi=300, bbox_inches="tight", facecolor='white')
    plt.close()
    
    return summary_file


def generate_benchmark_tables(results_dir="benchmark_results"):
    """Generate all benchmark tables as PNG images"""
    results_dir = Path(results_dir)
    output_dir = results_dir / "tables"
    output_dir.mkdir(exist_ok=True)
    
    # Find CSV files
    csv_files = list(results_dir.glob("*_results.csv"))
    if not csv_files:
        print("No CSV files found for table generation!")
        return
    
    print(f"\nGenerating aesthetic tables from {len(csv_files)} CSV files...")
    
    # Generate individual algorithm tables
    for csv_file in csv_files:
        table_file = generate_algorithm_table(csv_file, output_dir)
        algorithm = csv_file.stem.replace("_results", "").replace("_", " ").title()
        print(f"✓ {table_file.name} - Detailed table for {algorithm}")
    
    # Generate summary table
    summary_file = generate_summary_table(csv_files, output_dir)
    print(f"✓ {summary_file.name} - Summary comparison table")
    
    print(f"\nTables saved in: {output_dir}")


if __name__ == "__main__":
    import sys
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "benchmark_results"
    generate_benchmark_tables(results_dir)