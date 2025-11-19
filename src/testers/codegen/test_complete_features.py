"""
Complete Feature Test Suite
---------------------------
Comprehensive tests covering all project requirements:
- Main encapsulation
- Dynamic typing with type changes
- All control structures
- All operator types
- Functions with parameters and returns
- Data structures (lists, dicts)
- Builtin functions
"""

import unittest
import os
from src.compiler.transpiler import Transpiler


class TestMainEncapsulation(unittest.TestCase):
    """Test that global code is properly encapsulated in main()."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_simple_statements_in_main(self):
        """Test that simple statements are placed in main()."""
        source = """
x = 10
y = 20
z = x + y
print(z)
"""
        cpp_file = self.transpiler.transpile(source, "test_main.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Verify main() exists
        self.assertIn("int main() {", content)
        self.assertIn("return 0;", content)
        
        # Verify statements are inside main
        main_start = content.find("int main()")
        return_pos = content.find("return 0;")
        
        x_pos = content.find("DynamicType x")
        y_pos = content.find("DynamicType y")
        z_pos = content.find("DynamicType z")
        
        self.assertTrue(main_start < x_pos < return_pos)
        self.assertTrue(main_start < y_pos < return_pos)
        self.assertTrue(main_start < z_pos < return_pos)
        
        os.remove(cpp_file)
    
    def test_functions_outside_main(self):
        """Test that function definitions are outside main()."""
        source = """
def helper(x):
    return x * 2

result = helper(5)
print(result)
"""
        cpp_file = self.transpiler.transpile(source, "test_func_main.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Function definition should be before main
        main_pos = content.find("int main()")
        func_pos = content.find("DynamicType _fn_helper")
        
        self.assertGreater(main_pos, func_pos, "Function should be defined before main()")
        
        # Function call should be inside main
        call_pos = content.find("_fn_helper(DynamicType(5))")
        return_pos = content.find("return 0;")
        
        self.assertTrue(main_pos < call_pos < return_pos, "Function call should be inside main()")
        
        os.remove(cpp_file)
    
    def test_mixed_functions_and_code(self):
        """Test mix of function definitions and global code."""
        source = """
def add(a, b):
    return a + b

x = 5
y = 10

def multiply(a, b):
    return a * b

sum = add(x, y)
product = multiply(x, y)

