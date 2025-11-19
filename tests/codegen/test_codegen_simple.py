"""
Test basic code generation for C++
This tests the core CodeGenerator visitor methods for simple expressions.
"""
from src.codegen.code_generator import CodeGenerator
from src.core.ast import LiteralExpr, Identifier

def test_codegen_literal():
    """Test literal expression generation."""
    codegen = CodeGenerator()
    ast_node = LiteralExpr(value=100)
    result = codegen.visit(ast_node)
    # C++ wraps literals in DynamicType
    assert result == "DynamicType(100)"

def test_codegen_identifier():
    """Test identifier generation."""
    codegen = CodeGenerator()
    ast_node = Identifier(name="y")
    result = codegen.visit(ast_node)
    # Identifiers are used as-is in C++
    assert result == "y"
