# src/core/__init__.py
"""Core public API: re-export AST nodes + helpers (carpeta submodule 'ast/')."""

# --- AST base & module ---
from .ast.ast_base import AstNode, Module

# --- Definitions / names ---
from .ast.ast_definitions import FunctionDef, ClassDef, Attribute, Subscript

# --- Expressions ---
from .ast.ast_expressions import (
    LiteralExpr, Identifier, UnaryExpr, BinaryExpr, CallExpr, ListExpr, TupleExpr
)

# --- Statements / control flow ---
from .ast.ast_statements import (
    Block, ExprStmt, Assign, Return, If, While, For, Break, Continue, Pass
)

# --- Helpers existentes ---
from .symbol_table import *
from .utils import *

__all__ = [
    "AstNode", "Module",
    "FunctionDef", "ClassDef", "Attribute", "Subscript",
    "LiteralExpr", "Identifier", "UnaryExpr", "BinaryExpr", "CallExpr", "ListExpr", "TupleExpr",
    "Block", "ExprStmt", "Assign", "Return", "If", "While", "For", "Break", "Continue", "Pass",
]

