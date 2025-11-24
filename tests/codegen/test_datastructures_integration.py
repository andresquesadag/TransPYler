"""
Comprehensive tests for data structures and their methods.
Tests all data structure operations including edge cases, error conditions, and complex scenarios.
"""
import unittest
import tempfile
import subprocess
import os
from pathlib import Path
from src.compiler.transpiler import Transpiler


class TestDataStructuresIntegration(unittest.TestCase):
    """Integration tests for data structures (lists, dicts, sets) and their methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transpiler = Transpiler()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp files
        for f in self.temp_dir.glob("*"):
            f.unlink()
        self.temp_dir.rmdir()
        
    def _compile_and_run(self, cpp_code: str) -> str:
        """Compile and run C++ code, return output."""
        cpp_file = self.temp_dir / "test.cpp" 
        exe_file = self.temp_dir / "test"
        
        with open(cpp_file, "w") as f:
            f.write(cpp_code)
            
        # Find project root and runtime files
        project_root = Path(__file__).parent.parent.parent
        runtime_dir = project_root / "src" / "runtime" / "cpp"
        
        # Compile
        cmd = [
            "g++", "-std=c++17",
            str(cpp_file),
            str(runtime_dir / "DynamicType.cpp"),
            str(runtime_dir / "builtins.cpp"),
            f"-I{runtime_dir}",
            "-o", str(exe_file)
        ]
        
        compile_result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(compile_result.returncode, 0, 
                        f"Compilation failed: {compile_result.stderr}")
        
        # Run
        run_result = subprocess.run([str(exe_file)], capture_output=True, text=True)
        self.assertEqual(run_result.returncode, 0,
                        f"Execution failed: {run_result.stderr}")
        
        return run_result.stdout.strip()
    
    def _transpile_and_run(self, python_code: str) -> str:
        """Helper to transpile Python code and run it."""
        cpp_filename = self.transpiler.transpile(python_code, str(self.temp_dir / "test.cpp"))
        with open(cpp_filename, 'r') as f:
            cpp_code = f.read()
        return self._compile_and_run(cpp_code)

    # ========== LIST TESTS ==========
    
    def test_list_basic_operations(self):
        """Test basic list operations: append, len, access."""
        python_code = """
def test_list():
    # Create list
    numbers = [1, 2, 3]
    print("Initial:", numbers)
    print("Length:", len(numbers))
    
    # Append multiple items
    numbers.append(4)
    numbers.append(5)
    print("After appends:", numbers)
    print("New length:", len(numbers))
    
    # Access elements
    print("First:", numbers[0])
    print("Last:", numbers[4])

if __name__ == "__main__":
    test_list()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Initial: [1, 2, 3]", output)
        self.assertIn("Length: 3", output)
        self.assertIn("After appends: [1, 2, 3, 4, 5]", output)
        self.assertIn("New length: 5", output)
        self.assertIn("First: 1", output)
        self.assertIn("Last: 5", output)
    
    def test_list_empty_operations(self):
        """Test operations on empty lists."""
        python_code = """
def test_empty():
    empty_list = []
    print("Empty length:", len(empty_list))
    
    empty_list.append("first")
    print("After first append:", empty_list)
    print("Length after append:", len(empty_list))

if __name__ == "__main__":
    test_empty()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Empty length: 0", output)
        self.assertIn("After first append: [first]", output)
        self.assertIn("Length after append: 1", output)
    
    def test_list_mixed_types(self):
        """Test lists with mixed data types."""
        python_code = """
def test_mixed():
    mixed = [1, "hello", True, 3.14]
    print("Mixed list:", mixed)
    print("Length:", len(mixed))
    
    mixed.append(False)
    mixed.append("world")
    print("After appends:", mixed)

if __name__ == "__main__":
    test_mixed()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Mixed list:", output)
        self.assertIn("Length: 4", output)
        self.assertIn("After appends:", output)
        # Check individual elements are present
        self.assertIn("1", output)
        self.assertIn("hello", output)
        self.assertIn("True", output)
        self.assertIn("3.14", output)

    # ========== DICTIONARY TESTS ==========
    
    def test_dict_basic_operations(self):
        """Test basic dictionary operations: creation, access, len."""
        python_code = """
def test_dict():
    # Create dictionary
    person = {"name": "Alice", "age": 30, "city": "NYC"}
    print("Person:", person)
    print("Length:", len(person))
    
    # Access values
    print("Name:", person["name"])
    print("Age:", person["age"])
    print("City:", person["city"])

if __name__ == "__main__":
    test_dict()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Length: 3", output)
        self.assertIn("Name: Alice", output)
        self.assertIn("Age: 30", output) 
        self.assertIn("City: NYC", output)
    
    def test_dict_empty_operations(self):
        """Test operations on empty dictionaries."""
        python_code = """
