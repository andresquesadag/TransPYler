import pytest
from src.codegen.code_generator import CodeGenerator
from src.core.ast import LiteralExpr, Identifier

def test_codegen_literal():
    codegen = CodeGenerator(target="python")
    ast_node = LiteralExpr(value=42)
    result = codegen.visit(ast_node)
    assert result == "42"

def test_codegen_identifier():
    codegen = CodeGenerator(target="python")
    ast_node = Identifier(name="x")
    result = codegen.visit(ast_node)
    assert result == "x"
