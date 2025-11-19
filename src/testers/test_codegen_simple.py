"""
Test basic code generation for C++
This tests the core CodeGenerator visitor methods for simple expressions.
"""
import pytest
from src.codegen.code_generator import CodeGenerator
from src.core.ast import LiteralExpr, Identifier

def test_codegen_literal():
    """Test literal expression generation."""
    codegen = CodeGenerator()
    ast_node = LiteralExpr(value=42)
    result = codegen.visit(ast_node)
    # C++ wraps literals in DynamicType
    assert result == "DynamicType(42)"

def test_codegen_identifier():
    """Test identifier generation."""
    codegen = CodeGenerator()
    ast_node = Identifier(name="x")
    result = codegen.visit(ast_node)
    # Identifiers are used as-is in C++
    assert result == "x"
