"""
TestPersona3
------------
This module provides unit tests for Persona 3: control flow and data structure code generation in Python and C++.

Key Features:
- Validates code generation for if, for, lists, and break statements using the AST and code generators.
- Ensures correct integration of codegen modules for control flow and collections.
"""
"""
Tests for Persona 3: Control flow and data structure code generation (Python and C++).

Validates code generation for if, for, lists, and break statements using the AST and code generators.
"""
import unittest
from src.codegen.code_generator import CodeGenerator
from src.core.ast.ast_statements import If, While, For, Block, Break, Continue, Pass
from src.core.ast.ast_expressions import ListExpr, LiteralExpr

class TestPersona3(unittest.TestCase):
    def setUp(self):
        self.codegen_py = CodeGenerator(target="python")
        self.codegen_cpp = CodeGenerator(target="cpp")

    def test_if_python(self):
        ast = If(
            cond=LiteralExpr(value=True),
            body=Block(statements=[Pass()]),
            elifs=[],
            orelse=None
        )
        code = self.codegen_py.visit(ast)
        self.assertIn("if True:", code)
        self.assertIn("pass", code)

    def test_for_cpp(self):
        ast = For(
            target=LiteralExpr(value="i"),
            iterable=ListExpr(elements=[LiteralExpr(value=1), LiteralExpr(value=2)]),
            body=Block(statements=[Break()])
        )
        code = self.codegen_cpp.visit(ast)
        self.assertIn("for (int i : std::vector<int>{1, 2})", code)
        self.assertIn("break;", code)

    def test_list_python(self):
        ast = ListExpr(elements=[LiteralExpr(value=1), LiteralExpr(value=2)])
        code = self.codegen_py.visit(ast)
        self.assertEqual(code, "[1, 2]")

    def test_list_cpp(self):
        ast = ListExpr(elements=[LiteralExpr(value=1), LiteralExpr(value=2)])
        code = self.codegen_cpp.visit(ast)
        self.assertEqual(code, "std::vector<int>{1, 2}")

if __name__ == "__main__":
    unittest.main()
