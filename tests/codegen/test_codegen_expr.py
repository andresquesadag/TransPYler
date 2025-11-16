"""
test_codegen_expr.py David 
--------------------
Unit tests for ExprGenerator: expressions, literals, operators, and function calls.

Tests validate code generation for:
- Literal expressions (int, float, string, bool, None)
- Identifiers with scope validation
- Unary operations (-, not)
- Binary operations (+, -, *, /, %, ==, !=, <, and, or, **)
- Function call expressions (no args, single arg, multiple args, nested expressions)
"""

import pytest
from src.core import (
    LiteralExpr, Identifier, UnaryExpr, BinaryExpr, CallExpr
)
from src.codegen.expr_generator import ExprGenerator
from src.codegen.scope_manager import ScopeManager


# ============ ExprGenerator Literal Tests ============

class TestExprGeneratorLiterals:
    """Test literal expression generation."""

    def setup_method(self):
        """Setup before each test."""
        self.scope = ScopeManager()
        self.gen = ExprGenerator(scope=self.scope)

    def test_literal_int(self):
        """Test integer literal generation."""
        expr = LiteralExpr(value=42)
        code = self.gen.visit(expr)
        assert "DynamicType(42)" in code

    def test_literal_float(self):
        """Test float literal generation."""
        expr = LiteralExpr(value=3.14)
        code = self.gen.visit(expr)
        assert "DynamicType(3.14)" in code

    def test_literal_string(self):
        """Test string literal generation with escaping."""
        expr = LiteralExpr(value="hello")
        code = self.gen.visit(expr)
        assert 'DynamicType(std::string("hello"))' in code

    def test_literal_string_with_quotes(self):
        """Test string literal with escaped quotes."""
        expr = LiteralExpr(value='he said "hi"')
        code = self.gen.visit(expr)
        assert '\\"' in code

    def test_literal_bool_true(self):
        """Test boolean true literal."""
        expr = LiteralExpr(value=True)
        code = self.gen.visit(expr)
        assert "DynamicType(true)" in code

    def test_literal_bool_false(self):
        """Test boolean false literal."""
        expr = LiteralExpr(value=False)
        code = self.gen.visit(expr)
        assert "DynamicType(false)" in code

    def test_literal_none(self):
        """Test None literal."""
        expr = LiteralExpr(value=None)
        code = self.gen.visit(expr)
        assert "DynamicType()" in code


# ============ ExprGenerator Identifier Tests ============

class TestExprGeneratorIdentifiers:
    """Test identifier generation and scope validation."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.gen = ExprGenerator(scope=self.scope)

    def test_identifier_without_scope_check(self):
        """Identifier without scope validation should generate name only."""
        gen_no_scope = ExprGenerator(scope=None)
        expr = Identifier(name="x")
        code = gen_no_scope.visit(expr)
        assert code == "x"

    def test_identifier_with_declared_scope(self):
        """Identifier in declared scope should generate name."""
        self.scope.declare("x")
        expr = Identifier(name="x")
        code = self.gen.visit(expr)
        assert code == "x"

    def test_identifier_undeclared_raises_error(self):
        """Undeclared identifier should raise NameError."""
        expr = Identifier(name="undefined_var")
        with pytest.raises(NameError):
            self.gen.visit(expr)


# ============ ExprGenerator Unary Op Tests ============

class TestExprGeneratorUnaryOps:
    """Test unary operations."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.scope.declare("x")
        self.gen = ExprGenerator(scope=self.scope)

    def test_unary_minus(self):
        """Test unary minus operator."""
        expr = UnaryExpr(op="-", operand=Identifier(name="x"))
        code = self.gen.visit(expr)
        assert "(DynamicType(0) - (x))" in code

    def test_unary_not(self):
        """Test logical NOT operator."""
        expr = UnaryExpr(op="not", operand=Identifier(name="x"))
        code = self.gen.visit(expr)
        assert "(!(x))" in code


# ============ ExprGenerator Binary Op Tests ============

class TestExprGeneratorBinaryOps:
    """Test binary operations and operator mapping."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.scope.declare("a")
        self.scope.declare("b")
        self.gen = ExprGenerator(scope=self.scope)

    def test_binary_add(self):
        """Test addition operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="+", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) + (b))" in code

    def test_binary_subtract(self):
        """Test subtraction operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="-", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) - (b))" in code

    def test_binary_multiply(self):
        """Test multiplication operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="*", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) * (b))" in code

    def test_binary_divide(self):
        """Test division operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="/", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) / (b))" in code

    def test_binary_modulo(self):
        """Test modulo operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="%", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) % (b))" in code

    def test_binary_power_maps_to_pow(self):
        """Test power operator ** maps to builtins::pow."""
        expr = BinaryExpr(left=Identifier(name="a"), op="**", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "builtins::pow(a, b)" in code

    def test_binary_equality(self):
        """Test equality operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="==", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) == (b))" in code

    def test_binary_inequality(self):
        """Test inequality operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="!=", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) != (b))" in code

    def test_binary_less_than(self):
        """Test less than operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="<", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) < (b))" in code

    def test_binary_and_operator(self):
        """Test logical AND operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="and", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) && (b))" in code

    def test_binary_or_operator(self):
        """Test logical OR operator."""
        expr = BinaryExpr(left=Identifier(name="a"), op="or", right=Identifier(name="b"))
        code = self.gen.visit(expr)
        assert "((a) || (b))" in code


# ============ ExprGenerator Call Expression Tests ============

class TestExprGeneratorCallExpr:
    """Test function call expressions."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.gen = ExprGenerator(scope=self.scope)

    def test_call_no_args(self):
        """Test function call with no arguments."""
        expr = CallExpr(callee=Identifier(name="foo"), args=[])
        code = self.gen.visit(expr)
        assert "_fn_foo()" in code

    def test_call_one_arg(self):
        """Test function call with one argument."""
        expr = CallExpr(callee=Identifier(name="add"), args=[LiteralExpr(value=5)])
        code = self.gen.visit(expr)
        assert "_fn_add(DynamicType(5))" in code

    def test_call_multiple_args(self):
        """Test function call with multiple arguments."""
        expr = CallExpr(
            callee=Identifier(name="add"),
            args=[LiteralExpr(value=1), LiteralExpr(value=2)]
        )
        code = self.gen.visit(expr)
        assert "_fn_add(DynamicType(1), DynamicType(2))" in code

    def test_call_nested_expression_arg(self):
        """Test function call with nested expression as argument."""
        self.scope.declare("x")
        self.scope.declare("y")
        expr = CallExpr(
            callee=Identifier(name="add"),
            args=[
                BinaryExpr(left=Identifier(name="x"), op="+", right=Identifier(name="y"))
            ]
        )
        code = self.gen.visit(expr)
        assert "_fn_add(((x) + (y)))" in code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
