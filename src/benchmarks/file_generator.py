"""
File Generation Module
Copies original source files for command-line argument based benchmarking
"""

import shutil
from pathlib import Path
from src.benchmarks.config import get_manual_cpp_file_path


def copy_python_original(original_file, output_dir):
    """Copy the original Python file to output directory with descriptive name"""
    algorithm_name = original_file.stem
    algorithm_clean = algorithm_name.replace("_python", "")
    
    # Create descriptive filename
    output_file = output_dir / f"{algorithm_clean}_python_original.py"
    
    # Simply copy the file
    shutil.copy2(original_file, output_file)
    
    return output_file


def copy_cpp_manual(algorithm_name, output_dir):
    """Copy the original manual C++ file to output directory with descriptive name"""
    original_cpp = get_manual_cpp_file_path(algorithm_name)
    
    if not original_cpp or not original_cpp.exists():
        return None
    
    algorithm_clean = algorithm_name.replace("_python", "")
    
    # Create descriptive filename
    output_file = output_dir / f"{algorithm_clean}_cpp_manual_original.cpp"
    
    # Simply copy the file
    shutil.copy2(original_cpp, output_file)
    
    return output_file


def create_transpiled_cpp_file(transpiled_cpp, output_dir, algorithm_name):
    """Copy transpiled C++ file to output directory with descriptive name"""
    algorithm_clean = algorithm_name.replace("_python", "")
    
    # Create descriptive filename
    output_file = output_dir / f"{algorithm_clean}_cpp_transpiled.cpp"
    
    # Simply copy the file
    shutil.copy2(transpiled_cpp, output_file)
    
    return output_file


def modify_transpiled_for_args(transpiled_cpp, algorithm_name):
    """Modify transpiled C++ to accept command line arguments by replacing patterns"""
    with open(transpiled_cpp, 'r') as f:
        content = f.read()
    
    # Add necessary includes for command line arguments
    if '#include "builtins.hpp"' in content:
        content = content.replace(
            '#include "builtins.hpp"',
            '#include "builtins.hpp"\n#include <cstdlib>'
        )
    
    # Replace hardcoded values with argc/argv parsing
    if "fibonacci" in algorithm_name:
        # Replace number = 25 pattern
        content = content.replace(
            'DynamicType(25)',
            'DynamicType(atoi(argv[1]))'
        )
    elif "selection_sort" in algorithm_name:
        # Replace n = 100 pattern  
        content = content.replace(
            'DynamicType(100)',
            'DynamicType(atoi(argv[1]))'
        )
    
    # Modify main function signature to accept arguments
    content = content.replace(
        'int main() {',
        'int main(int argc, char* argv[]) {\n  if (argc != 2) { cout << "Usage: " << argv[0] << " <n>" << endl; return 1; }'
    )
    
    # Write back the modified content
    with open(transpiled_cpp, 'w') as f:
        f.write(content)
    
    return transpiled_cpp
