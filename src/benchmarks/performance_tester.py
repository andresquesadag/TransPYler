"""
Performance Testing Module
Handles execution and measurement of benchmark tests
"""

import sys
import time
import subprocess
import csv
from pathlib import Path

from src.benchmarks.config import PATHS, PERFORMANCE_SETTINGS


def measure_execution_time(executable_or_script, n_value, is_python=False, rounds=None):
    """Measure execution time for a given executable or Python script with n_value argument"""
    if rounds is None:
        rounds = PERFORMANCE_SETTINGS['measurement_rounds']
    
    times = []
    
    for _ in range(rounds):
        start_time = time.perf_counter()
        
        if is_python:
            result = subprocess.run([sys.executable, str(executable_or_script), str(n_value)], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run([str(executable_or_script), str(n_value)], 
                                  capture_output=True, text=True)
        
        end_time = time.perf_counter()
        times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    average_time = sum(times) / len(times)
    return average_time, result


def extract_result_from_output(output_text):
    """Extract result value from program output"""
    if not output_text:
        return "N/A"
    
    lines = output_text.strip().split('\n')
    for line in lines:
        if line.strip().startswith('result:'):
            return line.split(':', 1)[1].strip()
    
    return "N/A"


def run_performance_tests(generated_files):
    """Phase 2: Execute performance tests with command line arguments"""
    print("\nPhase 2: Running performance tests")
    print("-" * 40)
    
    # Create results directory
    results_dir = PATHS['results']
    results_dir.mkdir(exist_ok=True)
    
    for algorithm_name, files in generated_files.items():
        print(f"\nTesting: {algorithm_name}")
        
        n_values = files['n_values']
        print(f"Running {len(n_values)} test cases with command line arguments")
        
        # Prepare CSV data
        csv_data = []
        
        # Header for console output
        print(f"\n{'N':<6} {'Result':<12} {'Python(ms)':<12} {'C++Trans(ms)':<14} {'C++Manual(ms)':<14} {'Speedup':<10}")
        print("-" * 80)
        
        for n in n_values:
            # 1. Measure Python Original (with command line argument)
            py_file = files['python_original']
            tiempo_py, py_result = measure_execution_time(py_file, n, is_python=True)
            
            # Get result from Python output
            resultado = extract_result_from_output(py_result.stdout if py_result.returncode == 0 else "")
            
            # 2. Measure C++ Transpiled (with command line argument)
            transpiled_exe = files['executable_transpiled']
            tiempo_trans, trans_result = measure_execution_time(transpiled_exe, n, is_python=False)
            
            # 3. Measure C++ Manual (with command line argument) - if available
            tiempo_manual = None
            manual_exe = files['executable_manual']
            if manual_exe:
                tiempo_manual, _ = measure_execution_time(manual_exe, n, is_python=False)
            
            # Calculate speedup
            speedup_trans = tiempo_py / tiempo_trans if tiempo_trans > 0 else 0
            speedup_manual = tiempo_py / tiempo_manual if tiempo_manual and tiempo_manual > 0 else 0
            
            # Print result immediately (n by n)
            if tiempo_manual:
                print(f"{n:<6} {resultado:<12} {tiempo_py:<12.3f} {tiempo_trans:<14.3f} {tiempo_manual:<14.3f} {speedup_manual:<10.2f}x")
            else:
                print(f"{n:<6} {resultado:<12} {tiempo_py:<12.3f} {tiempo_trans:<14.3f} {'N/A':<14} {speedup_trans:<10.2f}x")
            
            # Store data for CSV
            csv_data.append({
                'n': n,
                'result': resultado,
                'python_ms': round(tiempo_py, 3),
                'cpp_transpiled_ms': round(tiempo_trans, 3),
                'cpp_manual_ms': round(tiempo_manual, 3) if tiempo_manual else None,
                'speedup_transpiled': round(speedup_trans, 2),
                'speedup_manual': round(speedup_manual, 2) if speedup_manual else None
            })
        
        # Write CSV file for this algorithm
        if csv_data:
            csv_file = results_dir / f"{algorithm_name}_results.csv"
            with open(csv_file, 'w', newline='') as f:
                fieldnames = ['n', 'result', 'python_ms', 'cpp_transpiled_ms', 'cpp_manual_ms', 'speedup_transpiled', 'speedup_manual']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            print(f"Results saved to: {csv_file}")


def generate_performance_summary(results_dir):
    """Generate a summary of all performance test results"""
    if not results_dir.exists():
        return
    
    csv_files = list(results_dir.glob("*_results.csv"))
    
    if not csv_files:
        return
    
    print("\nPerformance Summary:")
    print("=" * 50)
    
    for csv_file in csv_files:
        algorithm_name = csv_file.stem.replace("_results", "")
        print(f"\n{algorithm_name}:")
        
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if rows:
                    # Calculate speedups for both transpiled and manual (when available)
                    speedups_trans = [float(row['speedup_transpiled']) for row in rows if row['speedup_transpiled']]
                    speedups_manual = [float(row['speedup_manual']) for row in rows if row['speedup_manual']]
                    
                    avg_speedup_trans = sum(speedups_trans) / len(speedups_trans) if speedups_trans else 0
                    max_speedup_trans = max(speedups_trans) if speedups_trans else 0
                    min_speedup_trans = min(speedups_trans) if speedups_trans else 0
                    
                    avg_speedup_manual = sum(speedups_manual) / len(speedups_manual) if speedups_manual else 0
                    max_speedup_manual = max(speedups_manual) if speedups_manual else 0
                    min_speedup_manual = min(speedups_manual) if speedups_manual else 0
                    
                    print(f"  Tests run: {len(rows)}")
                    print(f"  Transpiled speedup - Avg: {avg_speedup_trans:.2f}x, Max: {max_speedup_trans:.2f}x, Min: {min_speedup_trans:.2f}x")
                    if speedups_manual:
                        print(f"  Manual speedup     - Avg: {avg_speedup_manual:.2f}x, Max: {max_speedup_manual:.2f}x, Min: {min_speedup_manual:.2f}x")
                    else:
                        print(f"  Manual C++: Not available")
        except Exception as e:
            print(f"  Error reading results: {e}")