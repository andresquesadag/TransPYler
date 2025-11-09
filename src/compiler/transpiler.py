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
from ..codegen.code_generator import CodeGenerator


class Transpiler:
    """
    Transpiler: Modular controller for the C++ transpilation process.
    Uses the parser and code generation visitors to produce C++ code from the AST.
    """

    def __init__(self, target: str = "cpp"):
        self.target = target
        self.parser = Parser()
        self.codegen = CodeGenerator(target)

    def transpile(self, source_code: str, filename: str = "output.cpp") -> str:
        ast_obj = self.parser.parse(source_code)
        # Convert AST object to dict (JSON-like)
        ast_dict = ast_obj.to_dict()
        # Codegen now works over dicts
        return self.codegen.generate_file(ast_dict, filename)
