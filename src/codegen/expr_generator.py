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
    TupleExpr,
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
    return (
        s.replace("\\", r"\\")
        .replace('"', r"\"")
        .replace("\n", r"\n")
        .replace("\r", r"\r")
        .replace("\t", r"\t")
    )


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
        # TODO(any): m is not callable
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
        # Handle special Python variables
        if name == "__name__":
            return 'DynamicType(std::string("__main__"))'
        # Note: We're relaxing scope checking as loop variables and function parameters
        # are handled specially and may not be in the main scope when checked
        return name

    # ---------- Unary Expressions  ----------
    def visit_UnaryExpr(self, node: UnaryExpr) -> str:
        rhs = self.visit(node.operand)
        if node.op in ("-", "MINUS"):
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

        if op == "//":
            return f"({lhs}).floor_div({rhs})"

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
        """Handle comparison expressions (==, !=, <, <=, >, >=, in)."""
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        op = node.op

        if op == "in":
            return f"DynamicType(({rhs}).contains({lhs}))"

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
            # Handle method calls like list.append(item), dict.get(key), etc.
            return self._handle_method_call(node.callee, node.args)
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
            "set": "::set",  # Use global namespace to avoid ambiguity with std::set
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
        elements_str = ", ".join(elements)
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
        pairs_str = ", ".join(pairs)
        return f"DynamicType(std::map<std::string, DynamicType>{{{pairs_str}}})"

    def visit_TupleExpr(self, node) -> str:
        """Delegate tuple expressions to DataStructureGenerator."""
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        # Fallback implementation (represent as vector)
        elements = [self.visit(e) for e in node.elements]
        elements_str = ", ".join(elements)
        return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"

    def visit_SetExpr(self, node) -> str:
        """Delegate set expressions to DataStructureGenerator."""
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        # Fallback implementation (use proper set)
        elements = [self.visit(e) for e in node.elements]
        elements_str = ", ".join(elements)
        return f"DynamicType(std::unordered_set<DynamicType>{{{elements_str}}})"

    # ---------- Subscript expressions (indexing and slicing) ----------
    def visit_Subscript(self, node) -> str:
        """
        Handle subscript operations like a[i] or dict[key] or a[start:end:step].
        """
        obj_code = self.visit(node.value)

        if isinstance(node.index, TupleExpr):
            # Slicing: a[start:end:step]
            elements = node.index.elements

            # Helper to convert None/expr to C++ code
            def slice_param(elem):
                if elem is None:
                    return "DynamicType()"  # None in slicing
                return self.visit(elem)

            if len(elements) == 3:
                # Full slice: [start:end:step]
                start = slice_param(elements[0])
                end = slice_param(elements[1])
                step = slice_param(elements[2])

                # Detect common patterns to optimize
                if elements[0] is None and elements[1] is None:
                    # [::step] or [::]
                    if elements[2] is None:
                        # [::] - full copy, just return object
                        return f"({obj_code})"
                    else:
                        # [::step] - need to implement with step from 0 to len
                        return f"({obj_code}).sublist(DynamicType(0), len({obj_code}), {step})"
                elif elements[2] is None or (
                    hasattr(elements[2], "value") and elements[2].value == 1
                ):
                    # [start:end] or [start:end:1] - no step
                    # Need to handle None for start/end
                    if elements[0] is None:
                        start = "DynamicType(0)"
                    if elements[1] is None:
                        end = f"len({obj_code})"
                    return f"({obj_code}).sublist({start}, {end})"
                else:
                    # [start:end:step] - full 3-argument form
                    if elements[0] is None:
                        start = "DynamicType(0)"
                    if elements[1] is None:
                        end = f"len({obj_code})"
                    return f"({obj_code}).sublist({start}, {end}, {step})"
            else:
                # ! Maybe unreachable with proper parser, but can be handled
                raise NotImplementedError(
                    f"Invalid slice tuple length: {len(elements)}"
                )

        # Regular indexing: a[i]
        index_code = self.visit(node.index)
        # Use DynamicType operator[] which automatically handles conversion
        # from DynamicType to appropriate index type (size_t for numbers, string for strings)
        return f"({obj_code})[{index_code}]"

    # ---------- Attribute access and method calls ----------
    def visit_Attribute(self, node: Attribute) -> str:
        """Handle attribute access like obj.attr."""
        obj_code = self.visit(node.value)
        # For simple attribute access (not method calls)
        # This might be used for accessing properties - not commonly used in our transpiler
        return f"({obj_code}).{node.attr}"

    def _handle_method_call(self, callee: Attribute, args) -> str:
        """Handle method calls like obj.method(args)."""
        obj_code = self.visit(callee.value)
        method_name = callee.attr
        args_code = [self.visit(a) for a in args]

        # Map Python data structure methods to DynamicType C++ methods
        # TODO(any): pop key is duplicated, need to differentiate between list.pop() and dict.pop(key) maybe?
        data_structure_methods = {
            # List methods
            "append": {"params": 1, "cpp_method": "append"},
            "pop": {
                "params": 0,
                "cpp_method": "removeAt",
                "default_args": ["DynamicType(-1)"],
            },  # pop() -> removeAt(-1)
            "remove": {"params": 1, "cpp_method": "remove"},  # For sets
            # Dict methods
            "get": {"params": 1, "cpp_method": "get"},
            "pop": {
                "params": 1,
                "cpp_method": "removeKey",
            },  # dict.pop(key) -> removeKey(key)
            # Set methods
            "add": {"params": 1, "cpp_method": "add"},
            "discard": {
                "params": 1,
                "cpp_method": "remove",
            },  # set.discard -> remove (but should not throw)
            "remove": {
                "params": 1,
                "cpp_method": "remove",
            },  # set.remove -> remove (throws if not found)
        }

        if method_name in data_structure_methods:
            method_info = data_structure_methods[method_name]
            cpp_method = method_info["cpp_method"]

            # Handle special cases
            if method_name == "pop" and len(args) == 0:
                # list.pop() without args -> removeAt(-1)
                return f"({obj_code}).{cpp_method}(DynamicType(-1))"
            elif method_name in ["sublist", "slice"]:
                # Handle slicing - expecting 2 args (start, end)
                if len(args_code) == 2:
                    return f"({obj_code}).sublist({args_code[0]}, {args_code[1]})"

            # Standard method call
            args_str = ", ".join(args_code)
            return f"({obj_code}).{cpp_method}({args_str})"

        # Special builtin methods that don't map directly to DynamicType methods
        if method_name == "keys":
            # For dict.keys() - would need implementation
            raise NotImplementedError("dict.keys() method not yet supported")
        elif method_name == "values":
            # For dict.values() - would need implementation
            raise NotImplementedError("dict.values() method not yet supported")
        elif method_name == "items":
            # For dict.items() - would need implementation
            raise NotImplementedError("dict.items() method not yet supported")

        # Fallback for unknown methods
        args_str = ", ".join(args_code)
        return f"({obj_code}).{method_name}({args_str})"
