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
        self.output_dir.mkdir(exist_ok=True)
        
        self.transpiler = Transpiler()
        self.runtime_path = Path(__file__).parent.parent / "runtime" / "cpp"
        
        self.results: List[BenchmarkResult] = []
    
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
    
    def transpile_and_compile(self, python_file: Path) -> Path:
        """
        Transpile a Python program to C++ and compile it.
        
        Args:
            python_file: Python file to transpile
            
        Returns:
            Path to the compiled executable
        """
        # Read Python code
        with open(python_file, 'r') as f:
            source_code = f.read()
        
        # Transpile to C++
        cpp_file = self.output_dir / f"{python_file.stem}_transpiled.cpp"
        self.transpiler.transpile(source_code, str(cpp_file))
        
        # Compile
        exe_file = self.output_dir / f"{python_file.stem}_transpiled"
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
    
    def benchmark_program(self, program_name: str, input_sizes: List[int],
                         iterations: int = 5) -> List[BenchmarkResult]:
        """
        Run complete benchmark of a program in all 3 versions.
        
        Args:
            program_name: Base name of the program (without extension)
            input_sizes: List of input sizes to test
            iterations: Number of executions per test
            
        Returns:
            List of BenchmarkResults
        """
        results = []
        
        # Files
        python_file = self.programs_dir / f"{program_name}.py"
        cpp_manual_file = self.programs_dir / f"{program_name}_manual.cpp"
        
        print(f"\n{'='*60}")
        print(f"Benchmarking: {program_name}")
        print(f"{'='*60}")
        
        # Compile manual C++ version
        print("Compiling manual C++...")
        cpp_manual_exe = self.compile_manual_cpp(cpp_manual_file)
        
        # Transpile and compile Python version
        print("Transpiling and compiling Python to C++...")
        cpp_transpiled_exe = self.transpile_and_compile(python_file)
        
        # Run benchmarks for each input size
        for size in input_sizes:
            print(f"\nTesting with input size: {size}")
            
            # Python
            print("  Running Python...")
            py_result = self.run_python(python_file, [size], iterations)
            py_result.language = "python"
            results.append(py_result)
            print(f"    Time: {py_result.execution_time:.6f}s")
            
            # C++ Transpilado
            print("  Running C++ (transpiled)...")
            cpp_trans_result = self.run_cpp(cpp_transpiled_exe, [size], iterations)
            cpp_trans_result.program_name = program_name
            cpp_trans_result.language = "cpp_transpiled"
            results.append(cpp_trans_result)
            print(f"    Time: {cpp_trans_result.execution_time:.6f}s")
            
            # C++ Manual
            print("  Running C++ (manual)...")
            cpp_manual_result = self.run_cpp(cpp_manual_exe, [size], iterations)
            cpp_manual_result.program_name = program_name
            cpp_manual_result.language = "cpp_manual"
            results.append(cpp_manual_result)
            print(f"    Time: {cpp_manual_result.execution_time:.6f}s")
            
            # Show speedup
            speedup_trans = py_result.execution_time / cpp_trans_result.execution_time
            speedup_manual = py_result.execution_time / cpp_manual_result.execution_time
            print(f"    Speedup (transpiled): {speedup_trans:.2f}x")
            print(f"    Speedup (manual): {speedup_manual:.2f}x")
        
        self.results.extend(results)
        return results
    
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