"""
test_codegen_functions.py David 
-------------------------
Unit tests for FunctionGenerator: function definitions, parameters, scope, and returns.

Tests validate code generation for:
- Function headers with parameters (DynamicType typing
- Function bodies with assignments and returns
- Automatic return insertion when none exists
- Scope push/pop for function-local variables
- Complex functions with multiple statements
"""

import pytest
from src.core import (
    FunctionDef, Identifier, LiteralExpr, BinaryExpr,
    Assign, ExprStmt, Return
)
from src.codegen.function_generator import FunctionGenerator
from src.codegen.scope_manager import ScopeManager


# ============ FunctionGenerator Unit Tests ============

class TestFunctionGeneratorBasic:
    """Test function definition generation."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.gen = FunctionGenerator(scope=self.scope)

    def test_function_no_params_no_body(self):
        """Test function with no parameters and no body."""
        fn = FunctionDef(name="empty", params=[], body=[])
        code = self.gen.emit(fn)
        assert "DynamicType _fn_empty()" in code
        assert "return DynamicType();" in code
        assert code.endswith("}")

    def test_function_with_params(self):
        """Test function with parameters."""
        fn = FunctionDef(
            name="add",
            params=[Identifier(name="a"), Identifier(name="b")],
            body=[]
        )
        code = self.gen.emit(fn)
        assert "DynamicType _fn_add(DynamicType a, DynamicType b)" in code

    def test_function_with_assignment(self):
        """Test function with assignment statement."""
        fn = FunctionDef(
            name="test",
            params=[],
            body=[
                Assign(target=Identifier(name="x"), value=LiteralExpr(value=10))
            ]
        )
        code = self.gen.emit(fn)
        assert "DynamicType x = DynamicType(10);" in code
        assert "_fn_test" in code

    def test_function_with_return(self):
        """Test function with explicit return."""
        fn = FunctionDef(
            name="get_value",
            params=[],
            body=[
                Return(value=LiteralExpr(value=42))
            ]
        )
        code = self.gen.emit(fn)
        assert "return DynamicType(42);" in code
        # Should not add automatic return when explicit return exists
        assert code.count("return") == 1

    def test_function_auto_return_when_no_explicit_return(self):
        """Test function adds automatic return when none exists."""
        fn = FunctionDef(
            name="test",
            params=[],
            body=[
                ExprStmt(value=LiteralExpr(value=10))
            ]
        )
        code = self.gen.emit(fn)
        assert "return DynamicType();" in code

    def test_function_scope_push_pop(self):
        """Test that function manages scope correctly."""
        fn = FunctionDef(
            name="test",
            params=[Identifier(name="x")],
            body=[
                Assign(target=Identifier(name="y"), value=Identifier(name="x"))
            ]
        )
        initial_scope_count = len(self.scope.all_scopes())
        code = self.gen.emit(fn)
        final_scope_count = len(self.scope.all_scopes())
        # Scope should be back to initial state after function generation
        assert initial_scope_count == final_scope_count

    def test_function_complex(self):
        """Test complex function with multiple statements."""
        fn = FunctionDef(
            name="add",
            params=[Identifier(name="a"), Identifier(name="b")],
            body=[
                Assign(
                    target=Identifier(name="sum"),
                    value=BinaryExpr(left=Identifier(name="a"), op="+", right=Identifier(name="b"))
                ),
                Return(value=Identifier(name="sum"))
            ]
        )
        code = self.gen.emit(fn)
        assert "_fn_add(DynamicType a, DynamicType b)" in code
        assert "DynamicType sum = ((a) + (b));" in code
        assert "return sum;" in code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
