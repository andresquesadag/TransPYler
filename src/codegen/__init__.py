"""
Codegen Package Init
--------------------
This file initializes the codegen package and provides helpers for automated tests.

Key Features:
- Imports all codegen modules.
- Provides a test entry point for code generation modules.
"""

# Import codegen modules
from .code_generator import CodeGenerator
from .expr_generator import ExprGenerator
from .statement_generator import StatementVisitor
from .function_generator import FunctionGenerator
from .basic_statement_generator import BasicStatementGenerator
from .data_structure_generator import DataStructureGenerator
from .scope_manager import ScopeManager

__all__ = [
    "CodeGenerator",
    "ExprGenerator", 
    "StatementVisitor",
    "FunctionGenerator",
    "BasicStatementGenerator",
    "DataStructureGenerator",
    "ScopeManager"
]

# Helpers for automated tests
def test_codegen():
    """
    Unit tests for code generators are implemented in the tests/ directory.
    Example tests include: if statements, for loops, lists, functions, expressions, DynamicType.
    """
    print("Code generation tests are located in tests/codegen/")
    return True