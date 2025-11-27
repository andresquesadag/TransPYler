"""
function_generator.py
---------------------
FunctionGenerator: Generates code for function definitions and scope management.

This module provides the FunctionGenerator class, which generates C++ code for function definitions, parameters, and return statements.
Key Features:
- Supports parameter handling, return statements, and extensibility for advanced function features.
- Includes helpers for scope and parameter management.
- Used by CodeGenerator to handle all function-related code generation.
"""

from typing import List
from src.core import (
    AstNode,
    FunctionDef,
    Identifier,
    Assign,
    ExprStmt,
    Return,
    Block,
    If,
    While,
    For,
)
from .scope_manager import ScopeManager
from .expr_generator import ExprGenerator
from .basic_statement_generator import BasicStatementGenerator
from .statement_generator import StatementVisitor


class FunctionGenerator:
    def __init__(self, scope: ScopeManager):
        """
        Initializes the FunctionGenerator for C++ code generation.
        Args:
                scope (ScopeManager): Scope manager for tracking variable declarations.
        """
        self.scope = scope
        self.expr_gen = ExprGenerator(scope=self.scope)
        self.basic_stmt = BasicStatementGenerator(self.scope)
        self.ctrl_stmt = StatementVisitor(
            expr_generator=self.expr_gen,
            scope_manager=self.scope,
            basic_stmt_generator=self.basic_stmt,
        )

    def visit(self, node: FunctionDef) -> str:
        if not isinstance(node, FunctionDef):
            raise TypeError("FunctionGenerator.visit() expects a FunctionDef")

        #  ------- Function Definition -------
        param_names: List[str] = []
        for p in node.params:
            if isinstance(p, Identifier):
                param_names.append(p.name)
            else:
                param_names.append(str(p))

        cpp_params = ", ".join(f"DynamicType {n}" for n in param_names)
        header = f"DynamicType _fn_{node.name}({cpp_params}) {{"
        #  ------- Function scope -------
        self.scope.push()
        try:
            for n in param_names:
                if not self.scope.exists(n):
                    self.scope.declare(n)
            #  ------- Function Body -------
            body_lines: List[str] = []
            # node.body can be either a list of statements or a Block node
            if isinstance(node.body, list):
                statements = node.body
            elif hasattr(node.body, "statements"):
                statements = node.body.statements
            else:
                statements = [node.body]

            for stmt in statements:
                body_lines.append(self._emit_stmt(stmt))
            has_top_return = any(isinstance(s, Return) for s in statements)
            lines = [header]
            for line in body_lines:
                if line is None:
                    continue
                for sub in line.splitlines():
                    lines.append("	" + sub)
            if not has_top_return:
                lines.append("	return DynamicType();")
            lines.append("}")
            return "\n".join(lines)
        finally:
            self.scope.pop()

    def _emit_stmt(self, stmt: AstNode) -> str:
        # Basic statements (assignments, expressions, returns)
        if isinstance(stmt, (Assign, ExprStmt, Return)):
            return self.basic_stmt.visit(stmt)
        # Control flow statements (if, while, for, blocks)
        if isinstance(stmt, (If, While, For, Block)):
            return self.ctrl_stmt.visit(stmt)
        # If it's an unknown statement type, try basic_stmt first, then ctrl_stmt
        try:
            return self.basic_stmt.visit(stmt)
        except (NotImplementedError, AttributeError):
            try:
                return self.ctrl_stmt.visit(stmt)
            except (NotImplementedError, AttributeError):
                raise NotImplementedError(
                    f"[FunctionGenerator] Statement type {type(stmt).__name__} not supported"
                )
