import pytest
from src.codegen.code_generator import CodeGenerator

def test_codegen_literal():
    codegen = CodeGenerator(target="python")
    ast_json = {
        "_type": "LiteralExpr",
        "value": 42
    }
    result = codegen.visit(ast_json)
    assert result == "42"

def test_codegen_identifier():
    codegen = CodeGenerator(target="python")
    ast_json = {
        "_type": "Identifier",
        "name": "x"
    }
    result = codegen.visit(ast_json)
    assert result == "x"
