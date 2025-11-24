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
    def __init__(self):
        """
        Initialize the Transpiler for C++ code generation.
        """
        self.parser = Parser()
        self.codegen = CodeGenerator()

    def transpile(self, source_code: str, filename: str = None) -> str:
        """
        Transpile source code to target language and write it to a file.

        Args:
            source_code: The source code to transpile
            filename: Output filename (auto-generated if None)

        Returns:
            str: The output filename
        """
        # Generate default filename if none provided
        if filename is None:
            filename = "output.cpp"

        # Parse the source code to get AST
        module = self.parser.parse(source_code)

        # Generate code using the unified CodeGenerator
        # The generate_file method now handles both Module nodes and individual nodes properly
        self.codegen.generate_file(module, filename)

        return filename
