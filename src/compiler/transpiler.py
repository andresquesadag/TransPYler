"""
Transpiler
----------
This module provides the Transpiler class, which is the modular controller for the C++ transpilation process.

Key Features:
- Uses the parser and code generation visitors to produce C++ code from the AST.
- Integrates all codegen modules for end-to-end transpilation.
- Entry point for converting source code to C++ files.
"""

"""
Transpiler: Modular controller for the C++ transpilation process.
Uses the parser and code generation visitors to produce C++ code from the AST.
"""

from ..parser.parser import Parser
from ..codegen.code_generator import CodeGenerator

class Transpiler:
	def __init__(self, target: str = "cpp"):
		self.target = target
		self.parser = Parser()
		self.codegen = CodeGenerator(target)

	def transpile(self, source_code: str, filename: str = "output.cpp") -> str:
		ast = self.parser.parse(source_code)
		# Persona 3: control de flujo y estructuras de datos
		return self.codegen.generate_file(ast, filename)