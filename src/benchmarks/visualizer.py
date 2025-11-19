"""
Benchmark Visualizer
-------------------
Generates comparative graphs and tables from benchmark results.

Features:
- Comparative line plots (time vs input size)
- Speedup plots (acceleration)
- Summary tables
- Export to PNG and PDF
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend without GUI for servers
import numpy as np
from pathlib import Path
from typing import List, Dict
from collections import defaultdict


class BenchmarkVisualizer:
    """Visualizes benchmark results."""
    
    def __init__(self, results: List, output_dir: str = None):
        """
        Initialize visualizer.
        
        Args:
            results: List of BenchmarkResult objects
            output_dir: Directory where to save graphs
        """
        self.results = results
        
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Organize results by program
        self.organized_results = self._organize_results()
    
    def _organize_results(self) -> Dict:
        """Organize results by program and language."""
        organized = defaultdict(lambda: defaultdict(dict))
        
        for result in self.results:
            program = result.program_name
            language = result.language
            size = result.input_size
            
            organized[program][language][size] = result
        
        return dict(organized)
    
    def plot_comparison(self, program_name: str, title: str = None,
                       save_path: str = None):
        """
        Generate comparative graph of execution times.
        
        Args:
            program_name: Program name
            title: Graph title
            save_path: Path where to save (auto-generated if None)
        """
        if program_name not in self.organized_results:
            print(f"No results found for {program_name}")
            return
        
        if title is None:
            title = f"{program_name} - Performance Comparison"
        
        if save_path is None:
            save_path = self.output_dir / f"{program_name}_comparison.png"
        
        # Prepare data
        program_data = self.organized_results[program_name]
        
        plt.figure(figsize=(12, 6))
        
        # Colors and styles
        colors = {
            'python': '#3776ab',  # Python Blue
            'cpp_transpiled': '#f34b7d',  # Pink/Red
            'cpp_manual': '#00599c'  # C++ Blue
        }
        
        labels = {
            'python': 'Python (Original)',
            'cpp_transpiled': 'C++ (Transpiled)',
            'cpp_manual': 'C++ (Hand-written)'
        }
        
        markers = {
            'python': 'o',
            'cpp_transpiled': 's',
            'cpp_manual': '^'
        }
        
        # Plot each language
        for language in ['python', 'cpp_transpiled', 'cpp_manual']:
            if language not in program_data:
                continue
            
            lang_data = program_data[language]
            sizes = sorted(lang_data.keys())
            times = [lang_data[size].execution_time for size in sizes]
            
            plt.plot(sizes, times, 
                    marker=markers[language],
                    color=colors[language],
                    label=labels[language],
                    linewidth=2,
                    markersize=8)
        
        plt.xlabel('Input Size (n)', fontsize=12)
        plt.ylabel('Execution Time (seconds)', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved comparison plot: {save_path}")
        plt.close()
    
    def plot_speedup(self, program_name: str, title: str = None,
                    save_path: str = None):
        """
        Generate speedup graph (acceleration) relative to Python.
        
        Args:
            program_name: Program name
            title: Graph title
            save_path: Path where to save
        """
        if program_name not in self.organized_results:
            print(f"No results found for {program_name}")
            return
        
        if title is None:
            title = f"{program_name} - Speedup vs Python"
        
        if save_path is None:
            save_path = self.output_dir / f"{program_name}_speedup.png"
        
        program_data = self.organized_results[program_name]
        
        if 'python' not in program_data:
            print(f"No Python baseline for {program_name}")
            return
        
        plt.figure(figsize=(12, 6))
        
        # Calculate speedups
        python_data = program_data['python']
        sizes = sorted(python_data.keys())
        
        speedups = {'cpp_transpiled': [], 'cpp_manual': []}
        
        for size in sizes:
            python_time = python_data[size].execution_time
            
            if 'cpp_transpiled' in program_data and size in program_data['cpp_transpiled']:
                trans_time = program_data['cpp_transpiled'][size].execution_time
                speedups['cpp_transpiled'].append(python_time / trans_time)
            
            if 'cpp_manual' in program_data and size in program_data['cpp_manual']:
                manual_time = program_data['cpp_manual'][size].execution_time
                speedups['cpp_manual'].append(python_time / manual_time)
        
        # Plot
        if speedups['cpp_transpiled']:
            plt.plot(sizes, speedups['cpp_transpiled'],
                    marker='s', color='#f34b7d',
                    label='C++ Transpiled',
                    linewidth=2, markersize=8)
        
        if speedups['cpp_manual']:
            plt.plot(sizes, speedups['cpp_manual'],
                    marker='^', color='#00599c',
                    label='C++ Hand-written',
                    linewidth=2, markersize=8)
        
        # Reference line 1x
        plt.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='1x (Python baseline)')
        
        plt.xlabel('Input Size (n)', fontsize=12)
        plt.ylabel('Speedup (times faster than Python)', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved speedup plot: {save_path}")
        plt.close()
    
    def generate_summary_table(self, save_path: str = None):
        """
        Generate summary table of results.
        
        Args:
            save_path: Path where to save
        """
        if save_path is None:
            save_path = self.output_dir / "summary_table.txt"
        
        with open(save_path, 'w') as f:
            f.write("="*100 + "\n")
            f.write(" " * 35 + "BENCHMARK SUMMARY TABLE\n")
            f.write("="*100 + "\n\n")
            
            for program_name in sorted(self.organized_results.keys()):
                program_data = self.organized_results[program_name]
                
                f.write(f"\n{program_name.upper()}\n")
                f.write("-"*100 + "\n")
                f.write(f"{'Size':<10} {'Python (s)':<15} {'C++ Trans (s)':<15} {'C++ Manual (s)':<15} "
                       f"{'Speedup Trans':<15} {'Speedup Manual':<15}\n")
                f.write("-"*100 + "\n")
                
                if 'python' not in program_data:
                    f.write("No Python baseline data\n")
                    continue
                
                python_data = program_data['python']
                sizes = sorted(python_data.keys())
                
                for size in sizes:
                    py_time = python_data[size].execution_time
                    
                    trans_time = "-"
                    manual_time = "-"
                    speedup_trans = "-"
                    speedup_manual = "-"
                    
                    if 'cpp_transpiled' in program_data and size in program_data['cpp_transpiled']:
                        trans_time = program_data['cpp_transpiled'][size].execution_time
                        speedup_trans = f"{py_time / trans_time:.2f}x"
                        trans_time = f"{trans_time:.6f}"
                    
                    if 'cpp_manual' in program_data and size in program_data['cpp_manual']:
                        manual_time = program_data['cpp_manual'][size].execution_time
                        speedup_manual = f"{py_time / manual_time:.2f}x"
                        manual_time = f"{manual_time:.6f}"
                    
                    f.write(f"{size:<10} {py_time:<15.6f} {trans_time:<15} {manual_time:<15} "
                           f"{speedup_trans:<15} {speedup_manual:<15}\n")
                
                f.write("\n")
            
            # General statistics
            f.write("\n" + "="*100 + "\n")
            f.write(" " * 35 + "OVERALL STATISTICS\n")
            f.write("="*100 + "\n\n")
            
            for program_name in sorted(self.organized_results.keys()):
                program_data = self.organized_results[program_name]
                
                if 'python' not in program_data:
                    continue
                
                f.write(f"\n{program_name}:\n")
                
                python_data = program_data['python']
                sizes = sorted(python_data.keys())
                
                trans_speedups = []
                manual_speedups = []
                
                for size in sizes:
                    py_time = python_data[size].execution_time
                    
                    if 'cpp_transpiled' in program_data and size in program_data['cpp_transpiled']:
                        trans_time = program_data['cpp_transpiled'][size].execution_time
                        trans_speedups.append(py_time / trans_time)
                    
                    if 'cpp_manual' in program_data and size in program_data['cpp_manual']:
                        manual_time = program_data['cpp_manual'][size].execution_time
                        manual_speedups.append(py_time / manual_time)
                
                if trans_speedups:
                    avg_trans = np.mean(trans_speedups)
                    min_trans = np.min(trans_speedups)
                    max_trans = np.max(trans_speedups)
                    f.write(f"  C++ Transpiled: Avg speedup = {avg_trans:.2f}x, "
                           f"Min = {min_trans:.2f}x, Max = {max_trans:.2f}x\n")
                
                if manual_speedups:
                    avg_manual = np.mean(manual_speedups)
                    min_manual = np.min(manual_speedups)
                    max_manual = np.max(manual_speedups)
                    f.write(f"  C++ Manual:     Avg speedup = {avg_manual:.2f}x, "
                           f"Min = {min_manual:.2f}x, Max = {max_manual:.2f}x\n")
        
        print(f"Saved summary table: {save_path}")
    
    def plot_all(self):
        """Generate all available graphs."""
        for program_name in self.organized_results.keys():
            self.plot_comparison(program_name)
            self.plot_speedup(program_name)
        
        self.generate_summary_table()


if __name__ == "__main__":
    print("Benchmark Visualizer")
    print("Use benchmark_suite.py to run complete analysis")