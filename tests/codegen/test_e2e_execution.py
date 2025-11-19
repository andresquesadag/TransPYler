"""
End-to-End Execution Tests
--------------------------
Tests that compile and execute the generated C++ code to validate correctness.
These tests verify that the transpiled code not only compiles but also
produces correct output when executed.
"""

import pytest
import tempfile
import os
import subprocess
from pathlib import Path
from src.compiler.transpiler import Transpiler


class TestEndToEndExecution:
    """Test complete execution pipeline from Python to C++ execution."""
    
    @pytest.fixture
    def transpiler(self):
        return Transpiler()
    
    @pytest.fixture
    def runtime_path(self):
        return Path("src/runtime/cpp")
    
    def compile_and_run(self, cpp_file, runtime_path):
        """Compile and execute C++ code, return output."""
        exe_file = cpp_file.replace('.cpp', '_exec')
        
        compile_cmd = [
            "g++", "-std=c++17", 
            "-I", str(runtime_path),
            cpp_file,
            str(runtime_path / "DynamicType.cpp"),
            str(runtime_path / "builtins.cpp"),
            "-o", exe_file
        ]
        
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
        
        if compile_result.returncode != 0:
            return None, compile_result.stderr, compile_result.returncode
        
        run_result = subprocess.run([f"./{exe_file}"], capture_output=True, text=True, timeout=5)
        
        # Cleanup
        if os.path.exists(exe_file):
            os.remove(exe_file)
        
        return run_result.stdout, run_result.stderr, run_result.returncode
    
    def test_factorial_execution(self, transpiler, runtime_path):
        """Test factorial function execution produces correct output."""
        source = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
print(factorial(6))
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_factorial.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        assert "120" in lines[0]  # 5! = 120
        assert "720" in lines[1]  # 6! = 720
        
        os.remove(cpp_file)
    
    def test_fibonacci_execution(self, transpiler, runtime_path):
        """Test Fibonacci sequence generation."""
        source = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

for i in range(8):
    print(fib(i))
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_fib.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        
        # Expected: 0, 1, 1, 2, 3, 5, 8, 13
        expected = ["0", "1", "1", "2", "3", "5", "8", "13"]
        for i, exp in enumerate(expected):
            assert exp in lines[i]
        
        os.remove(cpp_file)
    
    def test_dynamic_typing_execution(self, transpiler, runtime_path):
        """Test dynamic typing works at runtime."""
        source = """
x = 10
print(x)
x = "hello"
print(x)
x = True
print(x)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_dynamic.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        assert "10" in lines[0]
        assert "hello" in lines[1]
        assert "1" in lines[2] or "true" in lines[2].lower()
        
        os.remove(cpp_file)
    
    def test_list_operations_execution(self, transpiler, runtime_path):
        """Test list operations execute correctly."""
        source = """
numbers = [1, 2, 3, 4, 5]
total = 0
for num in numbers:
    total = total + num
print(total)
print(len(numbers))
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_list.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        assert "15" in lines[0]  # Sum: 1+2+3+4+5 = 15
        assert "5" in lines[1]   # Length: 5
        
        os.remove(cpp_file)
    
    def test_conditional_logic_execution(self, transpiler, runtime_path):
        """Test conditional logic produces correct output."""
        source = """
def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print(classify(5))
print(classify(0))
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_cond.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        assert "positive" in lines[0]
        assert "zero" in lines[1]
        
        os.remove(cpp_file)
    
    def test_nested_loops_execution(self, transpiler, runtime_path):
        """Test nested loops produce correct output."""
        source = """
for i in range(3):
    for j in range(3):
        print(i * 3 + j)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_nested.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        
        # Should print 0 through 8
        for i in range(9):
            assert str(i) in lines[i]
        
        os.remove(cpp_file)
    
    def test_function_with_multiple_params(self, transpiler, runtime_path):
        """Test function with multiple parameters."""
        source = """
def calc(a, b, c):
    return a + b * c

result = calc(2, 3, 4)
print(result)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_params.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        assert "14" in stdout  # 2 + 3*4 = 14
        
        os.remove(cpp_file)
    
    def test_while_loop_execution(self, transpiler, runtime_path):
        """Test while loop execution."""
        source = """
i = 0
total = 0
while i < 5:
    total = total + i
    i = i + 1
print(total)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_while.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        assert "10" in stdout  # 0+1+2+3+4 = 10
        
        os.remove(cpp_file)
    
    def test_comparison_operators_execution(self, transpiler, runtime_path):
        """Test comparison operators produce correct boolean results."""
        source = """
a = 10
b = 20
print(a < b)
print(a > b)
print(a == b)
print(a != b)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_compare.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        # a < b: True
        assert "1" in lines[0] or "true" in lines[0].lower()
        # a > b: False
        assert "0" in lines[1] or "false" in lines[1].lower()
        # a == b: False
        assert "0" in lines[2] or "false" in lines[2].lower()
        # a != b: True
        assert "1" in lines[3] or "true" in lines[3].lower()
        
        os.remove(cpp_file)
    
    def test_logical_operators_execution(self, transpiler, runtime_path):
        """Test logical operators work correctly."""
        source = """
a = True
b = False
print(a and b)
print(a or b)
print(not a)
print(not b)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_logic.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        # a and b: False
        assert "0" in lines[0] or "false" in lines[0].lower()
        # a or b: True
        assert "1" in lines[1] or "true" in lines[1].lower()
        # not a: False
        assert "0" in lines[2] or "false" in lines[2].lower()
        # not b: True
        assert "1" in lines[3] or "true" in lines[3].lower()
        
        os.remove(cpp_file)
    
    def test_range_variants_execution(self, transpiler, runtime_path):
        """Test different range() variants."""
        source = """
for i in range(3):
    print(i)

for j in range(2, 5):
    print(j)

for k in range(0, 6, 2):
    print(k)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_range.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        
        # range(3): 0, 1, 2
        assert "0" in lines[0]
        assert "1" in lines[1]
        assert "2" in lines[2]
        
        # range(2, 5): 2, 3, 4
        assert "2" in lines[3]
        assert "3" in lines[4]
        assert "4" in lines[5]
        
        # range(0, 6, 2): 0, 2, 4
        assert "0" in lines[6]
        assert "2" in lines[7]
        assert "4" in lines[8]
        
        os.remove(cpp_file)
    
    def test_complex_program_execution(self, transpiler, runtime_path):
        """Test a complex program with multiple features."""
        source = """
def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i = i + 1
    return True

primes = []
for num in range(2, 11):
    if is_prime(num):
        print(num)
"""
        
        cpp_file = transpiler.transpile(source, "test_e2e_complex.cpp")
        stdout, stderr, retcode = self.compile_and_run(cpp_file, runtime_path)
        
        assert retcode == 0, f"Execution failed: {stderr}"
        lines = stdout.strip().split('\n')
        
        # Primes from 2 to 10: 2, 3, 5, 7
        assert "2" in lines[0]
        assert "3" in lines[1]
        assert "5" in lines[2]
        assert "7" in lines[3]
        
        os.remove(cpp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
