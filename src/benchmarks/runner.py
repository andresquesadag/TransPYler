"""
Performance Benchmark Runner
----------------------------
System for executing and measuring the performance of Python,
transpiled C++, and hand-written C++ programs.

Features:
- Execution time measurement
- Comparison between Python, transpiled C++, and manual C++
- Multiple iterations for averaging
- Export results to CSV and JSON
"""

import time
import subprocess
import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import sys

# Add src to path to import the transpiler
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.compiler.transpiler import Transpiler


@dataclass
class BenchmarkResult:
    """Result of an individual benchmark."""
    program_name: str
    language: str  # 'python', 'cpp_transpiled', 'cpp_manual'
    input_size: int
    execution_time: float  # in seconds
    iterations: int
    output: str = ""
    
    def to_dict(self):
        return asdict(self)


class BenchmarkRunner:
    """Executes and measures program performance."""
    
    def __init__(self, programs_dir: str = None, output_dir: str = None):
        """
        Initialize the benchmark runner.
        
        Args:
            programs_dir: Directory where test programs are located
            output_dir: Directory where to save results
        """
        if programs_dir is None:
            programs_dir = Path(__file__).parent / "programs"
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        
        self.programs_dir = Path(programs_dir)
        self.output_dir = Path(output_dir)
        
        # Create organized directory structure
        self.build_dir = Path(__file__).parent / "build"
        self.graphs_dir = self.output_dir / "graphs"
        self.raw_data_dir = self.output_dir / "raw"
        
        # Create base directories
        for directory in [self.build_dir, self.output_dir, self.graphs_dir, self.raw_data_dir]:
            directory.mkdir(exist_ok=True, parents=True)
        
        self.transpiler = Transpiler()
        self.runtime_path = Path(__file__).parent.parent / "runtime" / "cpp"
        
        self.results: List[BenchmarkResult] = []
    
    def _get_program_build_dirs(self, program_name: str) -> Dict[str, Path]:
        """
        Get build directories for a specific program.
        Creates subdirectories: build/{program}/transpiled/ and build/{program}/executables/
        
        Args:
            program_name: Name of the program (e.g., 'fibonacci_recursivo')
            
        Returns:
            Dictionary with 'transpiled' and 'executables' paths
        """
        program_build = self.build_dir / program_name
        transpiled_dir = program_build / "transpiled"
        executables_dir = program_build / "executables"
        
        # Create directories
        transpiled_dir.mkdir(exist_ok=True, parents=True)
        executables_dir.mkdir(exist_ok=True, parents=True)
        
        return {
            'transpiled': transpiled_dir,
            'executables': executables_dir
        }
    
    def run_python_with_value(self, fangless_file: Path, value: int, 
                             iterations: int = 3, timeout: int = 300) -> float:
        """
        Execute Python code with a specific hardcoded value.
        
        Args:
            fangless_file: Path to the _fangless.py file
            value: Value to hardcode (replaces n=10 or size=100)
            iterations: Number of times to run for averaging
            timeout: Timeout in seconds (default 5 minutes)
            
        Returns:
            Average execution time in seconds
        """
        import re
        
        # Read source code
        with open(fangless_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Replace hardcoded value
        if "n = " in source_code:
            source_code = re.sub(r'n = \d+', f'n = {value}', source_code)
        elif "size = " in source_code:
            source_code = re.sub(r'size = \d+', f'size = {value}', source_code)
        else:
            raise ValueError(f"Could not find 'n =' or 'size =' pattern in {fangless_file}")
        
        # Execute multiple times and average
        times = []
        for _ in range(iterations):
            start = time.time()
            try:
                result = subprocess.run(
                    ["python", "-c", source_code],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                elapsed = time.time() - start
                times.append(elapsed)
            except subprocess.TimeoutExpired:
                print(f"      ⏱️  TIMEOUT after {timeout}s")
                return float('inf')  # Return infinity for timeout
        
        return sum(times) / len(times)
    
    def transpile_and_compile_with_value(self, program_name: str, fangless_file: Path, 
                                        value: int, build_dirs: Dict[str, Path]) -> Path:
        """
        Transpile Python to C++ with a specific value and compile.
        
        Args:
            program_name: Name of the program
            fangless_file: Path to the _fangless.py file
            value: Value to hardcode
            build_dirs: Dictionary with 'transpiled' and 'executables' paths
            
        Returns:
            Path to the compiled executable
        """
        import re
        
        # Read source code
        with open(fangless_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Replace hardcoded value
        # First try to find the pattern - check for hardcoded integer values
        n_pattern = re.search(r'n = (\d+)(?!\s*\+|\s*-|\s*\*|\s*/)', source_code)
        size_pattern = re.search(r'size = (\d+)(?!\s*\+|\s*-|\s*\*|\s*/)', source_code)
        
        if size_pattern:
            # Prefer 'size' if found
            source_code = re.sub(r'size = \d+', f'size = {value}', source_code)
            var_name = "size"
        elif n_pattern:
            # Use 'n' if found and it's a hardcoded value
            source_code = re.sub(r'n = \d+(?!\s*\+|\s*-|\s*\*|\s*/)', f'n = {value}', source_code)
            var_name = "n"
        else:
            raise ValueError(f"Could not find 'n = <number>' or 'size = <number>' pattern in {fangless_file}")
        
        # Transpile to C++
        cpp_filename = f"{program_name}_{var_name}{value}.cpp"
        cpp_file = build_dirs['transpiled'] / cpp_filename
        
        self.transpiler.transpile(source_code, str(cpp_file))
        
        # Compile
        exe_filename = f"{program_name}_{var_name}{value}.exe"
        exe_file = build_dirs['executables'] / exe_filename
        
        success = self.compile_cpp(cpp_file, exe_file, use_runtime=True)
        
        if not success:
            raise RuntimeError(f"Failed to compile {cpp_file}")
        
        return exe_file
    
    def run_cpp_executable(self, exe_file: Path, iterations: int = 3, 
                          timeout: int = 300, args: List[str] = None) -> float:
        """
        Execute a C++ executable and measure time.
        
        Args:
            exe_file: Path to executable
            iterations: Number of times to run for averaging
            timeout: Timeout in seconds
            args: Command-line arguments to pass to the executable
            
        Returns:
            Average execution time in seconds
        """
        if args is None:
            args = []
        
        cmd = [str(exe_file)] + [str(a) for a in args]
        
        times = []
        for _ in range(iterations):
            start = time.time()
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                elapsed = time.time() - start
                times.append(elapsed)
            except subprocess.TimeoutExpired:
                print(f"      ⏱️  TIMEOUT after {timeout}s")
                return float('inf')
        
        return sum(times) / len(times)
    
    def run_python(self, python_file: Path, args: List[str] = None, 
                   iterations: int = 5) -> BenchmarkResult:
        """
        Execute a Python program and measure its time.
        
        Args:
            python_file: Python file to execute
            args: Command line arguments
            iterations: Number of executions to average
            
        Returns:
            BenchmarkResult with the results
        """
        if args is None:
            args = []
        
        cmd = ["python3", str(python_file)] + [str(a) for a in args]
        
        times = []
        output = ""
        
        for _ in range(iterations):
            start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end = time.time()
            
            times.append(end - start)
            if not output:
                output = result.stdout.strip()
        
        avg_time = sum(times) / len(times)
        input_size = int(args[0]) if args else 0
        
        return BenchmarkResult(
            program_name=python_file.stem,
            language="python",
            input_size=input_size,
            execution_time=avg_time,
            iterations=iterations,
            output=output
        )
    
    def compile_cpp(self, cpp_file: Path, output_exe: Path, 
                    use_runtime: bool = False) -> bool:
        """
        Compile a C++ file.
        
        Args:
            cpp_file: C++ file to compile
            output_exe: Output executable name
            use_runtime: If True, includes the DynamicType runtime
            
        Returns:
            True if compilation was successful
        """
        cmd = [
            "g++", "-std=c++17", "-O3",  # -O3 for maximum optimization
            str(cpp_file)
        ]
        
        if use_runtime:
            cmd.extend([
                "-I", str(self.runtime_path),
                str(self.runtime_path / "DynamicType.cpp"),
                str(self.runtime_path / "builtins.cpp")
            ])
        
        cmd.extend(["-o", str(output_exe)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Compilation error for {cpp_file}:")
            print(result.stderr)
            return False
        
        return True
    
    def run_cpp(self, exe_file: Path, args: List[str] = None,
                iterations: int = 5) -> BenchmarkResult:
        """
        Execute a C++ executable and measure its time.
        
        Args:
            exe_file: Executable to run
            args: Command line arguments
            iterations: Number of executions to average
            
        Returns:
            BenchmarkResult with the results
        """
        if args is None:
            args = []
        
        cmd = [str(exe_file)] + [str(a) for a in args]
        
        times = []
        output = ""
        
        for _ in range(iterations):
            start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end = time.time()
            
            times.append(end - start)
            if not output:
                output = result.stdout.strip()
        
        avg_time = sum(times) / len(times)
        input_size = int(args[0]) if args else 0
        
        return BenchmarkResult(
            program_name=exe_file.stem,
            language="cpp",
            input_size=input_size,
            execution_time=avg_time,
            iterations=iterations,
            output=output
        )
    
    def transpile_and_compile(self, python_file: Path, input_value: int) -> Path:
        """
        Transpile a Python program to C++ and compile it.
        Modifies the input value in the code before transpiling.
        
        Args:
            python_file: Python file to transpile (should be _simple.py version)
            input_value: The input value to hardcode in the program
            
        Returns:
            Path to the compiled executable
        """
        # Read Python code
        with open(python_file, 'r') as f:
            source_code = f.read()
        
        # Replace the hardcoded value with the actual input
        # Look for patterns like "n = 10" or "size = 100" and replace
        if "n = " in source_code:
            # Replace "n = <number>" with "n = input_value"
            import re
            source_code = re.sub(r'n = \d+', f'n = {input_value}', source_code)
        elif "size = " in source_code:
            # Replace "size = <number>" with "size = input_value"
            import re
            source_code = re.sub(r'size = \d+', f'size = {input_value}', source_code)
        
        # Transpile to C++
        cpp_file = self.output_dir / f"{python_file.stem}_transpiled_{input_value}.cpp"
        self.transpiler.transpile(source_code, str(cpp_file))
        
        # Compile
        exe_file = self.output_dir / f"{python_file.stem}_transpiled_{input_value}"
        success = self.compile_cpp(cpp_file, exe_file, use_runtime=True)
        
        if not success:
            raise RuntimeError(f"Failed to compile transpiled {python_file}")
        
        return exe_file
    
    def compile_manual_cpp(self, cpp_file: Path) -> Path:
        """
        Compile a hand-written C++ file.
        
        Args:
            cpp_file: C++ file to compile
            
        Returns:
            Path to the compiled executable
        """
        exe_file = self.output_dir / cpp_file.stem
        success = self.compile_cpp(cpp_file, exe_file, use_runtime=False)
        
        if not success:
            raise RuntimeError(f"Failed to compile {cpp_file}")
        
        return exe_file
    
    def benchmark_algorithm(self, program_name: str, input_values: List[int],
                           iterations: int = 3) -> List[BenchmarkResult]:
        """
        Complete benchmark for one algorithm across all input values.
        Tests Python, C++ Transpiled, and C++ Manual versions.
        
        Args:
            program_name: Name of the program (e.g., 'fibonacci_recursivo')
            input_values: List of input values to test (e.g., [1, 2, 3, ..., 50])
            iterations: Number of executions per test for averaging
            
        Returns:
            List of BenchmarkResult objects
        """
        results = []
        
        # Setup paths
        program_dir = self.programs_dir / program_name
        fangless_file = program_dir / f"{program_name}_fangless.py"
        manual_cpp_file = program_dir / f"{program_name}_manual.cpp"
        
        # Get build directories
        build_dirs = self._get_program_build_dirs(program_name)
        
        print(f"\n{'='*80}")
        print(f" BENCHMARKING: {program_name}")
        print(f"{'='*80}")
        print(f"Input values: {len(input_values)} values from {min(input_values)} to {max(input_values)}")
        print(f"Iterations per test: {iterations}")
        print()
        
        # Compile C++ manual version (ONCE)
        print("[BUILD] Compiling C++ manual version...")
        manual_exe = build_dirs['executables'] / f"{program_name}_manual.exe"
        success = self.compile_cpp(manual_cpp_file, manual_exe, use_runtime=False)
        if not success:
            raise RuntimeError(f"Failed to compile {manual_cpp_file}")
        print(f"   [OK] Compiled: {manual_exe.name}")
        print()
        
        # Benchmark each input value
        for idx, value in enumerate(input_values, 1):
            print(f"[{idx}/{len(input_values)}] Testing with input = {value}")
            
            # === 1. PYTHON ===
            print(f"  [PY] Python Fangless...", end=" ", flush=True)
            try:
                python_time = self.run_python_with_value(fangless_file, value, iterations)
                if python_time == float('inf'):
                    print("TIMEOUT")
                else:
                    print(f"{python_time:.6f}s")
                
                results.append(BenchmarkResult(
                    program_name=program_name,
                    language="python",
                    input_size=value,
                    execution_time=python_time,
                    iterations=iterations
                ))
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(BenchmarkResult(
                    program_name=program_name,
                    language="python",
                    input_size=value,
                    execution_time=float('inf'),
                    iterations=0,
                    output=f"ERROR: {e}"
                ))
            
            # === 2. C++ TRANSPILED ===
            print(f"  [C++T] C++ Transpiled...", end=" ", flush=True)
            try:
                # Transpile and compile
                cpp_exe = self.transpile_and_compile_with_value(
                    program_name, fangless_file, value, build_dirs
                )
                
                # Execute and measure
                cpp_trans_time = self.run_cpp_executable(cpp_exe, iterations)
                if cpp_trans_time == float('inf'):
                    print("TIMEOUT")
                else:
                    print(f"{cpp_trans_time:.6f}s")
                
                results.append(BenchmarkResult(
                    program_name=program_name,
                    language="cpp_transpiled",
                    input_size=value,
                    execution_time=cpp_trans_time,
                    iterations=iterations
                ))
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(BenchmarkResult(
                    program_name=program_name,
                    language="cpp_transpiled",
                    input_size=value,
                    execution_time=float('inf'),
                    iterations=0,
                    output=f"ERROR: {e}"
                ))
            
            # === 3. C++ MANUAL ===
            print(f"  [C++M] C++ Manual...", end=" ", flush=True)
            try:
                # Manual C++ accepts command-line arguments
                cpp_manual_time = self.run_cpp_executable(manual_exe, iterations, args=[value])
                if cpp_manual_time == float('inf'):
                    print("TIMEOUT")
                else:
                    print(f"{cpp_manual_time:.6f}s")
                
                results.append(BenchmarkResult(
                    program_name=program_name,
                    language="cpp_manual",
                    input_size=value,
                    execution_time=cpp_manual_time,
                    iterations=iterations
                ))
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(BenchmarkResult(
                    program_name=program_name,
                    language="cpp_manual",
                    input_size=value,
                    execution_time=float('inf'),
                    iterations=0,
                    output=f"ERROR: {e}"
                ))
            
            # Show speedup
            if python_time != float('inf') and cpp_trans_time != float('inf'):
                speedup_trans = python_time / cpp_trans_time
                print(f"     Speedup (transpiled): {speedup_trans:.2f}x")
            if python_time != float('inf') and cpp_manual_time != float('inf'):
                speedup_manual = python_time / cpp_manual_time
                print(f"     Speedup (manual): {speedup_manual:.2f}x")
            print()
        
        print(f"{'='*80}")
        print(f" COMPLETED: {program_name}")
        print(f"{'='*80}\n")
        
        self.results.extend(results)
        return results
    
    def benchmark_program(self, program_name: str, input_sizes: List[int],
                         iterations: int = 5) -> List[BenchmarkResult]:
        """
        Run complete benchmark of a program in all 3 versions.
        This is a wrapper around benchmark_algorithm for backward compatibility.
        
        Args:
            program_name: Base name of the program (without extension)
            input_sizes: List of input sizes to test
            iterations: Number of executions per test
            
        Returns:
            List of BenchmarkResults
        """
        # Simply call the updated benchmark_algorithm method
        return self.benchmark_algorithm(program_name, input_sizes, iterations)
    
    def save_results(self, filename: str = "benchmark_results"):
        """
        Save results to CSV and JSON.
        
        Args:
            filename: Base name for the file (without extension)
        """
        # Save as CSV
        csv_file = self.output_dir / f"{filename}.csv"
        with open(csv_file, 'w', newline='') as f:
            if self.results:
                writer = csv.DictWriter(f, fieldnames=self.results[0].to_dict().keys())
                writer.writeheader()
                for result in self.results:
                    writer.writerow(result.to_dict())
        
        print(f"\nResults saved to {csv_file}")
        
        # Save as JSON
        json_file = self.output_dir / f"{filename}.json"
        with open(json_file, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)
        
        print(f"Results saved to {json_file}")
    
    def print_summary(self):
        """Print a summary of the results."""
        if not self.results:
            print("No results to display")
            return
        
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        
        # Group by program
        programs = {}
        for result in self.results:
            if result.program_name not in programs:
                programs[result.program_name] = {}
            if result.input_size not in programs[result.program_name]:
                programs[result.program_name][result.input_size] = {}
            programs[result.program_name][result.input_size][result.language] = result
        
        for program_name, sizes in programs.items():
            print(f"\n{program_name}:")
            print("-" * 80)
            print(f"{'Size':<10} {'Python (s)':<15} {'C++ Trans (s)':<15} {'C++ Manual (s)':<15} {'Speedup Trans':<15} {'Speedup Manual':<15}")
            print("-" * 80)
            
            for size in sorted(sizes.keys()):
                results_dict = sizes[size]
                py = results_dict.get('python')
                cpp_t = results_dict.get('cpp_transpiled')
                cpp_m = results_dict.get('cpp_manual')
                
                if py and cpp_t and cpp_m:
                    speedup_t = py.execution_time / cpp_t.execution_time
                    speedup_m = py.execution_time / cpp_m.execution_time
                    
                    print(f"{size:<10} {py.execution_time:<15.6f} {cpp_t.execution_time:<15.6f} "
                          f"{cpp_m.execution_time:<15.6f} {speedup_t:<15.2f}x {speedup_m:<15.2f}x")


if __name__ == "__main__":
    print("Performance Benchmark Runner")
    print("=" * 60)
    
    runner = BenchmarkRunner()
    
    # Note: Will be executed from a dedicated script
    print("Use benchmark_suite.py to run complete benchmarks")