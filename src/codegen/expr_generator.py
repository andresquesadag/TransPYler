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
    return s.replace("\\", r"\\").replace('"', r"\"")


class ExprGenerator:
    def __init__(self, scope: Optional[object] = None):
        self.scope = scope
        # Will be injected by CodeGenerator for data structure delegation
        self.data_structure_generator = None

    # Dispatcher (Visitor Pattern)
    def visit(self, node: AstNode) -> str:
        m = getattr(self, f"visit_{type(node).__name__}", None)
        if not m or not callable(m):
            raise NotImplementedError(
                f"ExprGenerator does not support nodes of type {type(node).__name__}"
            )
        return m(node)

    # ---------- Literals ----------
    def visit_LiteralExpr(self, node: LiteralExpr) -> str:
        v = node.value
        
        # Generate C++ DynamicType literals
        if isinstance(v, str):
            return f'DynamicType(std::string("{_escape_cpp_string(v)}"))'
        if isinstance(v, bool):
            return f"DynamicType({str(v).lower()})"
        if v is None:
            return "DynamicType()"
        if isinstance(v, (int, float)):
            return f"DynamicType({v})"
        
        raise NotImplementedError(
            f"LiteralExpr with value of type: {type(v).__name__} is not supported"
        )

    # ---------- Identifiers ----------
    def visit_Identifier(self, node: Identifier) -> str:
        name = node.name
        # Note: We're relaxing scope checking as loop variables and function parameters
        # are handled specially and may not be in the main scope when checked
        return name

    # ---------- Unary Expressions  ----------
    def visit_UnaryExpr(self, node: UnaryExpr) -> str:
        rhs = self.visit(node.operand)
        if node.op == "-":
            return f"(DynamicType(0) - ({rhs}))"
        if node.op in ("not", "!", "NOT"):
            return f"(!({rhs}))"
        raise NotImplementedError(f"Unary op '{node.op}' is not supported")

    # ---------- Binary expressions ----------
    def visit_BinaryExpr(self, node: BinaryExpr) -> str:
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        op = node.op
        
        # For C++, use DynamicType
        if op == "**":
            return f"DynamicType(pow({lhs}.toDouble(), {rhs}.toDouble()))"

        mapped = _BIN_OP_CPP.get(op)
        if not mapped:
            raise NotImplementedError(f"Binary Op '{op}' is not supported")
        
        # Logical operators - lhs and rhs are DynamicType, convert to bool for logical op
        if op in ("and", "or"):
            return f"DynamicType(({lhs}).toBool() {mapped} ({rhs}).toBool())"
        
        # Arithmetic operators
        return f"({lhs}) {mapped} ({rhs})"

    # ---------- Comparison expressions ----------
    def visit_ComparisonExpr(self, node) -> str:
        """Handle comparison expressions (==, !=, <, <=, >, >=)."""
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        op = node.op
        
        mapped = _BIN_OP_CPP.get(op)
        if not mapped:
            raise NotImplementedError(f"Comparison Op '{op}' is not supported")
        # Wrap in DynamicType for consistency
        return f"DynamicType(({lhs}) {mapped} ({rhs}))"

    # ---------- Funct calls ----------
    def visit_CallExpr(self, node: CallExpr) -> str:
        if isinstance(node.callee, Identifier):
            callee = node.callee.name
        elif isinstance(node.callee, Attribute):
            raise NotImplementedError("Method calls are not supported by CallExpr")
        else:
            raise NotImplementedError("callee type not supported in CallExpr")

        builtin_mapping = {
            "print": "print",
            "len": "len",
            "range": "range",
            "str": "str",
            "int": "int_",
            "float": "float_",
            "bool": "bool_",
            "abs": "abs",
            "min": "min",
            "max": "max",
            "sum": "sum",
            "type": "type",
            "input": "input",
        }
        
        # Use DynamicType overloads for all builtin functions including range()
        args = [self.visit(a) for a in node.args]
            
        # if it's a builtin function
        if callee in builtin_mapping:
            cpp_name = builtin_mapping[callee]
            return f"{cpp_name}({', '.join(args)})"
        # Else, it's a user-defined function
        return f"_fn_{callee}({', '.join(args)})"

    # ---------- Data structure expressions (delegate to DataStructureGenerator) ----------
    def visit_ListExpr(self, node) -> str:
        """Delegate list expressions to DataStructureGenerator."""
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        # Fallback implementation
        elements = [self.visit(e) for e in node.elements]
        elements_str = ', '.join(elements)
        return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"

    def visit_DictExpr(self, node) -> str:
        """Delegate dict expressions to DataStructureGenerator."""
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        # Fallback implementation
        pairs = []
        for k, v in node.pairs:
            key_code = self.visit(k)
            val_code = self.visit(v)
            pairs.append(f"{{({key_code}).toString(), {val_code}}}")
        pairs_str = ', '.join(pairs)
        return f"DynamicType(std::map<std::string, DynamicType>{{{pairs_str}}})"

    def visit_TupleExpr(self, node) -> str:
        """Delegate tuple expressions to DataStructureGenerator."""
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        # Fallback implementation (represent as vector)
        elements = [self.visit(e) for e in node.elements]
        elements_str = ', '.join(elements)
        return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"

    def visit_SetExpr(self, node) -> str:
        """Delegate set expressions to DataStructureGenerator."""
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        # Fallback implementation (represent as vector)
        elements = [self.visit(e) for e in node.elements]
        elements_str = ', '.join(elements)
        return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"

    # ---------- Subscript expressions (indexing and slicing) ----------
    def visit_Subscript(self, node) -> str:
        """Handle subscript operations like a[i] or dict[key]."""
        obj_code = self.visit(node.value)
        index_code = self.visit(node.index)
        
        # Use DynamicType operator[] which automatically handles conversion
        # from DynamicType to appropriate index type (size_t for numbers, string for strings)
        return f"({obj_code})[{index_code}]"
