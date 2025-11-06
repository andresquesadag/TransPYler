"""Top-level program generator that composes includes, runtime stubs, and
emits the main() function containing top-level statements.

This is a lightweight wrapper used by Person 3 to produce a complete C++ file
from an AST (list of statements or a module node). It delegates statement
generation to ControlFlowGenerator and expression generation to ExpressionGenerator.
"""

from typing import List
import os

from .control_flow_generator import ControlFlowGenerator
from .expr_generator import ExpressionGenerator
from ._stubs import get_stub_dynamic_value_class


class ProgramGenerator:
    def __init__(self, expression_gen: ExpressionGenerator = None):
        self.expr_gen = expression_gen or ExpressionGenerator()
        self.cf_gen = ControlFlowGenerator(self.expr_gen)

    def generate_cpp(self, statements: List[object]) -> str:
        """Generate a full C++ program string for the given top-level statements.

        `statements` can be a list of AST nodes (from src/core/ast).
        """
        # NOTE (Persona 3 provisional): ProgramGenerator creates a minimal C++ file
        # that includes a provisional DynamicValue runtime stub and wraps top-level
        # statements inside main(). This is intended for testing and prototyping the
        # code generation produced by Persona 3. Replace the runtime stub with the
        # final Persona 1 implementation when available.

        includes = """#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <stdexcept>
"""

        # Use stub dynamic value class (consumer may post-process it to use std::map)
        stub = get_stub_dynamic_value_class()

        # Separate global definitions (functions, classes) from top-level code
        # so function definitions are emitted at global scope, not inside main().
        from src.core.ast.ast_definitions import FunctionDef, ClassDef

        global_gen = ControlFlowGenerator(self.expr_gen)
        main_gen = ControlFlowGenerator(self.expr_gen)

        for stmt in statements:
            # Detect core AST FunctionDef/ClassDef or name-based fallbacks
            kind = getattr(stmt, '__class__', None)
            name = kind.__name__ if kind is not None else None
            if name in ('FunctionDef', 'ClassDef') or isinstance(stmt, FunctionDef) or isinstance(stmt, ClassDef):
                global_gen.visit(stmt)
            else:
                main_gen.visit(stmt)

        globals_code = global_gen.get_code()
        body = main_gen.get_code()

        main_code = f"""
{globals_code}
int main() {{
    // Top-level program
{body}
    return 0;
}}
"""

        return includes + "\n" + stub + "\n" + main_code
