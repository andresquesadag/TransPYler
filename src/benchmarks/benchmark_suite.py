"""
Benchmark Suite - Main Script
-----------------------------
Runs all required benchmarks for the project:
1. Recursive Fibonacci (n = 1-50)
2. Iterative Fibonacci (n = 1-50)
3. Bubble Sort (variable sizes)

Generates results in CSV/JSON and comparative graphs.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.benchmarks.runner import BenchmarkRunner
from src.benchmarks.visualizer import BenchmarkVisualizer


def main():
    print("="*80)
    print(" TRANSPYLER - PERFORMANCE BENCHMARK SUITE")
    print("="*80)
    print()
    print("This suite will run comprehensive performance tests comparing:")
    print("  1. Original Python code")
    print("  2. Transpiled C++ code (with DynamicType runtime)")
    print("  3. Hand-written C++ code (optimized)")
    print()
    print("Tests to run:")
    print("  - Fibonacci Recursivo (n = 1 to 40)")
    print("  - Fibonacci Iterativo (n = 1 to 50)")
    print("  - Bubble Sort (size = 100 to 5000)")
    print()
    
    # Create runner
    runner = BenchmarkRunner()
    
    # ========================================================================
    # TEST 1: Recursive Fibonacci
    # ========================================================================
    print("\n" + "="*80)
    print(" TEST 1: FIBONACCI RECURSIVO")
    print("="*80)
    print("Testing fibonacci_recursivo with n from 1 to 40")
    print("(Limited to 40 due to exponential complexity)")
    print()
    
    # Ranges: 1-10, then 5 by 5 up to 40
    fib_rec_sizes = list(range(1, 11)) + list(range(15, 41, 5))
    
    runner.benchmark_program(
        "fibonacci_recursivo",
        input_sizes=fib_rec_sizes,
        iterations=3  # 3 iterations because it's slow
    )
    
    # ========================================================================
    # TEST 2: Iterative Fibonacci
    # ========================================================================
    print("\n" + "="*80)
    print(" TEST 2: FIBONACCI ITERATIVO")
    print("="*80)
    print("Testing fibonacci_iterativo with n from 1 to 50")
    print()
    
    # Ranges: 1-10, then 5 by 5 up to 50
    fib_iter_sizes = list(range(1, 11)) + list(range(15, 51, 5))
    
    runner.benchmark_program(
        "fibonacci_iterativo",
        input_sizes=fib_iter_sizes,
        iterations=5
    )
    
    # ========================================================================
    # TEST 3: Bubble Sort (Proposed Test)
    # ========================================================================
    print("\n" + "="*80)
    print(" TEST 3: BUBBLE SORT (Variable Input Size)")
    print("="*80)
    print("Testing bubble_sort with array sizes from 100 to 5000")
    print("At least 10 different input sizes")
    print()
    
    # 10 different sizes from 100 to 5000
    bubble_sizes = [100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000]
    
    runner.benchmark_program(
        "bubble_sort",
        input_sizes=bubble_sizes,
        iterations=5
    )
    
    # ========================================================================
    # Save Results
    # ========================================================================
    print("\n" + "="*80)
    print(" SAVING RESULTS")
    print("="*80)
    
    runner.save_results("benchmark_results")
    runner.print_summary()
    
    # ========================================================================
    # Generate Graphs
    # ========================================================================
    print("\n" + "="*80)
    print(" GENERATING VISUALIZATIONS")
    print("="*80)
    
    visualizer = BenchmarkVisualizer(runner.results)
    
    # Generate graphs for each program
    visualizer.plot_comparison("fibonacci_recursivo", 
                               title="Fibonacci Recursivo - Performance Comparison")
    visualizer.plot_comparison("fibonacci_iterativo",
                               title="Fibonacci Iterativo - Performance Comparison")
    visualizer.plot_comparison("bubble_sort",
                               title="Bubble Sort - Performance Comparison")
    
    # Generate speedup graph
    visualizer.plot_speedup("fibonacci_recursivo",
                           title="Fibonacci Recursivo - Speedup")
    visualizer.plot_speedup("fibonacci_iterativo",
                           title="Fibonacci Iterativo - Speedup")
    visualizer.plot_speedup("bubble_sort",
                           title="Bubble Sort - Speedup")
    
    # Generate summary table
    visualizer.generate_summary_table()
    
    print("\n" + "="*80)
    print(" BENCHMARK SUITE COMPLETED")
    print("="*80)
    print(f"\nResults saved in: {runner.output_dir}")
    print(f"Visualizations saved in: {visualizer.output_dir}")
    print()
    print("Files generated:")
    print("  - benchmark_results.csv")
    print("  - benchmark_results.json")
    print("  - fibonacci_recursivo_comparison.png")
    print("  - fibonacci_iterativo_comparison.png")
    print("  - bubble_sort_comparison.png")
    print("  - fibonacci_recursivo_speedup.png")
    print("  - fibonacci_iterativo_speedup.png")
    print("  - bubble_sort_speedup.png")
    print("  - summary_table.txt")
    print()


if __name__ == "__main__":
    main()
