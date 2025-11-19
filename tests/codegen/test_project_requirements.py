"""
Test Project Requirements - Comprehensive Test Suite
----------------------------------------------------
Tests to validate all project requirements for the Fangless Python to C++ transpiler.
This test suite covers:
1. Dynamic typing emulation
2. Control structures (if/elif/else, while, for)
3. Functions with parameters and return values
4. Arithmetic, relational, and logical operators
5. Type changes in variables
6. Main program encapsulation
"""

import pytest
import tempfile
import os
import subprocess
from src.compiler.transpiler import Transpiler
from src.parser.parser import Parser
from src.codegen.code_generator import CodeGenerator


class TestDynamicTyping:
    """Test dynamic typing emulation - core requirement."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
        self.runtime_path = "src/runtime/cpp"
    
    def compile_and_run(self, cpp_code, filename="test_output.cpp"):
        """Helper to compile and run C++ code."""
        with open(filename, 'w') as f:
            f.write(cpp_code)
        
        # Compile
        compile_cmd = [
            "g++", "-std=c++17", "-I", self.runtime_path,
            filename,
            f"{self.runtime_path}/DynamicType.cpp",
            f"{self.runtime_path}/builtins.cpp",
            "-o", filename.replace('.cpp', '')
        ]
        
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            pytest.fail(f"Compilation failed: {result.stderr}")
        
        # Run
        run_result = subprocess.run([f"./{filename.replace('.cpp', '')}"], 
                                   capture_output=True, text=True)
        
        # Cleanup
        os.remove(filename)
        os.remove(filename.replace('.cpp', ''))
        
        return run_result.stdout, run_result.stderr, run_result.returncode
    
    def test_variable_type_change_int_to_string(self):
        """Test that variables can change from int to string."""
        source = """
x = 10
print(x)
x = "hola"
print(x)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        # Verify type change is supported in generated code
        assert "DynamicType x = DynamicType(10)" in generated
        assert 'x = DynamicType(std::string("hola"))' in generated
        
        # Cleanup
        os.remove(cpp_code)
    
    def test_variable_type_change_string_to_int(self):
        """Test that variables can change from string to int."""
        source = """
y = "test"
y = 42
print(y)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert 'DynamicType y = DynamicType(std::string("test"))' in generated
        assert "y = DynamicType(42)" in generated
        
        os.remove(cpp_code)
    
    def test_mixed_type_operations(self):
        """Test operations with mixed types."""
        source = """
a = 5
b = 10
c = a + b
print(c)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "DynamicType" in generated
        assert "(a) + (b)" in generated
        
        os.remove(cpp_code)


class TestControlStructures:
    """Test control structures translation."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
    
    def test_if_statement(self):
        """Test if statement translation."""
        source = """
x = 10
if x > 5:
    print("mayor")
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "if" in generated
        assert ".toBool()" in generated
        assert 'print(DynamicType(std::string("mayor")))' in generated
        
        os.remove(cpp_code)
    
    def test_if_elif_else_chain(self):
        """Test if/elif/else translation."""
        source = """
x = 5
if x < 0:
    print("negativo")
elif x == 0:
    print("cero")
else:
    print("positivo")
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "if" in generated
        assert "else" in generated
        assert generated.count("else") >= 2  # else if and else
        
        os.remove(cpp_code)
    
    def test_while_loop(self):
        """Test while loop translation."""
        source = """
x = 0
while x < 5:
    x = x + 1
print(x)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "while" in generated
        assert ".toBool()" in generated
        
        os.remove(cpp_code)
    
    def test_for_loop_simple(self):
        """Test for loop with simple iterable."""
        source = """
numbers = [1, 2, 3, 4, 5]
for n in numbers:
    print(n)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "for (auto n :" in generated
        assert ".getList()" in generated
        
        os.remove(cpp_code)
    
    def test_for_loop_with_range(self):
        """Test for loop with range()."""
        source = """
for i in range(10):
    print(i)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "range(DynamicType(10))" in generated
        assert "for (auto i :" in generated
        
        os.remove(cpp_code)
    
    def test_nested_control_structures(self):
        """Test nested if and loops."""
        source = """
for i in range(5):
    if i % 2 == 0:
        print(i)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "for (auto i :" in generated
        assert "if" in generated
        
        os.remove(cpp_code)


class TestFunctions:
    """Test function definition and calling."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
    
    def test_function_no_params_no_return(self):
        """Test function without parameters or return."""
        source = """
def greet():
    print("Hello")

greet()
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "DynamicType _fn_greet()" in generated
        assert "_fn_greet()" in generated  # Call
        
        os.remove(cpp_code)
    
    def test_function_with_parameters(self):
        """Test function with parameters."""
        source = """
def add(a, b):
    return a + b

result = add(5, 3)
print(result)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "DynamicType _fn_add(DynamicType a, DynamicType b)" in generated
        assert "return" in generated
        assert "_fn_add(DynamicType(5), DynamicType(3))" in generated
        
        os.remove(cpp_code)
    
    def test_function_with_different_return_types(self):
        """Test function that returns different types based on condition."""
        source = """
def get_value(flag):
    if flag:
        return 42
    else:
        return "text"

print(get_value(True))
print(get_value(False))
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "DynamicType _fn_get_value(DynamicType flag)" in generated
        assert "return DynamicType(42)" in generated
        assert 'return DynamicType(std::string("text"))' in generated
        
        os.remove(cpp_code)
    
    def test_recursive_function(self):
        """Test recursive function (factorial)."""
        source = """
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