def test_empty_dict():
    empty_dict = {}
    print("Empty dict:", empty_dict)
    print("Empty length:", len(empty_dict))

if __name__ == "__main__":
    test_empty_dict()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Empty dict: {}", output)
        self.assertIn("Empty length: 0", output)
    
    def test_dict_mixed_value_types(self):
        """Test dictionaries with mixed value types."""
        python_code = """
def test_mixed_dict():
    data = {
        "string": "hello",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "list": [1, 2, 3]
    }
    print("Data length:", len(data))
    print("String:", data["string"])
    print("Number:", data["number"])
    print("List:", data["list"])

if __name__ == "__main__":
    test_mixed_dict()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Data length: 5", output)
        self.assertIn("String: hello", output)
        self.assertIn("Number: 42", output)
        self.assertIn("List: [1, 2, 3]", output)

    # ========== SET TESTS ==========
    
    def test_set_basic_operations(self):
        """Test basic set operations: creation, add, len, uniqueness."""
        python_code = """
def test_set():
    # Create set
    numbers = {1, 2, 3}
    print("Initial set:", numbers)
    print("Length:", len(numbers))
    
    # Add new elements
    numbers.add(4)
    numbers.add(5)
    print("After adds:", numbers)
    print("New length:", len(numbers))

if __name__ == "__main__":
    test_set()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Length: 3", output)
        self.assertIn("New length: 5", output)
        # Check that all numbers appear in output
        for i in [1, 2, 3, 4, 5]:
            self.assertIn(str(i), output)
    
    def test_set_uniqueness_property(self):
        """Test that sets maintain uniqueness and handle duplicates correctly."""
        python_code = """
def test_uniqueness():
    # Create set with duplicates (should be removed)
    numbers = {1, 2, 2, 3, 3, 3}
    print("Set with duplicates:", numbers)
    print("Length:", len(numbers))
    
    # Add existing element (should not change size)
    numbers.add(2)
    print("After adding existing 2:", numbers)
    print("Length after duplicate:", len(numbers))
    
    # Add new element
    numbers.add(4)
    print("After adding new 4:", numbers) 
    print("Final length:", len(numbers))

if __name__ == "__main__":
    test_uniqueness()
"""
        output = self._transpile_and_run(python_code)
        
        # Set should have only 3 unique elements initially
        self.assertIn("Length: 3", output)
        # Adding duplicate should not change size
        self.assertIn("Length after duplicate: 3", output)
        # Adding new element should increase size
        self.assertIn("Final length: 4", output)
    
    def test_set_empty_operations(self):
        """Test operations on empty sets."""
        python_code = """
def test_empty_set():
    empty_set = set()
    print("Empty set length:", len(empty_set))
    
    empty_set.add("first")
    print("After first add:", len(empty_set))
    
    empty_set.add("second") 
    print("After second add:", len(empty_set))

if __name__ == "__main__":
    test_empty_set()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Empty set length: 0", output)
        self.assertIn("After first add: 1", output)
        self.assertIn("After second add: 2", output)
    
    def test_set_mixed_types(self):
        """Test sets with mixed data types."""
        python_code = """
def test_mixed_set():
    mixed = {1, "hello", True}
    print("Mixed set length:", len(mixed))
    
    mixed.add(3.14)
    mixed.add("world")
    print("After adds:", len(mixed))

if __name__ == "__main__":
    test_mixed_set()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Mixed set length: 3", output)
        self.assertIn("After adds: 5", output)

    # ========== COMPLEX SCENARIOS ==========
    
    def test_nested_data_structures(self):
        """Test nested data structures (lists of dicts, etc.)."""
        python_code = """
def test_nested():
    # List of dictionaries
    people = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    print("People list length:", len(people))
    print("First person name:", people[0]["name"])
    print("Second person age:", people[1]["age"])
    
    # Add another person
    people.append({"name": "Charlie", "age": 35})
    print("After adding Charlie:", len(people))

if __name__ == "__main__":
    test_nested()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("People list length: 2", output)
        self.assertIn("First person name: Alice", output)
        self.assertIn("Second person age: 25", output)
        self.assertIn("After adding Charlie: 3", output)
    
    def test_data_structure_operations_in_loops(self):
        """Test data structure operations inside loops."""
        python_code = """
