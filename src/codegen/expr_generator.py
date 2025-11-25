"""
ExprGenerator: Generates C++ code for expressions and literals.

Handles operators, literals, function calls, data structures, and method calls.
Converts Python expressions to DynamicType-based C++ code.
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
        self.data_structure_generator = None

    def _create_dynamic_vector(self, elements: list) -> str:
        """Helper method to create DynamicType vector code with consistent formatting."""
        if len(elements) <= 3:
            elements_str = ", ".join(elements)
            return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"
        else:
            elements_str = ",\n    ".join(elements)
            return f"DynamicType(std::vector<DynamicType>{{\n    {elements_str}\n}})"

    def visit(self, node: AstNode) -> str:
        m = getattr(self, f"visit_{type(node).__name__}", None)
        if not m or not callable(m):
            raise NotImplementedError(
                f"ExprGenerator does not support nodes of type {type(node).__name__}"
            )
        return m(node)

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
            f"LiteralExpr with value of type: {type(v).__name__} is not supported"
        )

    def visit_Identifier(self, node: Identifier) -> str:
        name = node.name
        if name == "__name__":
            return 'DynamicType(std::string("__main__"))'
        return name

    def visit_UnaryExpr(self, node: UnaryExpr) -> str:
        rhs = self.visit(node.operand)
        if node.op in ("-", "MINUS"):
            return f"(DynamicType(0) - ({rhs}))"
        if node.op in ("not", "!", "NOT"):
            return f"(!({rhs}))"
        raise NotImplementedError(f"Unary op '{node.op}' is not supported")

    def visit_BinaryExpr(self, node: BinaryExpr) -> str:
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        op = node.op

        if op == "**":
            return f"DynamicType(pow({lhs}.toDouble(), {rhs}.toDouble()))"

        if op == "//":
            return f"({lhs}).floor_div({rhs})"

        mapped = _BIN_OP_CPP.get(op)
        if not mapped:
            raise NotImplementedError(f"Binary Op '{op}' is not supported")

        if op in ("and", "or"):
            return f"DynamicType(({lhs}).toBool() {mapped} ({rhs}).toBool())"

        return f"({lhs}) {mapped} ({rhs})"

    def visit_ComparisonExpr(self, node) -> str:
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        op = node.op

        if op == "in":
            return f"DynamicType(({rhs}).contains({lhs}))"

        mapped = _BIN_OP_CPP.get(op)
        if not mapped:
            raise NotImplementedError(f"Comparison Op '{op}' is not supported")
        return f"DynamicType(({lhs}) {mapped} ({rhs}))"

    def visit_CallExpr(self, node: CallExpr) -> str:
        if isinstance(node.callee, Identifier):
            callee = node.callee.name
        elif isinstance(node.callee, Attribute):
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
            "set": "::set",
        }

        args = [self.visit(a) for a in node.args]

        if callee in builtin_mapping:
            cpp_name = builtin_mapping[callee]
            return f"{cpp_name}({', '.join(args)})"
        return f"_fn_{callee}({', '.join(args)})"

    def visit_ListExpr(self, node) -> str:
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        elements = [self.visit(e) for e in node.elements]
        return self._create_dynamic_vector(elements)

    def visit_DictExpr(self, node) -> str:
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        pairs = []
        for k, v in node.pairs:
            key_code = self.visit(k)
            val_code = self.visit(v)
            pairs.append(f"{{({key_code}).toString(), {val_code}}}")
        pairs_str = ", ".join(pairs)
        return f"DynamicType(std::map<std::string, DynamicType>{{{pairs_str}}})"

    def visit_TupleExpr(self, node) -> str:
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        elements = [self.visit(e) for e in node.elements]
        return self._create_dynamic_vector(elements)

    def visit_SetExpr(self, node) -> str:
        if self.data_structure_generator:
            return self.data_structure_generator.visit(node)
        elements = [self.visit(e) for e in node.elements]
        elements_str = ", ".join(elements)
        return f"DynamicType(std::unordered_set<DynamicType>{{{elements_str}}})"

    def visit_Subscript(self, node) -> str:
        obj_code = self.visit(node.value)

        if isinstance(node.index, TupleExpr):
            elements = node.index.elements

            def slice_param(elem):
                if elem is None:
                    return "DynamicType()"
                return self.visit(elem)

            if len(elements) == 3:
                start = slice_param(elements[0])
                end = slice_param(elements[1])
                step = slice_param(elements[2])

                if elements[0] is None and elements[1] is None:
                    if elements[2] is None:
                        return f"({obj_code})"
                    else:
                        return f"({obj_code}).sublist(DynamicType(0), len({obj_code}), {step})"
                elif elements[2] is None or (
                    hasattr(elements[2], "value") and elements[2].value == 1
                ):
                    if elements[0] is None:
                        start = "DynamicType(0)"
                    if elements[1] is None:
                        end = f"len({obj_code})"
                    return f"({obj_code}).sublist({start}, {end})"
                else:
                    if elements[0] is None:
                        start = "DynamicType(0)"
                    if elements[1] is None:
                        end = f"len({obj_code})"
                    return f"({obj_code}).sublist({start}, {end}, {step})"
            else:
                raise NotImplementedError(
                    f"Invalid slice tuple length: {len(elements)}"
                )

        index_code = self.visit(node.index)
        return f"({obj_code})[{index_code}]"

    def visit_Attribute(self, node: Attribute) -> str:
        obj_code = self.visit(node.value)
        return f"({obj_code}).{node.attr}"

    def _handle_method_call(self, callee: Attribute, args) -> str:
        obj_code = self.visit(callee.value)
        method_name = callee.attr
        args_code = [self.visit(a) for a in args]

        data_structure_methods = {
            "append": {"params": 1, "cpp_method": "append"},
            "pop": {
                "params": -1,
                "cpp_method": "removeAt",
                "default_args": ["DynamicType(-1)"],
            },
            "remove": {
                "params": 1,
                "cpp_method": "remove",
            },
            "get": {"params": 1, "cpp_method": "get"},
            "add": {"params": 1, "cpp_method": "add"},
            "discard": {
                "params": 1,
                "cpp_method": "remove",
            },
        }

        if method_name in data_structure_methods:
            method_info = data_structure_methods[method_name]
            cpp_method = method_info["cpp_method"]

            if method_name == "pop":
                if len(args) == 0:
                    return f"({obj_code}).removeAt(DynamicType(-1))"
                return f"({obj_code}).removeKey({args_code[0]})"
            if method_name in ["sublist", "slice"]:
                if len(args_code) == 2:
                    return f"({obj_code}).sublist({args_code[0]}, {args_code[1]})"

            args_str = ", ".join(args_code)
            return f"({obj_code}).{cpp_method}({args_str})"

        if method_name == "keys":
            return f"({obj_code}).keys()"
        if method_name == "values":
            return f"({obj_code}).values()"
        if method_name == "items":
            return f"({obj_code}).items()"

        args_str = ", ".join(args_code)
        return f"({obj_code}).{method_name}({args_str})"
