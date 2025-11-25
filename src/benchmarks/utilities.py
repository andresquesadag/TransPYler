"""
Utilities Module
Helper functions for benchmark operations: value generation, file parsing, cleanup
"""

import shutil
import re
from pathlib import Path


def generate_n_values_for_algorithm(algorithm_name, max_values=None, custom_values=None):
    """Generate appropriate n values for each algorithm"""
    # Check if custom values are specified for this algorithm
    if custom_values:
        # Clean algorithm name for matching
        clean_name = algorithm_name.replace("_python", "")
        
        # Check for exact match or partial match in custom values
        for custom_algo, custom_value in custom_values.items():
            if custom_algo == clean_name or custom_algo in clean_name:
                print(f"  Using custom range: 1 to {custom_value}")
                
                # Generate range based on algorithm type
                if "fibonacci" in algorithm_name:
                    return list(range(1, custom_value + 1))
                elif "selection_sort" in algorithm_name:
                    # For selection sort, generate reasonable increments up to the value  
                    # Ensure we start from 1 and go up to custom_value
                    if custom_value <= 10:
                        return list(range(1, custom_value + 1))  # 1, 2, 3, ..., 10
                    elif custom_value <= 20:
                        return list(range(1, custom_value + 1, 2))  # 1, 3, 5, 7, 9, ..., 19
                    elif custom_value <= 50:
                        return list(range(1, custom_value + 1, 5))  # 1, 6, 11, 16, ..., 
                    else:
                        step = max(5, custom_value // 10)
                        return list(range(1, custom_value + 1, step))
                else:
                    return list(range(1, custom_value + 1))
    
    # Default ranges
    if "fibonacci" in algorithm_name:
        full_range = list(range(1, 51))  # Fibonacci: 1 to 50
    elif "selection_sort" in algorithm_name:
        full_range = [1, 5, 10, 20, 30, 50, 75, 100, 150, 200]  # Selection Sort: reasonable sizes starting from 1
    else:
        full_range = list(range(1, 51))  # Default: 1 to 50
    
    # If max_values is specified, limit the amount
    if max_values is not None and max_values > 0:
        # For uniform ranges like fibonacci, take evenly distributed values
        if "fibonacci" in algorithm_name:
            step = max(1, len(full_range) // max_values)
            return full_range[::step][:max_values]
        else:
            # For selection sort, take the first max_values
            return full_range[:max_values]
    
    return full_range


def get_original_n_values_from_file(py_file):
    """Extract original n values from Python file for verification"""
    try:
        with open(py_file, 'r') as f:
            content = f.read()
        
        if "fibonacci_iterative" in py_file.name:
            # Look for pattern "values = [1, 5, 10, ...]"
            match = re.search(r'values\s*=\s*\[([\d,\s]+)\]', content)
            if match:
                values_str = match.group(1)
                return [int(x.strip()) for x in values_str.split(',')]
        elif "fibonacci_recursive" in py_file.name:
            match = re.search(r'values\s*=\s*\[([\d,\s]+)\]', content)
            if match:
                values_str = match.group(1)
                return [int(x.strip()) for x in values_str.split(',')]
        elif "selection_sort" in py_file.name:
            match = re.search(r'sizes\s*=\s*\[([\d,\s]+)\]', content)
            if match:
                values_str = match.group(1)
                return [int(x.strip()) for x in values_str.split(',')]
        
        return []
    except Exception as e:
        print(f"   ⚠️  Error reading original values from {py_file.name}: {e}")
        return []


def cleanup_generated_files(output_dir):
    """Clean up temporary files and directories"""
    if output_dir.exists():
        shutil.rmtree(output_dir)


def check_manual_cpp_file_exists(algorithm_name):
    """Check if corresponding manual C++ file exists for an algorithm"""
    cpp_manual_dir = Path("src/benchmarks/cpp_manual")
    
    if "fibonacci_iterative" in algorithm_name:
        manual_file = cpp_manual_dir / "fibonacci_iterative.cpp"
    elif "fibonacci_recursive" in algorithm_name:
        manual_file = cpp_manual_dir / "fibonacci_recursive.cpp"
    elif "selection_sort" in algorithm_name:
        manual_file = cpp_manual_dir / "selection_sort.cpp"
    else:
        return False
    
    return manual_file.exists()