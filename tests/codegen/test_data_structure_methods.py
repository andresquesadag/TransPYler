"""
Tests for the new data structure methods implementation.
"""
import unittest
import tempfile
import subprocess
import os
from pathlib import Path
from src.compiler.transpiler import Transpiler

class TestDataStructureMethods(unittest.TestCase):
    
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
    
    def test_list_append_method(self):
        """Test list.append() method transpilation."""
        python_code = """
def test():
    my_list = [1, 2, 3]
    print("Before:", my_list)
    my_list.append(4)
    print("After:", my_list)

if __name__ == "__main__":
    test()
"""
        cpp_filename = self.transpiler.transpile(python_code, str(self.temp_dir / "test.cpp"))
        with open(cpp_filename, 'r') as f:
            cpp_code = f.read()
        output = self._compile_and_run(cpp_code)
        
        self.assertIn("Before: [1, 2, 3]", output)
        self.assertIn("After: [1, 2, 3, 4]", output)
    
    def test_set_add_method(self):
        """Test set.add() method transpilation."""
        python_code = """
def test():
    my_set = {1, 2, 3}
    print("Before:", my_set)
    my_set.add(4)
    print("After:", my_set)

if __name__ == "__main__":
    test()
"""
        cpp_filename = self.transpiler.transpile(python_code, str(self.temp_dir / "test.cpp"))
        with open(cpp_filename, 'r') as f:
            cpp_code = f.read()
        output = self._compile_and_run(cpp_code)
        
        self.assertIn("Before:", output)
        self.assertIn("After:", output)
        # Sets might have different ordering, just check the numbers are present
        self.assertIn("1", output)
        self.assertIn("2", output) 
        self.assertIn("3", output)
        self.assertIn("4", output)
    
    def test_dict_access_and_len(self):
        """Test dictionary access and len() function."""
        python_code = """
def test():
    my_dict = {"name": "Alice", "age": 30}
    print("Dict:", my_dict)
    print("Name:", my_dict["name"])
    print("Length:", len(my_dict))

if __name__ == "__main__":
    test()
"""
        cpp_filename = self.transpiler.transpile(python_code, str(self.temp_dir / "test.cpp"))
        with open(cpp_filename, 'r') as f:
            cpp_code = f.read()
        output = self._compile_and_run(cpp_code)
        
        self.assertIn("Name: Alice", output)
        self.assertIn("Length: 2", output)
    
    def test_len_function_all_types(self):
        """Test len() function works with all data structure types."""
        python_code = """
def test():
    my_list = [1, 2, 3, 4]
    my_dict = {"a": 1, "b": 2}  
    my_set = {10, 20, 30}
    
    print("List length:", len(my_list))
    print("Dict length:", len(my_dict))
    print("Set length:", len(my_set))

if __name__ == "__main__":
    test()
"""
        cpp_filename = self.transpiler.transpile(python_code, str(self.temp_dir / "test.cpp"))
        with open(cpp_filename, 'r') as f:
            cpp_code = f.read()
        output = self._compile_and_run(cpp_code)
        
        self.assertIn("List length: 4", output)
        self.assertIn("Dict length: 2", output)
        self.assertIn("Set length: 3", output)
    
    def test_set_uniqueness(self):
        """Test that sets maintain uniqueness property."""
        python_code = """
def test():
    my_set = {1, 2, 3}
    print("Before:", len(my_set))
    my_set.add(2)  # Add duplicate
    print("After adding duplicate:", len(my_set))
    my_set.add(4)  # Add new element
    print("After adding new:", len(my_set))

if __name__ == "__main__":
    test()
"""
        cpp_filename = self.transpiler.transpile(python_code, str(self.temp_dir / "test.cpp"))
        with open(cpp_filename, 'r') as f:
            cpp_code = f.read()
        output = self._compile_and_run(cpp_code)
        
        self.assertIn("Before: 3", output)
        self.assertIn("After adding duplicate: 3", output)  # Should still be 3
        self.assertIn("After adding new: 4", output)       # Should be 4
    
    def test_string_escaping(self):
        """Test that strings with newlines are properly escaped."""
        python_code = '''
def test():
    print("Line 1\\nLine 2")

if __name__ == "__main__":
    test()
'''
        cpp_filename = self.transpiler.transpile(python_code, str(self.temp_dir / "test.cpp"))
        with open(cpp_filename, 'r') as f:
            cpp_code = f.read()
        output = self._compile_and_run(cpp_code)
        
        # Should have actual newline in output
        self.assertIn("Line 1\nLine 2", output)

if __name__ == "__main__":
    unittest.main()