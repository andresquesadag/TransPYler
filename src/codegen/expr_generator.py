"""
ExprGenerator
-------------
This module provides the ExprGenerator class, which generates code for expressions and literals (Persona 2).

Key Features:
- Handles conversion of operators, literals, assignments, and special cases (e.g., pow(a, b) for a**b in Python).
- Includes helpers for scope management and extensibility for new expression types.
- Used by CodeGenerator to handle all expression-related code generation.
"""

"""
ExprGenerator: Generates code for expressions and literals (Persona 2).

Handles conversion of operators, literals, assignments, and special cases (e.g., pow(a, b) for a**b in Python).
Includes helpers for scope management and extensibility for new expression types.
"""
from typing import Optional
from src.core import (
    AstNode,
    LiteralExpr,
    Identifier,
    UnaryExpr,
    BinaryExpr,
    CallExpr,
    Attribute,
)

# Operadores binarios mapeo a C++
_BIN_OP_CPP = {
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "%": "%",
    "==": "==",
    "!=": "!=",
    "<": "<",
    "<=": "<=",
    ">": ">",
    ">=": ">=",
    "and": "&&",
    "or": "||",
}


def _escape_cpp_string(s: str) -> str:
    # Escapa comillas y backslashes para literales de C++
    return s.replace("\\", r"\\").replace('"', r"\"")


class ExprGenerator:
    def __init__(self, scope: Optional[object] = None):
        self.scope = scope

    # Dispatcher (Visitor Pattern)
    def visit(self, node: AstNode) -> str:
        m = getattr(self, f"visit_{type(node).__name__}", None)
        if not m:
            raise NotImplementedError(
                f"ExprGenerator no soporta nodos de tipo {type(node).__name__}"
            )
        return m(node) # TODO(any): m is not callable

    # ---------- Literales ----------
    def visit_LiteralExpr(self, node: LiteralExpr) -> str:
        v = node.value
        if isinstance(v, str):
            return f'DynamicType(std::string("{_escape_cpp_string(v)}"))'
        if isinstance(v, bool):
            return f"DynamicType({str(v).lower()})"
        if v is None:
            return "DynamicType()"
        if isinstance(v, (int, float)):
            return f"DynamicType({v})"
        raise NotImplementedError(
            f"LiteralExpr con valor de tipo {type(v).__name__} no soportado"
        )

    # ---------- Identificadores ----------
    def visit_Identifier(self, node: Identifier) -> str:
        name = node.name
        if self.scope is not None and hasattr(self.scope, "exists"):
            if not self.scope.exists(name):
                raise NameError(
                    f"Identificador '{name}' no definido en el scope actual"
                )
        return name

    # ---------- Expresiones Unarias ----------
    def visit_UnaryExpr(self, node: UnaryExpr) -> str:
        rhs = self.visit(node.operand)
        if node.op == "-":
            return f"(DynamicType(0) - ({rhs}))"
        if node.op in ("not", "!"):
            return f"(!({rhs}))"
        raise NotImplementedError(f"Operador unario '{node.op}' no soportado")

    # ---------- Expresiones Binarias ----------
    def visit_BinaryExpr(self, node: BinaryExpr) -> str:
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        op = node.op
        if op == "**":
            return f"builtins::pow({lhs}, {rhs})"

        mapped = _BIN_OP_CPP.get(op)
        if not mapped:
            raise NotImplementedError(f"Operador binario '{op}' no soportado")
        return f"(({lhs}) {mapped} ({rhs}))"

    # ---------- Llamadas a Funciones ----------
    def visit_CallExpr(self, node: CallExpr) -> str:
        if isinstance(node.callee, Identifier):
            callee = node.callee.name
        elif isinstance(node.callee, Attribute):
            raise NotImplementedError("Llamadas a métodos no soportadas aún")
        else:
            raise NotImplementedError("Tipo de callee no soportado en CallExpr")

        args = [self.visit(a) for a in node.args]
        return f"_fn_{callee}({', '.join(args)})"
