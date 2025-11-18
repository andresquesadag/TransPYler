"""
CodeGenerator
-------------
This module provides the CodeGenerator class, which orchestrates code generation using modular visitors for statements, data structures, expressions, and functions.

Key Features:
- Integrates Persona 1 (DynamicType, C++ type system), Persona 2 (expressions, functions, scopes), and Persona 3 (control flow, data structures).
- Provides file generation for Python and C++ code, including STL headers and placeholders for unimplemented features.
- Central entry point for generating code from ASTs.
"""

"""
CodeGenerator: Orchestrates code generation using modular visitors for statements, data structures, expressions, and functions.

Integrates Persona 1 (DynamicType, C++ type system), Persona 2 (expressions, functions, scopes), and Persona 3 (control flow, data structures).
Provides file generation for Python and C++ code, including STL headers and placeholders for unimplemented features.
"""


from .statement_generator import StatementVisitor
from .data_structure_generator import DataStructureGenerator
from .expr_generator import ExprGenerator
from .function_generator import FunctionGenerator
from .scope_manager import ScopeManager
import os


class CodeGenerator:
    """
    Main code generation orchestrator.
    Integrates all codegen visitors and provides file output for Python and C++.
    """

    def __init__(self, target: str = "python"):
        """
        Initialize the CodeGenerator.
        Args:
                target (str): Target language ('python' or 'cpp').
        Sets up all codegen visitors for statements, data structures, expressions, and functions.
        """
        self.target = target  # Target language for code generation
        self.statement_visitor = StatementVisitor(
            target
        )  # Handles control flow (Persona 3)
        self.data_structure_generator = DataStructureGenerator(
            target
        )  # Handles collections (Persona 3)
        # Create a shared ScopeManager for generators that need scope tracking
        self.scope = ScopeManager()
        # ExprGenerator expects an optional scope; pass the shared ScopeManager
        self.expr_generator = ExprGenerator(
            scope=self.scope
        )  # Handles expressions and literals (Persona 2)
        self.function_generator = FunctionGenerator(
            self.scope
        )  # Handles functions and scopes (Persona 2)
        # TODO(Andres): Integrate DynamicType system and helpers for dynamic typing in C++ (Persona 1)

    def visit(self, node) -> str:
        """
        Dispatch code generation to the appropriate visitor based on node type.
        Args:
                node: AST node object
        Returns:
                str: Generated code for the node.
        """
        node_type = node.__class__.__name__
        if node_type.endswith("Expr") or node_type == "Identifier":
            return self.expr_generator.visit(node)
        if node_type.endswith("FunctionDef"):
            return self.function_generator.visit(node)
        return self.statement_visitor.visit(node)

    def generate_file(self, node, filename: str = "output.cpp"):
        """Generate code for the given AST node and write it to a file."""
        code = self.visit(node)  # Generate code from AST
        if self.target == "cpp":
            # Include DynamicType system and builtins
            code = (
                # "builtins.hpp" includes DynamicType and that one includes other useful libraries
                '#include "builtins.hpp"\n'
                "using namespace std;\n\n" + code
            )
        # Write generated code to file
        with open(file=filename, mode="w", encoding="utf-8") as f:
            f.write(code)
        return filename
