"""
test_codegen_cpp_integration.py
-------------------------------
Integration tests for CodeGeneratorCpp (Persona 2): end-to-end C++ code generation from Module ASTs.

Tests validate the full code generation pipeline:
- Preamble generation (#include directives, using namespace)
- Function generation with parameters and bodies
- Global variable declarations and assignments in main()
- Special operator mappings (e.g., ** to builtins::pow)
- Complete Module → .cpp transformation

All tests use pytest and validate generated C++ code via string assertions.
"""

import pytest
from src.core import (
    Module, FunctionDef, Identifier, LiteralExpr, BinaryExpr,
    Assign, Return
)
from src.codegen.code_generator_cpp import CodeGeneratorCpp


# ============ CodeGeneratorCpp Integration Tests ============

class TestCodeGeneratorCppIntegration:
    """Test full code generation pipeline with CodeGeneratorCpp."""

    def test_simple_module_with_function(self):
        """Test generating C++ for a module with one function."""
        fn = FunctionDef(
            name="add",
            params=[Identifier(name="a"), Identifier(name="b")],
            body=[
                Assign(
                    target=Identifier(name="x"),
                    value=BinaryExpr(left=Identifier(name="a"), op="+", right=Identifier(name="b"))
                ),
                Return(value=Identifier(name="x"))
            ]
        )
        module = Module(body=[fn])
        gen = CodeGeneratorCpp()
        code = gen.generate(module)

        # Check preamble
        assert "#include <iostream>" in code
        assert "#include \"dynamic_type.hpp\"" in code

        # Check function
        assert "_fn_add(DynamicType a, DynamicType b)" in code
        assert "DynamicType x = ((a) + (b));" in code

        # Check main
        assert "int main()" in code
        assert "return 0;" in code

    def test_module_with_pow_operation(self):
        """Test ** operator mapping in generated code."""
        fn = FunctionDef(
            name="power",
            params=[Identifier(name="a"), Identifier(name="b")],
            body=[
                Return(value=BinaryExpr(left=Identifier(name="a"), op="**", right=Identifier(name="b")))
            ]
        )
        module = Module(body=[fn])
        gen = CodeGeneratorCpp()
        code = gen.generate(module)

        assert "builtins::pow(a, b)" in code

    def test_module_with_globals(self):
        """Test module with global statements in main()."""
        fn = FunctionDef(
            name="test",
            params=[],
            body=[Return(value=LiteralExpr(value=1))]
        )
        global_assign = Assign(target=Identifier(name="g"), value=LiteralExpr(value=10))
        
        module = Module(body=[fn, global_assign])
        gen = CodeGeneratorCpp()
        code = gen.generate(module)

        # Check function
        assert "_fn_test()" in code

        # Check global in main
        assert "int main()" in code
        assert "DynamicType g = DynamicType(10);" in code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
