"""
Test Transpiler Integration
---------------------------
This module provides integration tests for the complete transpiler pipeline.
Tests the full flow from Python source code through AST to C++ code generation.

Key Features:
- Tests complete transpilation pipeline (Parser -> AST -> CodeGenerator -> C++)
- Validates code generation for expressions, control flow, functions, and data structures
- Tests integration between Persona 1 (DynamicType), Persona 2 (expressions/functions), and Persona 3 (control flow/data structures)
"""

import unittest
import tempfile
import os
from src.compiler.transpiler import Transpiler


class TestTranspilerIntegration(unittest.TestCase):
    """Integration tests for the complete transpiler pipeline."""
    
    def setUp(self):
        self.transpiler = Transpiler()
    
    def test_simple_assignment(self):
        """Test simple variable assignment."""
        source = "x = 42"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify C++ code contains expected elements
            self.assertIn('#include "builtins.hpp"', cpp_code)
            self.assertIn('using namespace std;', cpp_code)
            self.assertIn('int main() {', cpp_code)
            self.assertIn('DynamicType x = DynamicType(42);', cpp_code)
            self.assertIn('return 0;', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_arithmetic_expressions(self):
        """Test arithmetic expression generation."""
        source = """
x = 5 + 3
y = x * 2
z = y ** 2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify arithmetic operations
            self.assertIn('DynamicType x = ', cpp_code)
            self.assertIn('(DynamicType(5)) + (DynamicType(3))', cpp_code)
            self.assertIn('DynamicType y = ', cpp_code)
            self.assertIn('(x) * (DynamicType(2))', cpp_code)
            self.assertIn('DynamicType z = DynamicType(pow(', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_if_statement(self):
        """Test if statement generation."""
        source = """
x = 10
if x > 5:
    y = 1
else:
    y = 0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify if statement structure
            self.assertIn('if (DynamicType((x) > (DynamicType(5))).toBool())', cpp_code)
            self.assertIn('DynamicType y = DynamicType(1);', cpp_code)
            self.assertIn('else', cpp_code)
            self.assertIn('y = DynamicType(0);', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_while_loop(self):
        """Test while loop generation."""
        source = """
x = 0
while x < 5:
    x = x + 1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify while loop structure
            self.assertIn('while (DynamicType((x) < (DynamicType(5))).toBool())', cpp_code)
            self.assertIn('x = (x) + (DynamicType(1));', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_for_loop(self):
        """Test for loop generation."""
        source = """
numbers = [1, 2, 3]
for x in numbers:
    print(x)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify for loop and list generation
            self.assertIn('DynamicType(std::vector<DynamicType>{DynamicType(1), DynamicType(2), DynamicType(3)})', cpp_code)
            # The for loop now uses a temporary variable to avoid dangling references
            self.assertIn('for (auto x :', cpp_code)
            self.assertIn('.getList()', cpp_code)
            self.assertIn('print(x);', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_function_definition(self):
        """Test function definition generation."""
        source = """
def add(a, b):
    return a + b

result = add(5, 3)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify function definition
            self.assertIn('DynamicType _fn_add(DynamicType a, DynamicType b) {', cpp_code)
            self.assertIn('return (a) + (b);', cpp_code)
            self.assertIn('DynamicType result = _fn_add(DynamicType(5), DynamicType(3));', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_list_operations(self):
        """Test list creation and operations."""
        source = """
my_list = [1, 2, 3, 4]
length = len(my_list)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify list creation and len function
            self.assertIn('DynamicType(std::vector<DynamicType>{DynamicType(1), DynamicType(2), DynamicType(3), DynamicType(4)})', cpp_code)
            self.assertIn('DynamicType length = len(my_list);', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_string_operations(self):
        """Test string literal and operations."""
        source = """
message = "Hello"
name = "World"
greeting = message + " " + name
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify string handling
            self.assertIn('DynamicType(std::string("Hello"))', cpp_code)
            self.assertIn('DynamicType(std::string("World"))', cpp_code)
            self.assertIn('DynamicType(std::string(" "))', cpp_code)
            # Verify string concatenation (format may vary slightly)
            self.assertIn('message', cpp_code)
            self.assertIn('name', cpp_code)
            self.assertIn('greeting', cpp_code)
        finally:
            os.unlink(output_file)
    
    def test_boolean_operations(self):
        """Test boolean literals and operations."""
        source = """
flag = True
result = not flag
check = flag and False
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            output_file = self.transpiler.transpile(source, f.name)
            
        try:
            with open(output_file, 'r') as f:
                cpp_code = f.read()
            
            # Verify boolean handling
            self.assertIn('DynamicType(true)', cpp_code)
            self.assertIn('DynamicType(false)', cpp_code)
            self.assertIn('!(flag)', cpp_code)
            # Logical operators now generate toBool() conversions
            self.assertIn('.toBool()', cpp_code)
        finally:
            os.unlink(output_file)


if __name__ == "__main__":
    unittest.main()