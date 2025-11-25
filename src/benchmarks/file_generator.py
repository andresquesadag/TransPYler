"""
File Generation Module
Copies original source files for command-line argument based benchmarking
"""

import shutil
from pathlib import Path
from src.benchmarks.config import get_manual_cpp_file_path


def modify_python_for_args(content, algorithm_name):
    """Modify Python content to accept command line arguments"""
    import sys
    
    if "fibonacci" in algorithm_name:
        # Replace hardcoded number = 25 with command line argument
        content = content.replace(
            "number = 25",
            "import sys\nif len(sys.argv) != 2:\n    print('Usage: python', sys.argv[0], '<n>')\n    sys.exit(1)\nnumber = int(sys.argv[1])"
        )
    elif "selection_sort" in algorithm_name:
        # Replace hardcoded n = 100 with command line argument
        content = content.replace(
            "n = 100",
            "import sys\nif len(sys.argv) != 2:\n    print('Usage: python', sys.argv[0], '<n>')\n    sys.exit(1)\nn = int(sys.argv[1])"
        )
    
    return content


def copy_python_original(original_file, output_dir):
    """Create a modified Python file that accepts command line arguments"""
    algorithm_name = original_file.stem
    algorithm_clean = algorithm_name.replace("_python", "")
    
    # Create descriptive filename
    output_file = output_dir / f"{algorithm_clean}_python_original.py"
    
    # Read the original file
    with open(original_file, 'r') as f:
        content = f.read()
    
    # Modify content to accept command line arguments
    content = modify_python_for_args(content, algorithm_clean)
    
    # Write the modified content
    with open(output_file, 'w') as f:
        f.write(content)
    
    return output_file


def copy_cpp_manual(algorithm_name, output_dir):
    """Copy the original manual C++ file to output directory"""
    original_cpp = get_manual_cpp_file_path(algorithm_name)
    
    print(f"  Looking for manual C++: {original_cpp}")
    
    if not original_cpp:
        print(f"  ✗ No manual C++ configuration found for {algorithm_name}")
        return None
        
    if not original_cpp.exists():
        print(f"  ✗ Manual C++ file not found: {original_cpp}")
        return None
    
    algorithm_clean = algorithm_name.replace("_python", "")
    
    # Create descriptive filename
    output_file = output_dir / f"{algorithm_clean}_cpp_manual_original.cpp"
    
    # Simply copy the file
    shutil.copy2(original_cpp, output_file)
    print(f"  ✓ Manual C++: {output_file.name}")
    
    return output_file


def create_transpiled_cpp_file(transpiled_cpp, output_dir, algorithm_name):
    """Copy transpiled C++ file to output directory"""
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
