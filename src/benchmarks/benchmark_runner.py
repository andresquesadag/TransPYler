#!/usr/bin/env python3
"""
Benchmark Runner - Performance comparison between Python original, C++ transpiled, and C++ manual implementations
1. GENERATE all transpiled files first
2. EXECUTE performance tests with n-by-n real-time measurement
3. EXPORT results to CSV files for analysis

Refactored into modular components for better maintainability.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modular components
from src.benchmarks.transpiler_interface import generate_all_transpiled_files
from src.benchmarks.performance_tester import (
    run_performance_tests,
    generate_performance_summary,
    verify_program_outputs,
)
from src.benchmarks.utilities import cleanup_generated_files
from src.benchmarks.config import PATHS


def run_benchmark(max_values=None, generate_charts=True, custom_values=None):
    """
    Run complete benchmark with modular architecture:
    1. GENERATE all transpiled files
    2. EXECUTE tests n by n in real time
    3. GENERATE performance summary
    4. CREATE visualizations and HTML report

    max_values: Limit number of test values per algorithm
    generate_charts: If True, generates visual charts and HTML report
    custom_values: Dictionary with custom limits for each algorithm
    """
    print("TransPYler Benchmark Runner")
    print("=" * 50)

    try:
        # Phase 1: Generate all files
        generated_files = generate_all_transpiled_files(
            fast_mode=True, max_values=max_values, custom_values=custom_values
        )

        # Phase 1.5: Verify program outputs
        verify_program_outputs(generated_files)

        # Phase 2: Execute performance tests
        run_performance_tests(generated_files)

        # Phase 3: Generate performance summary
        generate_performance_summary(PATHS["results"])

        # Phase 4: Generate visualizations and tables
        if generate_charts:
            print("\nPhase 4: Generating charts and tables")
            print("-" * 40)
            try:
                from src.benchmarks.csv_visualizer import visualize_benchmark_results
                from src.benchmarks.table_generator import generate_benchmark_tables

                visualize_benchmark_results(str(PATHS["results"]))
                print("✅ Charts generated successfully!")
                
                generate_benchmark_tables(str(PATHS["results"]))
                print("✅ Tables generated successfully!")
            except Exception as e:
                print(f"⚠️  Visualization generation failed: {e}")

        # Files are always preserved for debugging
        print("\nPreserving generated files for debugging")

        print("\nBenchmark completed successfully")

    except Exception as e:
        print(f"Benchmark error: {e}")
        return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TransPYler Benchmark Runner"
    )
    parser.add_argument(
        "--limits",
        nargs=3,
        type=int,
        metavar=('SEL', 'FIB_REC', 'FIB_ITER'),
        help="Limits for each algorithm: selection_sort fibonacci_recursive fibonacci_iterative (e.g., --limits 10 25 30)",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip generation of visualization charts and tables",
    )

    args = parser.parse_args()

    # Parse limits if provided
    custom_values = None
    if args.limits:
        custom_values = {
            'selection_sort': args.limits[0],
            'fibonacci_recursive': args.limits[1], 
            'fibonacci_iterative': args.limits[2]
        }
        print(f"Limits: selection_sort={args.limits[0]}, fibonacci_recursive={args.limits[1]}, fibonacci_iterative={args.limits[2]}")
    else:
        print("Using default algorithm ranges")

    run_benchmark(
        generate_charts=not args.no_charts,
        custom_values=custom_values,
    )
