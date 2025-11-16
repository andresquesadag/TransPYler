"""
AST nodes for expressions.
"""


from dataclasses import dataclass, field
from typing import Any, List, Tuple, Optional
from .ast_base import AstNode


# ---------- Atomic expressions ----------
@dataclass
class LiteralExpr(AstNode):
    """
    Represents a literal value(numbers, strings, True/False/None (and basic collections after)).
    """
    value: Any = field(default=None)


@dataclass
class Identifier(AstNode):
    """
    Represents an identifier (variable or function name).
    """
    name: str = field(default="")


# ---------- Operators ----------
@dataclass
class UnaryExpr(AstNode):
    """
    Represents a unary operation, e.g. -x, +y, not z
    """
    op: str = field(default="")
    operand: Optional[AstNode] = field(default=None)


@dataclass
class BinaryExpr(AstNode):
    """
    Represents a binary operation, e.g. x + y, a * b, c ** d
    """
    left: Optional[AstNode] = field(default=None)
    op: str = field(default="")  # "PLUS", "MINUS", "TIMES", "POWER", etc. (token o symbol)
    right: Optional[AstNode] = field(default=None)


@dataclass
class ComparisonExpr(AstNode):
    """
    Represents a comparison operation, e.g. x < y, a == b
    """
    left: Optional[AstNode] = field(default=None)
    op: str = field(default="")  # "EQUALS", "LESS_THAN", ...
    right: Optional[AstNode] = field(default=None)
    # Note: could be chained comparisons (a < b < c) but for simplicity, we keep it binary


# ---------- Calls ----------
@dataclass
class CallExpr(AstNode):
    callee: Optional[AstNode] = field(default=None)  # Identifier, but could be more complex (e.g., obj.method)
    args: List[AstNode] = field(default_factory=list)  # positional arguments


# ---------- Collections ----------
@dataclass
class TupleExpr(AstNode):
    """
    Represents a tuple literal, e.g. (1, 2, 3)
    Empty tuple: ()
    """

    elements: List[AstNode] = field(default_factory=list)


@dataclass
class ListExpr(AstNode):
    """
    Represents a list literal, e.g. [1, 2, 3]
    """

    elements: List[AstNode] = field(default_factory=list)

@dataclass
class SetExpr(AstNode):
    """
    Represents a set literal, e.g. {1, 2, 3}
    """
    elements: List[AstNode] = field(default_factory=list)

@dataclass
class DictExpr(AstNode):
    """
    Represents a dictionary literal, e.g. {"a": 1, "b": 2}
    Each pair is (key, value)
    """
    pairs: List[Tuple[AstNode, AstNode]] = field(default_factory=list)
