"""
Configuration Module
Central configuration for benchmark algorithms, patterns, and settings
"""

from pathlib import Path


# Algorithm configurations
ALGORITHM_CONFIGS = {
    'fibonacci_iterative': {
        'python_pattern': "values = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]",
        'cpp_pattern': "DynamicType(std::vector<DynamicType>{DynamicType(1), DynamicType(5), DynamicType(10), DynamicType(15), DynamicType(20), DynamicType(25), DynamicType(30), DynamicType(35), DynamicType(40), DynamicType(45), DynamicType(50)})",
        'manual_cpp_file': 'fibonacci_iterative.cpp',
        'default_range': list(range(1, 121))
    },
    'fibonacci_recursive': {
        'python_pattern': "values = [1, 5, 10, 15, 20, 25, 30, 35]",
        'cpp_pattern': "DynamicType(std::vector<DynamicType>{DynamicType(1), DynamicType(5), DynamicType(10), DynamicType(15), DynamicType(20), DynamicType(25), DynamicType(30), DynamicType(35)})",
        'manual_cpp_file': 'fibonacci_recursive.cpp',
        'default_range': list(range(1, 46))
    },
    'selection_sort': {
        'python_pattern': "sizes = [10, 50, 100, 200, 300, 500, 750, 1000, 1250, 1500]",
        'cpp_pattern': "DynamicType(std::vector<DynamicType>{DynamicType(10), DynamicType(50), DynamicType(100), DynamicType(200), DynamicType(300), DynamicType(500), DynamicType(750), DynamicType(1000), DynamicType(1250), DynamicType(1500)})",
        'manual_cpp_file': 'selection_sort.cpp',
        'default_range': list(range(1, 51))
    }
}

# Directory paths
PATHS = {
    'benchmark_dir': Path(__file__).parent,
    'python_original': Path(__file__).parent / "python_transpiler_source",
    'cpp_manual': Path(__file__).parent / "cpp_manual",
    'transpiled_output': Path(__file__).parent / "transpiled_output",
    'results': Path("benchmark_results"),
    'project_root': Path(__file__).parent.parent.parent
}

# Compilation settings
COMPILE_SETTINGS = {
    'cpp_flags': ["-std=c++17", "-O2"],
    'runtime_includes': [
        "src/runtime/cpp",
        "src/runtime/cpp/DynamicType.cpp",
        "src/runtime/cpp/builtins.cpp"
    ]
}

# Performance test settings
PERFORMANCE_SETTINGS = {
    'measurement_rounds': 3,  # Number of measurements per test
    'timeout_seconds': 30     # Timeout for individual tests
}

# Benchmark suffix (can be set dynamically for version-specific runs)
BENCHMARK_SUFFIX = ""


def set_benchmark_suffix(suffix):
    """Set the suffix for benchmark output files (e.g., 'py310' for Python 3.10)"""
    global BENCHMARK_SUFFIX
    BENCHMARK_SUFFIX = f"_{suffix}" if suffix else ""


def get_benchmark_suffix():
    """Get the current benchmark suffix"""
    return BENCHMARK_SUFFIX


def get_algorithm_config(algorithm_name):
    """Get configuration for a specific algorithm"""
    for algo_key, config in ALGORITHM_CONFIGS.items():
        if algo_key in algorithm_name:
            return config
    return None


def get_manual_cpp_file_path(algorithm_name):
    """Get the path to the manual C++ file for an algorithm"""
    # Clean the algorithm name
    clean_name = algorithm_name.replace("_python", "").replace(".py", "")
    
    config = get_algorithm_config(clean_name)
    if config:
        cpp_file_path = PATHS['cpp_manual'] / config['manual_cpp_file']
        return cpp_file_path
    return None