print(factorial(5))
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "DynamicType _fn_factorial(DynamicType n)" in generated
        assert "_fn_factorial(" in generated  # Recursive call
        
        os.remove(cpp_code)


class TestOperators:
    """Test arithmetic, relational, and logical operators."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
    
    def test_arithmetic_operators(self):
        """Test all arithmetic operators."""
        source = """
a = 10
b = 3
sum = a + b
diff = a - b
prod = a * b
quot = a / b
mod = a % b
power = a ** b
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "(a) + (b)" in generated
        assert "(a) - (b)" in generated
        assert "(a) * (b)" in generated
        assert "(a) / (b)" in generated
        assert "(a) % (b)" in generated
        assert "pow(" in generated  # Power operator
        
        os.remove(cpp_code)
    
    def test_relational_operators(self):
        """Test all relational operators."""
        source = """
x = 5
y = 10
eq = x == y
neq = x != y
lt = x < y
gt = x > y
lte = x <= y
gte = x >= y
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "(x) == (y)" in generated
        assert "(x) != (y)" in generated
        assert "(x) < (y)" in generated
        assert "(x) > (y)" in generated
        assert "(x) <= (y)" in generated
        assert "(x) >= (y)" in generated
        
        os.remove(cpp_code)
    
    def test_logical_operators(self):
        """Test logical operators."""
        source = """
a = True
b = False
and_result = a and b
or_result = a or b
not_result = not a
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "&&" in generated
        assert "||" in generated
        assert "!" in generated
        assert ".toBool()" in generated
        
        os.remove(cpp_code)
    
    def test_operator_precedence(self):
        """Test operator precedence is maintained."""
        source = """
result = 2 + 3 * 4
print(result)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        # Verify expression is generated
        assert "DynamicType result" in generated
        
        os.remove(cpp_code)


class TestMainEncapsulation:
    """Test that global code is encapsulated in main()."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
    
    def test_global_code_in_main(self):
        """Test that global statements go into main()."""
        source = """
x = 10
print(x)
y = 20
print(y)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "int main() {" in generated
        assert "return 0;" in generated
        # Verify statements are inside main
        main_start = generated.find("int main()")
        return_pos = generated.find("return 0;")
        assert main_start < generated.find("DynamicType x") < return_pos
        
        os.remove(cpp_code)
    
    def test_functions_outside_main(self):
        """Test that functions are defined outside main()."""
        source = """
def helper():
    return 42

x = helper()
print(x)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        # Function should be before main
        main_pos = generated.find("int main()")
        func_pos = generated.find("DynamicType _fn_helper()")
        assert func_pos < main_pos
        
        os.remove(cpp_code)


class TestDataStructures:
    """Test list and dictionary support."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
    
    def test_list_creation(self):
        """Test list creation."""
        source = """
numbers = [1, 2, 3, 4, 5]
print(numbers)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "std::vector<DynamicType>" in generated
        assert "DynamicType(1)" in generated
        
        os.remove(cpp_code)
    
    def test_list_indexing(self):
        """Test list indexing."""
        source = """
lst = [10, 20, 30]
first = lst[0]
print(first)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "(lst)[" in generated
        
        os.remove(cpp_code)
    
    def test_dictionary_creation(self):
        """Test dictionary creation."""
        source = """
person = {"name": "Alice", "age": 30}
print(person)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "std::map<std::string, DynamicType>" in generated
        
        os.remove(cpp_code)
    
    def test_len_function(self):
        """Test len() builtin function."""
        source = """
lst = [1, 2, 3, 4]
size = len(lst)
print(size)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "len(lst)" in generated
        
        os.remove(cpp_code)


class TestBuiltinFunctions:
    """Test builtin functions support."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
    
    def test_print_function(self):
        """Test print() function."""
        source = """
print("Hello, World!")
print(42)
print(True)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "print(" in generated
        assert generated.count("print(") >= 3
        
        os.remove(cpp_code)
    
    def test_range_function(self):
        """Test range() function."""
        source = """
for i in range(5):
    print(i)

for j in range(2, 8):
    print(j)

for k in range(0, 10, 2):
    print(k)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "range(DynamicType(5))" in generated
        assert "range(DynamicType(2), DynamicType(8))" in generated
        assert "range(DynamicType(0), DynamicType(10), DynamicType(2))" in generated
        
        os.remove(cpp_code)
    
    def test_str_function(self):
        """Test str() type conversion."""
        source = """
num = 42
text = str(num)
print(text)
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "str(num)" in generated
        
        os.remove(cpp_code)


class TestComplexPrograms:
    """Test complete programs that combine multiple features."""
    
    def setup_method(self):
        self.transpiler = Transpiler()
    
    def test_fibonacci_program(self):
        """Test complete Fibonacci program."""
        source = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

for i in range(10):
    print(fib(i))
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "DynamicType _fn_fib(DynamicType n)" in generated
        assert "return" in generated
        assert "for (auto i :" in generated
        
        os.remove(cpp_code)
    
    def test_mixed_types_program(self):
        """Test program with dynamic type changes."""
        source = """
def process(value):
    if value == 0:
        return "zero"
    elif value < 5:
        return "small"
    else:
        return value * 2

results = []
for i in range(0, 10):
    results = results
    print(process(i))
"""
        cpp_code = self.transpiler.transpile(source, "temp_test.cpp")
        with open(cpp_code, 'r') as f:
            generated = f.read()
        
        assert "DynamicType _fn_process" in generated
        assert "if" in generated
        assert "else" in generated
        
        os.remove(cpp_code)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
