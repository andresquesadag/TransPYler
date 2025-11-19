"""
test_codegen_statements.py David
---------------------------
Unit tests for BasicStatementGenerator: assignments, expression statements, and returns.

Tests validate code generation for:
- Assignments: first declaration vs reassignment with DynamicType
- Expression statements: literal and function call expressions with semicolons
- Return statements: no value, literal, identifier, and complex expressions
"""

import pytest
from src.core import (
    Identifier, LiteralExpr, UnaryExpr, BinaryExpr, CallExpr,
    Assign, ExprStmt, Return
)
from src.codegen.basic_statement_generator import BasicStatementGenerator
from src.codegen.scope_manager import ScopeManager


# ============ BasicStatementGenerator Assignment Tests ============

class TestBasicStatementGeneratorAssign:
    """Test assignment statement generation."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.gen = BasicStatementGenerator(scope=self.scope)

    def test_assign_first_declaration(self):
        """Test first assignment declaration (new variable)."""
        stmt = Assign(target=Identifier(name="x"), value=LiteralExpr(value=10))
        code = self.gen.visit(stmt)
        assert "DynamicType x = DynamicType(10);" in code
        # Verify variable is now in scope
        assert self.scope.exists("x")

    def test_assign_reassignment(self):
        """Test reassignment to existing variable."""
        self.scope.declare("x")
        stmt = Assign(target=Identifier(name="x"), value=LiteralExpr(value=20))
        code = self.gen.visit(stmt)
        assert "x = DynamicType(20);" in code
        assert "DynamicType x" not in code  # Should not redeclare

    def test_assign_multiple_variables(self):
        """Test assigning to different variables."""
        stmt1 = Assign(target=Identifier(name="x"), value=LiteralExpr(value=1))
        code1 = self.gen.visit(stmt1)
        assert "DynamicType x = DynamicType(1);" in code1

        stmt2 = Assign(target=Identifier(name="y"), value=LiteralExpr(value=2))
        code2 = self.gen.visit(stmt2)
        assert "DynamicType y = DynamicType(2);" in code2

    def test_assign_with_expression(self):
        """Test assignment with complex expression."""
        self.scope.declare("a")
        self.scope.declare("b")
        stmt = Assign(
            target=Identifier(name="c"),
            value=BinaryExpr(left=Identifier(name="a"), op="+", right=Identifier(name="b"))
        )
        code = self.gen.visit(stmt)
        assert "DynamicType c = " in code
        assert "(a) + (b)" in code

    def test_assign_non_identifier_target_raises_error(self):
        """Test that non-identifier targets raise NotImplementedError."""
        stmt = Assign(target=LiteralExpr(value=10), value=LiteralExpr(value=20))
        with pytest.raises(NotImplementedError):
            self.gen.visit(stmt)


# ============ BasicStatementGenerator Expression Statement Tests ============

class TestBasicStatementGeneratorExprStmt:
    """Test expression statements."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.gen = BasicStatementGenerator(scope=self.scope)

    def test_expr_stmt_literal(self):
        """Test expression statement with literal."""
        stmt = ExprStmt(value=LiteralExpr(value=42))
        code = self.gen.visit(stmt)
        assert "DynamicType(42);" in code

    def test_expr_stmt_function_call(self):
        """Test expression statement with function call."""
        stmt = ExprStmt(value=CallExpr(callee=Identifier(name="print"), args=[LiteralExpr(value="hi")]))
        code = self.gen.visit(stmt)
        # print is a builtin, so it's not prefixed with _fn_
        assert "print(DynamicType(std::string(\"hi\")));" in code


# ============ BasicStatementGenerator Return Tests ============

class TestBasicStatementGeneratorReturn:
    """Test return statements."""

    def setup_method(self):
        self.scope = ScopeManager()
        self.gen = BasicStatementGenerator(scope=self.scope)

    def test_return_no_value(self):
        """Test return without value."""
        stmt = Return(value=None)
        code = self.gen.visit(stmt)
        assert "return DynamicType();" in code

    def test_return_with_literal(self):
        """Test return with literal value."""
        stmt = Return(value=LiteralExpr(value=42))
        code = self.gen.visit(stmt)
        assert "return DynamicType(42);" in code

    def test_return_with_identifier(self):
        """Test return with identifier."""
        self.scope.declare("x")
        stmt = Return(value=Identifier(name="x"))
        code = self.gen.visit(stmt)
        assert "return x;" in code

    def test_return_with_expression(self):
        """Test return with complex expression."""
        self.scope.declare("a")
        self.scope.declare("b")
        stmt = Return(
            value=BinaryExpr(left=Identifier(name="a"), op="+", right=Identifier(name="b"))
        )
        code = self.gen.visit(stmt)
        assert "return " in code
        assert "(a) + (b)" in code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