def test_loops():
    numbers = []
    factors = set()
    
    # Build data structures in loop
    for i in range(1, 6):
        numbers.append(i)
        factors.add(i * 2)
    
    print("Numbers:", numbers)
    print("Numbers length:", len(numbers))
    print("Factors length:", len(factors))

if __name__ == "__main__":
    test_loops()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("Numbers: [1, 2, 3, 4, 5]", output)
        self.assertIn("Numbers length: 5", output)
        self.assertIn("Factors length: 5", output)
    
    def test_data_structures_with_functions(self):
        """Test data structures passed to and returned from functions."""
        python_code = """
def add_numbers_to_list(lst, start, end):
    for i in range(start, end + 1):
        lst.append(i)
    return lst

def create_person_dict(name, age):
    return {"name": name, "age": age, "id": len(name)}

def test_functions():
    # List operations through function
    my_list = [0]
    result = add_numbers_to_list(my_list, 1, 3)
    print("List result:", result)
    print("List length:", len(result))
    
    # Dict creation through function
    person = create_person_dict("Alice", 30)
    print("Person:", person)
    print("Person length:", len(person))

if __name__ == "__main__":
    test_functions()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("List result: [0, 1, 2, 3]", output)
        self.assertIn("List length: 4", output)
        self.assertIn("Person length: 3", output)
        self.assertIn("Alice", output)
    
    def test_all_len_function_variants(self):
        """Test len() function with all supported data types."""
        python_code = """
def test_all_lens():
    # Test len() with different types
    string = "hello"
    list_data = [1, 2, 3, 4]
    dict_data = {"a": 1, "b": 2, "c": 3}
    set_data = {10, 20, 30, 40, 50}
    empty_list = []
    empty_dict = {}
    empty_string = ""
    
    print("String length:", len(string))
    print("List length:", len(list_data))
    print("Dict length:", len(dict_data))
    print("Set length:", len(set_data))
    print("Empty list length:", len(empty_list))
    print("Empty dict length:", len(empty_dict))
    print("Empty string length:", len(empty_string))

if __name__ == "__main__":
    test_all_lens()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("String length: 5", output)
        self.assertIn("List length: 4", output)
        self.assertIn("Dict length: 3", output)
        self.assertIn("Set length: 5", output)
        self.assertIn("Empty list length: 0", output)
        self.assertIn("Empty dict length: 0", output)
        self.assertIn("Empty string length: 0", output)
    
    def test_string_handling_edge_cases(self):
        """Test string handling with various escape sequences."""
        python_code = '''
def test_strings():
    # Various string scenarios
    newline = "Line 1\\nLine 2"
    tab = "Column 1\\tColumn 2"
    quote = "He said \\"Hello\\""
    backslash = "Path: C:\\\\folder\\\\file.txt"
    
    print(newline)
    print(tab)
    print(quote)
    print(backslash)

if __name__ == "__main__":
    test_strings()
'''
        output = self._transpile_and_run(python_code)
        
        # Check that escaped characters are properly handled
        self.assertIn("Line 1\nLine 2", output)
        self.assertIn("Column 1\tColumn 2", output)
        self.assertIn('He said "Hello"', output)
        self.assertIn("Path: C:\\folder\\file.txt", output)

    # ========== PERFORMANCE TESTS ==========
    
    def test_moderate_scale_operations(self):
        """Test with moderately sized data structures."""
        python_code = """
def test_scale():
    # Create moderately sized structures
    big_list = []
    big_set = set()
    
    # Add 15 elements to each
    for i in range(15):
        big_list.append(i)
        big_set.add(i * 2)
    
    print("List length:", len(big_list))
    print("Set length:", len(big_set))
    
    # Verify some values
    print("List[10]:", big_list[10])

if __name__ == "__main__":
    test_scale()
"""
        output = self._transpile_and_run(python_code)
        
        self.assertIn("List length: 15", output) 
        self.assertIn("Set length: 15", output)
        self.assertIn("List[10]: 10", output)


if __name__ == "__main__":
    unittest.main()