from src.codegen.code_generator import CodeGenerator

def test_codegen_literal():
    codegen = CodeGenerator(target="python")
    ast_json = {
        "_type": "LiteralExpr",
        "value": 100
    }
    result = codegen.visit(ast_json)
    assert result == "100"

def test_codegen_identifier():
    codegen = CodeGenerator(target="python")
    ast_json = {
        "_type": "Identifier",
        "name": "y"
    }
    result = codegen.visit(ast_json)
    assert result == "y"