print(sum)
print(product)
"""
        cpp_file = self.transpiler.transpile(source, "test_mixed.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        main_pos = content.find("int main()")
        
        # Both functions should be before main
        add_pos = content.find("DynamicType _fn_add")
        multiply_pos = content.find("DynamicType _fn_multiply")
        
        self.assertLess(add_pos, main_pos)
        self.assertLess(multiply_pos, main_pos)
        
        # Variables and calls should be in main
        x_assign = content.find("DynamicType x = DynamicType(5)")
        self.assertGreater(x_assign, main_pos)
        
        os.remove(cpp_file)


class TestDynamicTypingComplete(unittest.TestCase):
    """Comprehensive dynamic typing tests."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_all_type_changes(self):
        """Test all possible type change combinations."""
        source = """
x = 10
print(x)

x = "hello"
print(x)

x = True
print(x)

x = [1, 2, 3]
print(x)

x = {"key": "value"}
print(x)
"""
        cpp_file = self.transpiler.transpile(source, "test_type_changes.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Verify all assignments use DynamicType
        self.assertIn("DynamicType x = DynamicType(10)", content)
        self.assertIn('x = DynamicType(std::string("hello"))', content)
        self.assertIn("x = DynamicType(true)", content)
        self.assertIn("std::vector<DynamicType>", content)
        self.assertIn("std::map<std::string, DynamicType>", content)
        
        os.remove(cpp_file)
    
    def test_type_changes_in_loop(self):
        """Test type changes within a loop."""
        source = """
for i in range(3):
    if i == 0:
        x = 1
    elif i == 1:
        x = "two"
    else:
        x = True
    print(x)
"""
        cpp_file = self.transpiler.transpile(source, "test_loop_types.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("DynamicType x", content)
        self.assertIn("DynamicType(1)", content)
        self.assertIn('DynamicType(std::string("two"))', content)
        self.assertIn("DynamicType(true)", content)
        
        os.remove(cpp_file)
    
    def test_type_changes_in_function(self):
        """Test function returning different types."""
        source = """
def get_value(code):
    if code == 1:
        return 100
    elif code == 2:
        return "text"
    elif code == 3:
        return True
    else:
        return [1, 2, 3]

a = get_value(1)
b = get_value(2)
c = get_value(3)
d = get_value(4)
"""
        cpp_file = self.transpiler.transpile(source, "test_func_types.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Function should return DynamicType
        self.assertIn("DynamicType _fn_get_value", content)
        
        # Multiple return types
        self.assertIn("return DynamicType(100)", content)
        self.assertIn('return DynamicType(std::string("text"))', content)
        self.assertIn("return DynamicType(true)", content)
        
        os.remove(cpp_file)


class TestAllControlStructures(unittest.TestCase):
    """Test all control structures comprehensively."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_nested_if_elif_else(self):
        """Test deeply nested if/elif/else."""
        source = """
x = 15
if x < 10:
    if x < 5:
        result = "very small"
    else:
        result = "small"
elif x < 20:
    if x < 15:
        result = "medium-low"
    else:
        result = "medium-high"
else:
    result = "large"

print(result)
"""
        cpp_file = self.transpiler.transpile(source, "test_nested_if.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Count if/else statements
        if_count = content.count("if")
        else_count = content.count("else")
        
        self.assertGreaterEqual(if_count, 4)
        self.assertGreaterEqual(else_count, 3)
        
        os.remove(cpp_file)
    
    def test_while_with_break_simulation(self):
        """Test while loop with conditional exit."""
        source = """
counter = 0
found = False
while counter < 100:
    if counter == 50:
        found = True
    counter = counter + 1

print(counter)
print(found)
"""
        cpp_file = self.transpiler.transpile(source, "test_while_cond.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("while", content)
        self.assertIn(".toBool()", content)
        self.assertIn("DynamicType counter", content)
        self.assertIn("DynamicType found", content)
        
        os.remove(cpp_file)
    
    def test_nested_loops(self):
        """Test nested for loops."""
        source = """
for i in range(3):
    for j in range(3):
        print(i)
        print(j)
"""
        cpp_file = self.transpiler.transpile(source, "test_nested_loops.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Should have two for loops
        for_count = content.count("for (auto")
        self.assertGreaterEqual(for_count, 2)
        
        os.remove(cpp_file)
    
    def test_for_with_different_iterables(self):
        """Test for loop with different types of iterables."""
        source = """
numbers = [1, 2, 3]
for n in numbers:
    print(n)

for i in range(5):
    print(i)

for j in range(2, 8):
    print(j)

for k in range(0, 10, 2):
    print(k)
"""
        cpp_file = self.transpiler.transpile(source, "test_for_iter.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Verify different range calls
        self.assertIn("range(DynamicType(5))", content)
        self.assertIn("range(DynamicType(2), DynamicType(8))", content)
        self.assertIn("range(DynamicType(0), DynamicType(10), DynamicType(2))", content)
        
        os.remove(cpp_file)
    
    def test_mixed_control_structures(self):
        """Test complex mixing of control structures."""
        source = """
result = 0
for i in range(10):
    if i % 2 == 0:
        j = 0
        while j < i:
            result = result + 1
            j = j + 1
    else:
        result = result + i

print(result)
"""
        cpp_file = self.transpiler.transpile(source, "test_mixed_control.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("for (auto", content)
        self.assertIn("if", content)
        self.assertIn("while", content)
        self.assertIn("else", content)
        
        os.remove(cpp_file)


class TestAllOperators(unittest.TestCase):
    """Test all operator types comprehensively."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_all_arithmetic_operators(self):
        """Test all arithmetic operators."""
        source = """
a = 10
b = 3

add = a + b
sub = a - b
mul = a * b
div = a / b
mod = a % b
power = a ** b
"""
        cpp_file = self.transpiler.transpile(source, "test_arith_ops.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("(a) + (b)", content)
        self.assertIn("(a) - (b)", content)
        self.assertIn("(a) * (b)", content)
        self.assertIn("(a) / (b)", content)
        self.assertIn("(a) % (b)", content)
        self.assertIn("pow(", content)
        
        os.remove(cpp_file)
    
    def test_all_comparison_operators(self):
        """Test all comparison operators."""
        source = """
a = 10
b = 20

eq = a == b
neq = a != b
lt = a < b
gt = a > b
lte = a <= b
gte = a >= b
"""
        cpp_file = self.transpiler.transpile(source, "test_comp_ops.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("(a) == (b)", content)
        self.assertIn("(a) != (b)", content)
        self.assertIn("(a) < (b)", content)
        self.assertIn("(a) > (b)", content)
        self.assertIn("(a) <= (b)", content)
        self.assertIn("(a) >= (b)", content)
        
        os.remove(cpp_file)
    
    def test_all_logical_operators(self):
        """Test all logical operators."""
        source = """
a = True
b = False

and_op = a and b
or_op = a or b
not_op = not a
"""
        cpp_file = self.transpiler.transpile(source, "test_logic_ops.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("&&", content)
        self.assertIn("||", content)
        self.assertIn("!(a)", content)
        self.assertIn(".toBool()", content)
        
        os.remove(cpp_file)
    
    def test_operator_precedence_complex(self):
        """Test complex operator precedence."""
        source = """
result1 = 2 + 3 * 4
result2 = (2 + 3) * 4
result3 = 2 ** 3 + 4
result4 = 10 - 3 - 2
result5 = 10 / 2 * 5
result6 = 5 > 3 and 10 < 20
result7 = 5 + 3 > 10 - 4
"""
        cpp_file = self.transpiler.transpile(source, "test_precedence.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        # Verify expressions are generated
        self.assertIn("DynamicType result1", content)
        self.assertIn("DynamicType result2", content)
        self.assertIn("DynamicType result3", content)
        
        os.remove(cpp_file)
    
    def test_chained_comparisons(self):
        """Test chained comparison operations."""
        source = """
x = 10
result1 = x > 5 and x < 15
result2 = x >= 10 or x <= 0
result3 = not (x == 5)
"""
        cpp_file = self.transpiler.transpile(source, "test_chained_comp.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("&&", content)
        self.assertIn("||", content)
        self.assertIn("!", content)
        
        os.remove(cpp_file)


class TestFunctionsComplete(unittest.TestCase):
    """Comprehensive function tests."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_function_no_params_no_return(self):
        """Test function without params or return."""
        source = """
def greet():
    print("Hello")

greet()
"""
        cpp_file = self.transpiler.transpile(source, "test_func_simple.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("DynamicType _fn_greet()", content)
        self.assertIn("_fn_greet()", content)
        
        os.remove(cpp_file)
    
    def test_function_multiple_params(self):
        """Test function with multiple parameters."""
        source = """
def calculate(a, b, c):
    return a + b * c

result = calculate(1, 2, 3)
print(result)
"""
        cpp_file = self.transpiler.transpile(source, "test_func_params.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("DynamicType _fn_calculate(DynamicType a, DynamicType b, DynamicType c)", content)
        self.assertIn("_fn_calculate(DynamicType(1), DynamicType(2), DynamicType(3))", content)
        
        os.remove(cpp_file)
    
    def test_recursive_functions(self):
        """Test multiple recursive functions."""
        source = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(factorial(5))
print(fibonacci(7))
"""
        cpp_file = self.transpiler.transpile(source, "test_recursion.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("DynamicType _fn_factorial", content)
        self.assertIn("DynamicType _fn_fibonacci", content)
        self.assertIn("_fn_factorial(", content)  # Recursive call
        self.assertIn("_fn_fibonacci(", content)  # Recursive call
        
        os.remove(cpp_file)
    
    def test_function_calling_function(self):
        """Test functions calling other functions."""
        source = """
def helper(x):
    return x * 2

def main_func(a):
    temp = helper(a)
    return temp + 10

result = main_func(5)
print(result)
"""
        cpp_file = self.transpiler.transpile(source, "test_func_call.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("DynamicType _fn_helper", content)
        self.assertIn("DynamicType _fn_main_func", content)
        # main_func calls helper
        helper_call_in_main = "_fn_helper(a)" in content
        self.assertTrue(helper_call_in_main)
        
        os.remove(cpp_file)
    
    def test_function_with_complex_logic(self):
        """Test function with complex internal logic."""
        source = """
def process_list(items):
    total = 0
    for item in items:
        if item > 0:
            total = total + item
        else:
            total = total + item
    return total

numbers = [1, 2, 3, 4, 5]
result = process_list(numbers)
print(result)
"""
        cpp_file = self.transpiler.transpile(source, "test_func_complex.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("DynamicType _fn_process_list", content)
        self.assertIn("for (auto item :", content)
        self.assertIn("if", content)
        self.assertIn("else", content)
        
        os.remove(cpp_file)


class TestDataStructuresComplete(unittest.TestCase):
    """Comprehensive data structure tests."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_list_operations_complete(self):
        """Test comprehensive list operations."""
        source = """
empty_list = []
numbers = [1, 2, 3, 4, 5]
mixed = [1, "two", True, 4.5]

first = numbers[0]
last = numbers[4]

length = len(numbers)
mixed_len = len(mixed)

print(first)
print(last)
print(length)
"""
        cpp_file = self.transpiler.transpile(source, "test_lists.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("std::vector<DynamicType>{}", content)  # Empty list
        self.assertIn("std::vector<DynamicType>", content)
        self.assertIn("len(", content)
        
        os.remove(cpp_file)
    
    def test_dictionary_operations(self):
        """Test dictionary operations."""
        source = """
person = {"name": "Alice", "age": 30}
settings = {"debug": True, "level": 5}

name = person["name"]
age = person["age"]

print(name)
print(age)
"""
        cpp_file = self.transpiler.transpile(source, "test_dicts.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("std::map<std::string, DynamicType>", content)
        
        os.remove(cpp_file)
    
    def test_nested_data_structures(self):
        """Test nested lists and dictionaries."""
        source = """
matrix = [[1, 2], [3, 4]]
nested_dict = {"outer": {"inner": 42}}

value = matrix[0][1]
nested_value = nested_dict["outer"]["inner"]

print(value)
print(nested_value)
"""
        cpp_file = self.transpiler.transpile(source, "test_nested_data.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("std::vector<DynamicType>", content)
        self.assertIn("std::map<std::string, DynamicType>", content)
        
        os.remove(cpp_file)


class TestBuiltinFunctionsComplete(unittest.TestCase):
    """Comprehensive builtin function tests."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_all_builtin_functions(self):
        """Test all supported builtin functions."""
        source = """
numbers = [1, 2, 3, 4, 5]
size = len(numbers)

text = str(42)
number = int("100")

for i in range(10):
    print(i)

for j in range(5, 10):
    print(j)

for k in range(0, 20, 3):
    print(k)

print("Hello")
print(size)
print(text)
print(number)
"""
        cpp_file = self.transpiler.transpile(source, "test_builtins.cpp")
        
        with open(cpp_file, 'r') as f:
            content = f.read()
        
        self.assertIn("len(", content)
        self.assertIn("str(", content)
        self.assertIn("int_(", content)
        self.assertIn("range(", content)
        self.assertIn("print(", content)
        
        os.remove(cpp_file)


if __name__ == "__main__":
    unittest.main()
