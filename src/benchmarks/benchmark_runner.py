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
)
from src.benchmarks.utilities import cleanup_generated_files
from src.benchmarks.config import PATHS


def run_benchmark(
    fast_mode=False, no_cleanup=False, max_values=None, generate_charts=True
):
    """
    Run complete benchmark with modular architecture:
    1. GENERATE all transpiled files
    2. EXECUTE tests n by n in real time
    3. CLEAN UP temporary files (optional)
    4. GENERATE performance summary
    5. CREATE visualizations and HTML report

    fast_mode: If True, uses literal replacement instead of re-transpiling for each n
    no_cleanup: If True, doesn't delete generated temporary files
    max_values: Limit number of test values per algorithm
    generate_charts: If True, generates visual charts and HTML report
    """
    print("TransPYler Benchmark Runner")
    print("=" * 50)

    try:
        # Phase 1: Generate all files
        generated_files = generate_all_transpiled_files(
            fast_mode=fast_mode, max_values=max_values
        )

        # Phase 2: Execute performance tests
        run_performance_tests(generated_files)

        # Phase 3: Generate performance summary
        generate_performance_summary(PATHS["results"])

        # Phase 4: Generate simple visualizations
        if generate_charts:
            print("\nPhase 4: Generating charts")
            print("-" * 40)
            try:
                from src.benchmarks.csv_visualizer import visualize_benchmark_results

                visualize_benchmark_results(str(PATHS["results"]))
                print("✅ Charts generated successfully!")
            except Exception as e:
                print(f"⚠️  Chart generation failed: {e}")

        # Phase 5: Cleanup (optional)
        if not no_cleanup:
            cleanup_generated_files(PATHS["transpiled_output"])
            print("\nCleaning up temporary files...")
            print("Cleanup completed")
        else:
            print("\nPreserving generated files for debugging")

        print("\nBenchmark completed successfully")

    except Exception as e:
        print(f"Benchmark error: {e}")
        return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TransPYler Benchmark Runner - Modular Architecture"
    )
    parser.add_argument(
        "-f",
        "--fast",
        action="store_true",
        help="Fast mode: transpile once and use literal replacement (faster)",
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Preserve generated temporary files (useful for debugging)",
    )
    parser.add_argument(
        "--values",
        type=int,
        default=None,
        help="Number of values to generate per algorithm (e.g., --values 10). Default uses all original values.",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip generation of visualization charts and HTML report",
    )

    args = parser.parse_args()

    if args.fast:
        print("Fast mode enabled - using literal replacement optimization")

    if args.no_cleanup:
        print("No cleanup - generated files will be preserved")

    if args.values:
        print(f"Limited values - generating maximum {args.values} values per algorithm")

    run_benchmark(
        fast_mode=args.fast,
        no_cleanup=args.no_cleanup,
        max_values=args.values,
        generate_charts=not args.no_charts,
    )
