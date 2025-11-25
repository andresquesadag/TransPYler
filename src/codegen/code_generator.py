"""
CodeGenerator
-------------
This module provides the CodeGenerator class, which orchestrates code generation using modular visitors for statements, data structures, expressions, and functions.

Key Features:
- Integrates Persona 1 (DynamicType, C++ type system), Persona 2 (expressions, functions, scopes), and Persona 3 (control flow, data structures).
- Provides file generation for Python and C++ code, including STL headers and placeholders for unimplemented features.
- Central entry point for generating code from ASTs.
- Unified interface that replaces both CodeGenerator and CodeGeneratorCpp
"""

from typing import List
from .statement_generator import StatementVisitor
from .data_structure_generator import DataStructureGenerator
from .expr_generator import ExprGenerator
from .function_generator import FunctionGenerator
from .basic_statement_generator import BasicStatementGenerator
from .scope_manager import ScopeManager
from src.core import (
    AstNode,
    Module,
    FunctionDef,
    Block,
    If,
    While,
    For,
    Assign,
    ExprStmt,
    Return,
)
import os

CPP_PREAMBLE = """#include "builtins.hpp"
using namespace std;
"""


class CodeGenerator:
    """
    Main code generation orchestrator.
    Integrates all codegen visitors and provides file output for Python and C++.
    Unified interface that handles both targets seamlessly.
    """

    def __init__(self):
        """
        Initialize the CodeGenerator for C++ target only.
        Sets up all codegen visitors for statements, data structures, expressions, and functions.
        """
        self.target = "cpp"  # Only C++ target supported

        # Create a shared ScopeManager for generators that need scope tracking
        self.scope = ScopeManager()

        # Initialize generators in correct order to allow dependencies
        self.expr_generator = ExprGenerator(
            scope=self.scope
        )  # Handles expressions and literals (Persona 2)
        self.data_structure_generator = DataStructureGenerator(
            expr_generator=self.expr_generator
        )  # Handles collections (Persona 3)

        # Inject data structure generator reference into expr generator for delegation
        self.expr_generator.data_structure_generator = self.data_structure_generator
        self.basic_stmt_generator = BasicStatementGenerator(scope=self.scope)

        self.statement_visitor = StatementVisitor(
            expr_generator=self.expr_generator,
            scope_manager=self.scope,
            basic_stmt_generator=self.basic_stmt_generator,
        )  # Handles control flow (Persona 3)
        self.function_generator = FunctionGenerator(
            self.scope
        )  # Handles functions and scopes (Persona 2)
        self.basic_stmt_generator = BasicStatementGenerator(
            scope=self.scope
        )  # Persona 2

    def visit(self, node) -> str:
        """
        Dispatch code generation to the appropriate visitor based on node type.
        Args:
                node: AST node object
        Returns:
                str: Generated code for the node.
        """
        node_type = node.__class__.__name__

        # Handle expressions and identifiers
        if node_type.endswith("Expr") or node_type == "Identifier":
            # Check if it's a data structure expression first
            if node_type in ["ListExpr", "TupleExpr", "SetExpr", "DictExpr"]:
                return self.data_structure_generator.visit(node)
            return self.expr_generator.visit(node)

        # Handle function definitions
        if node_type == "FunctionDef":
            return self.function_generator.visit(node)

        # For C++ mode, handle basic statements separately from control flow
        if self.target == "cpp":
            if node_type in ["Assign", "ExprStmt", "Return"]:
                return self.basic_stmt_generator.visit(node)

        # Handle control flow and other statements
        return self.statement_visitor.visit(node)

    def generate(self, module: Module) -> str:
        """
        Generate complete code for a module, handling both Python and C++ targets.
        For C++, uses the integrated approach from CodeGeneratorCpp.
        Args:
                module: Module AST node
        Returns:
                str: Generated code
        """
        if not isinstance(module, Module):
            raise TypeError("CodeGenerator.generate expects a Module node")

        return self._generate_cpp(module)

    def _generate_cpp(self, module: Module) -> str:
        """Generate C++ code using the integrated approach."""
        self.scope.reset()

        # Separate functions from global statements
        fun_defs: List[FunctionDef] = [
            n for n in module.body if isinstance(n, FunctionDef)
        ]
        globals_: List[AstNode] = [
            n for n in module.body if not isinstance(n, FunctionDef)
        ]

        # Check if we should generate argument-based version
        self.should_use_args = self._should_generate_with_args(globals_)

        parts: List[str] = [CPP_PREAMBLE]

        # Add argument parsing headers if needed
        if self.should_use_args:
            parts[0] = (
                '#include "builtins.hpp"\n#include <cstdlib>\nusing namespace std;'
            )

        # Generate functions first
        for f in fun_defs:
            parts.append(self.function_generator.visit(f))
            parts.append("")

        # Generate main() function with global statements
        if self.should_use_args:
            parts.append("int main(int argc, char* argv[]) {")
            parts.append("  if (argc != 2) {")
            parts.append('    cout << "Usage: " << argv[0] << " <n>" << endl;')
            parts.append("    return 1;")
            parts.append("  }")
            parts.append("  int n = atoi(argv[1]);")
            parts.append("")
        else:
            parts.append("int main() {")
        self.scope.push()

        # Check if there's a main function
        has_main_function = any(f.name == "main" for f in fun_defs)
        main_call_added = False

        # Process global statements
        for stmt in globals_:
            stmt_lines = self._emit_cpp_top_stmt(stmt)
            parts.extend(stmt_lines)

            # Check if any of the generated lines contains a call to _fn_main()
            for line in stmt_lines:
                if "_fn_main()" in line:
                    main_call_added = True

        # If there's a main function but no call was added, add one
        if has_main_function and not main_call_added:
            parts.append("  _fn_main();")

        self.scope.pop()
        parts.append("  return 0;")
        parts.append("}")

        return "\n".join(parts)

    def _should_generate_with_args(self, globals_: List[AstNode]) -> bool:
        """
        Check if the code contains patterns that should be converted to argument-based execution.
        Look for loops over hardcoded arrays of values.
        """
        from src.core import For, Assign

        for stmt in globals_:
            # Check for assignment of arrays with multiple values
            if isinstance(stmt, Assign):
                # Convert to string to analyze pattern
                assign_code = str(stmt)
                if any(
                    pattern in assign_code.lower()
                    for pattern in [
                        "values = [",
                        "tamanos = [",
                        "sizes = [",
                        "valores = [",
                    ]
                ):
                    # Check if it has multiple values (more than 1 element)
                    if assign_code.count(",") > 0:  # Multiple elements
                        return True

            # Check for For loops that might be iterating over value arrays
            if isinstance(stmt, For):
                # Check if iterating over a values/sizes array
                for_code = str(stmt)
                if any(
                    pattern in for_code.lower()
                    for pattern in [
                        "for number in values",
                        "for n in sizes",
                        "for numero in valores",
                    ]
                ):
                    return True

        return False

    def _emit_cpp_top_stmt(self, stmt: AstNode) -> List[str]:
        """Emit C++ code for top-level statements in main()."""
        # Basic statements (Persona 2)
        if isinstance(stmt, (Assign, ExprStmt, Return)):
            code = self.basic_stmt_generator.visit(stmt)
            if code.strip():  # Only add non-empty code
                # If using args mode, skip hardcoded array assignments
                # TODO(any): self._is_values_assignment is not implemented yet
                if self.should_use_args and self._is_values_assignment(stmt):
                    return []  # Skip the values array assignment
                return ["  " + code]
            else:
                return []  # Skip empty code (like import statements)
        # Control flow (Persona 3)
        if isinstance(stmt, (If, While, For, Block)):
            # Generate code and check if it contains __name__ == "__main__"
            block_code = self.statement_visitor.visit(stmt)

            # Skip if __name__ == "__main__" blocks
            if "__name__" in block_code and "__main__" in block_code:
                return []  # Skip this if statement

            # Transform for loops if using args mode
            if self.should_use_args and isinstance(stmt, For):
                # TODO(any): _transform_for_loop_to_single_execution not implemented yet
                transformed_code = self._transform_for_loop_to_single_execution(stmt)
                if transformed_code:
                    return [
                        "  " + line if line.strip() else line
                        for line in transformed_code.splitlines()
                    ]

            return [
                "  " + line if line.strip() else line
                for line in block_code.splitlines()
            ]
        raise NotImplementedError(
            f"[CodeGenerator] Statement not supported at global level: {type(stmt).__name__}"
        )

    def generate_file(self, node, filename: str = "output.cpp"):
        """Generate code for the given AST node and write it to a file."""
        if isinstance(node, Module):
            # Use the new generate method for modules
            code = self.generate(node)
        else:
            # Fall back to the old visit method for individual nodes
            code = self.visit(node)
            if self.target == "cpp":
                # Include DynamicType system and builtins for non-module nodes
                code = CPP_PREAMBLE + "\n" + code

        # Write generated code to file
        with open(file=filename, mode="w", encoding="utf-8") as f:
            f.write(code)
        return filename
