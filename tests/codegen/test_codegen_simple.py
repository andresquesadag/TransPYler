from src.codegen.code_generator import CodeGenerator
from src.core.ast import LiteralExpr, Identifier

def test_codegen_literal():
    codegen = CodeGenerator(target="python")
    ast_node = LiteralExpr(value=100)
    result = codegen.visit(ast_node)
    assert result == "100"

def test_codegen_identifier():
    codegen = CodeGenerator(target="python")
    ast_node = Identifier(name="y")
    result = codegen.visit(ast_node)
    assert result == "y"
