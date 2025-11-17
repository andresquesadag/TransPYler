"""
Transpiler
----------
This module provides the Transpiler class, which is the modular controller for the C++ transpilation process.

Key Features:
- Uses the parser and code generation visitors to produce C++ code from the AST.
- Integrates all codegen modules for end-to-end transpilation.
- Entry point for converting source code to C++ files.
"""

from ..parser.parser import Parser
#from ..codegen.code_generator import CodeGenerator
from ..codegen.code_generator_cpp import CodeGeneratorCpp

# class Transpiler:
# 	def __init__(self, target: str = "cpp"):
# 		self.target = target
# 		self.parser = Parser()
# 		self.codegen = CodeGenerator(target)

# 	def transpile(self, source_code: str, filename: str = "output.cpp") -> str:
# 		"""
# 		Transpile source code to target language.
		
# 		Args:
# 			source_code: The source code to transpile
# 			filename: Output filename
			
# 		Returns:
# 			str: The output filename
# 		"""
# 		ast_obj = self.parser.parse(source_code)
# 		# Pass AST object directly to codegen (no conversion to dict)
# 		return self.codegen.generate_file(ast_obj, filename) 

class Transpiler:
    def __init__(self):
        self.parser = Parser()
        self.codegen = CodeGeneratorCpp()  # solo C++

    def transpile(self, source_code: str, filename: str = "output.cpp") -> str:
        """
        Transpile Fangless Python source code to C++ and write it to a file.

        Args:
            source_code: Fangless Python source
            filename: output C++ filename

        Returns:
            str: the output filename
        """
        module = self.parser.parse(source_code)          # AST: Module
        cpp_code = self.codegen.generate(module)         # string C++
        with open(filename, "w", encoding="utf-8") as f:
            f.write(cpp_code)
        return filename