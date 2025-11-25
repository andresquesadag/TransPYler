"""
Transpiler Interface Module
Handles transpilation and compilation of Python files to C++ executables
"""

import sys
import subprocess
import shutil

# TODO(any): Path and get_manual_cpp_file_path imports might be redundant
from pathlib import Path

from src.benchmarks.config import PATHS, COMPILE_SETTINGS, get_manual_cpp_file_path
from src.benchmarks.file_generator import (
    copy_python_original,
    copy_cpp_manual,
    create_transpiled_cpp_file,
    modify_transpiled_for_args,
)
from src.benchmarks.utilities import (
    generate_n_values_for_algorithm,
    check_manual_cpp_file_exists,
)


def transpile_file(py_file, output_cpp_file):
    """Transpile a single Python file to C++"""
    cmd = [
        sys.executable,
        "-m",
        "src.tools.transpile_cli",
        str(py_file),
        "-o",
        str(output_cpp_file),
    ]
    result = subprocess.run(
        cmd, capture_output=True, cwd=PATHS["project_root"], check=False
    )
    return result


def compile_cpp_transpiled(cpp_file, executable_path):
    """Compile transpiled C++ file with runtime dependencies"""
    compile_cmd = [
        "g++",
        *COMPILE_SETTINGS["cpp_flags"],
        "-I",
        str(PATHS["project_root"] / COMPILE_SETTINGS["runtime_includes"][0]),
        str(cpp_file),
        str(PATHS["project_root"] / COMPILE_SETTINGS["runtime_includes"][1]),
        str(PATHS["project_root"] / COMPILE_SETTINGS["runtime_includes"][2]),
        "-o",
        str(executable_path),
    ]
    result = subprocess.run(compile_cmd, capture_output=True, cwd=PATHS["project_root"], check=False)
    return result


def compile_cpp_manual(cpp_file, executable_path):
    """Compile manual C++ file (standalone)"""
    compile_cmd = [
        "g++",
        *COMPILE_SETTINGS["cpp_flags"],
        str(cpp_file),
        "-o",
        str(executable_path),
    ]
    result = subprocess.run(compile_cmd, capture_output=True, cwd=PATHS["project_root"], check=False)
    return result

# TODO(any): fast_mode is currently unused
def generate_all_transpiled_files(fast_mode=False, max_values=None, custom_values=None):
    """Phase 1: Generate single transpiled version per algorithm (accepts command line args)"""
    print("\nPhase 1: Generating transpiled files")
    print("-" * 40)

    output_dir = PATHS["transpiled_output"]

    # Clean and create directories
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Find Python files
    python_files = list(PATHS["python_original"].glob("*.py"))

    generated_files = {}

    for py_file in python_files:
        print(f"Processing: {py_file.name}")

        algorithm_name = py_file.stem
        n_values = generate_n_values_for_algorithm(algorithm_name, max_values, custom_values)

        print(
            f"  Test values: {len(n_values)} points ({min(n_values)} to {max(n_values)})"
        )

        # Check for corresponding manual C++ file
        manual_exists = check_manual_cpp_file_exists(algorithm_name)
        print(f"  Manual C++: {'Found' if manual_exists else 'Not found'}")

        # Create directory for this algorithm
        algorithm_clean = algorithm_name.replace("_python", "")
        algo_dir = output_dir / f"{algorithm_clean}_files"
        algo_dir.mkdir(exist_ok=True)

        # Copy original Python file (now accepts command line args)
        python_copy = copy_python_original(py_file, algo_dir)
        print(f"  ✓ Python: {python_copy.name}")

        # Use special transpiler-compatible Python files
        transpiler_source_dir = PATHS["benchmark_dir"] / "python_transpiler_source"
        if "fibonacci_iterative" in algorithm_name:
            transpiler_py = transpiler_source_dir / "fibonacci_iterative.py"
        elif "fibonacci_recursive" in algorithm_name:
            transpiler_py = transpiler_source_dir / "fibonacci_recursive.py"
        elif "selection_sort" in algorithm_name:
            transpiler_py = transpiler_source_dir / "selection_sort.py"
        else:
            transpiler_py = py_file  # Fallback

        # Transpile using the transpiler-compatible file
        transpiled_cpp = algo_dir / f"{algorithm_clean}_transpiled.cpp"
        transpile_result = transpile_file(transpiler_py, transpiled_cpp)

        if transpile_result.returncode != 0:
            print(f"  ✗ Transpilation failed: {transpile_result.stderr.decode()}")
            continue

        # Modify transpiled C++ to accept command line arguments
        modify_transpiled_for_args(transpiled_cpp, algorithm_name)

        # Move transpiled file to descriptive location
        final_transpiled_cpp = create_transpiled_cpp_file(
            transpiled_cpp, algo_dir, algorithm_name
        )
        print(f"  ✓ Transpiled: {final_transpiled_cpp.name}")

        # Compile transpiled C++
        transpiled_exe = algo_dir / f"{algorithm_clean}_executable_transpiled"
        compile_result = compile_cpp_transpiled(final_transpiled_cpp, transpiled_exe)

        if compile_result.returncode != 0:
            print(
                f"  ✗ Transpiled compilation failed: {compile_result.stderr.decode()}"
            )
            continue
        print(f"  ✓ Transpiled executable: {transpiled_exe.name}")

        # Copy and compile manual C++ if available
        manual_exe = None
        if manual_exists:
            manual_cpp_copy = copy_cpp_manual(algorithm_name, algo_dir)
            if manual_cpp_copy:
                print(f"  ✓ Manual C++: {manual_cpp_copy.name}")

                # Compile manual C++
                manual_exe = algo_dir / f"{algorithm_clean}_executable_manual"
                manual_result = compile_cpp_manual(manual_cpp_copy, manual_exe)

                if manual_result.returncode == 0:
                    print(f"  ✓ Manual executable: {manual_exe.name}")
                else:
                    print(
                        f"  ✗ Manual compilation failed: {manual_result.stderr.decode()}"
                    )
                    manual_exe = None

        # Store file references
        generated_files[algorithm_name] = {
            "n_values": n_values,
            "python_original": python_copy,
            "cpp_transpiled": final_transpiled_cpp,
            "executable_transpiled": transpiled_exe,
            "executable_manual": manual_exe,
        }

        print("  ✓ Algorithm ready for testing")

    print(f"\nPhase 1 complete: {len(generated_files)} algorithms processed")
    return generated_files
