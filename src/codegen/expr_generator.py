"""Expression generator for Person 3 (minimal, pragmatic implementation)

Produces C++ expressions (strings) using DynamicValue and runtime helpers.
This is intentionally minimal but covers the common node types required by
control flow generation and the example program.
"""

from typing import Any
from .data_structure_generator import ListOperationsGenerator


class ExpressionGenerator:
    def __init__(self):
        self.list_gen = ListOperationsGenerator(self)

    def visit(self, node) -> str:
        if node is None:
            return "DynamicValue()"

        node_type = getattr(node, 'node_type', node.__class__.__name__)
        method = getattr(self, f'visit_{node_type}', None)
        if method:
            return method(node)
        # Fallback
        return f"/* UnhandledExpr: {node_type} */"

    def visit_Constant(self, node) -> str:
        value = node.value
        if isinstance(value, bool):
            return f"DynamicValue({'true' if value else 'false'})"
        if isinstance(value, int):
            return f"DynamicValue({value})"
        if isinstance(value, float):
            return f"DynamicValue({value})"
        if isinstance(value, str):
            return f'DynamicValue("{value}")'
        if value is None:
            return "DynamicValue()"
        return "DynamicValue()"

    # Name: variable reference
    def visit_Name(self, node) -> str:
        return node.id

    def visit_NameConstant(self, node) -> str:
        if node.value is True:
            return "DynamicValue(true)"
        if node.value is False:
            return "DynamicValue(false)"
        if node.value is None:
            return "DynamicValue()"
        return "DynamicValue()"

    def visit_BinOp(self, node) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.__class__.__name__
        op_map = {
            'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/', 'Mod': '%'
        }
        cpp_op = op_map.get(op, '+')
    # Avoid unnecessary outer parentheses; keep sub-expression grouping
    return f"({left} {cpp_op} {right})"

    def visit_UnaryOp(self, node) -> str:
        operand = self.visit(node.operand)
        op = node.op.__class__.__name__
        if op == 'USub':
            return f"(DynamicValue(0) - ({operand}))"
        if op == 'Not':
            # Return plain boolean expression for logical not
            return f"!({operand}).toBool()"
        return operand

    def visit_Compare(self, node) -> str:
        left = self.visit(node.left)
        op = node.ops[0].__class__.__name__
        right = self.visit(node.comparators[0])
        op_map = {
            'Lt': '<', 'Gt': '>', 'LtE': '<=', 'GtE': '>=', 'Eq': '==', 'NotEq': '!='
        }
        cpp_op = op_map.get(op, '==')
        # Return a plain boolean C++ expression (not wrapped in DynamicValue)
        return f"({left} {cpp_op} {right})"

    def visit_BoolOp(self, node) -> str:
        op = node.op.__class__.__name__
        vals = [self.visit(v) for v in node.values]
        if op == 'And':
            expr = vals[0]
            for v in vals[1:]:
                expr = f"(({expr}).toBool() && ({v}).toBool())"
        else:
            expr = vals[0]
            for v in vals[1:]:
                expr = f"(({expr}).toBool() || ({v}).toBool())"
        # BoolOp returns a plain boolean expression
        return expr

    def visit_Call(self, node) -> str:
        # function name
        func_name = getattr(node.func, 'id', getattr(node.func, 'attr', 'unknown'))
        args = [self.visit(a) for a in getattr(node, 'args', [])]
        args_str = ', '.join(args)
        builtin_map = {
            'print': 'print_func', 'len': 'len_func', 'range': 'range_func',
            'str': 'str_func', 'int': 'int_func', 'float': 'float_func', 'bool': 'bool_func'
        }
        cpp_name = builtin_map.get(func_name, func_name)
        return f"{cpp_name}({args_str})"

    def visit_List(self, node) -> str:
        return self.list_gen.visit_List(node)

    def visit_Subscript(self, node) -> str:
        return self.list_gen.visit_Subscript(node)

    def visit_Tuple(self, node) -> str:
        # Delegate to list generation (tuples are represented as vectors)
        return self.list_gen.visit_Tuple(node)

    def visit_Dict(self, node) -> str:
        # Delegate to data structure generator for dicts
        return self.list_gen.visit_Dict(node)
#TODO(David): Implement expr_generator.py