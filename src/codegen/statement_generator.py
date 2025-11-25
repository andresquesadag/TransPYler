"""
StatementVisitor: Generates C++ code for control flow statements.

Handles if/while/for loops, break/continue/pass, bl    def visit_Break_cpp(self, node):
        return "break;"

    def visit_Continue_cpp(self, node):
        return "continue;" delegation.
"""




class StatementVisitor:
    """Generates C++ code for control flow statements."""

    def __init__(self, expr_generator=None, scope_manager=None, basic_stmt_generator=None):
        self.target = "cpp"
        self.indent_level = 0
        self.indent_str = "    "
        self.expr_generator = expr_generator
        self.scope_manager = scope_manager
        self.basic_stmt_generator = basic_stmt_generator
        self._iter_counter = 0

    def indent(self) -> str:
        return self.indent_str * self.indent_level

    def visit(self, node) -> str:
        method_name = f"visit_{node.__class__.__name__}_cpp"
        visitor = getattr(self, method_name, None)
        if visitor and callable(visitor):
            return visitor(node)
        return self.generic_visit(node)

    def generic_visit(self, node) -> str:
        if node.__class__.__name__ in ["ExprStmt", "Assign", "Return"]:
            raise NotImplementedError(
                f"BasicStatementGenerator should handle {node.__class__.__name__}"
            )
        raise NotImplementedError(
            f"StatementVisitor does not support node type {node.__class__.__name__}"
        )

    # --- C++ Methods ---
    def visit_Block_cpp(self, node):
        code = []
        code.append("{")
        self.indent_level += 1
        for stmt in node.statements:
            stmt_code = self.visit(stmt)
            if stmt_code.strip():
                if not stmt_code.strip().endswith((";", "}")):
                    stmt_code += ";"
                code.append(self.indent() + stmt_code)
        self.indent_level -= 1
        code.append(self.indent() + "}")
        return "\n".join(code)

    def visit_If_cpp(self, node):
        code = []
        cond_code = (
            self.expr_generator.visit(node.cond)
            if hasattr(self, "expr_generator")
            else str(node.cond)
        )
        if cond_code.startswith("DynamicType("):
            code.append(f"if ({cond_code}.toBool())")
        else:
            code.append(f"if (DynamicType({cond_code}).toBool())")

        body_code = self.visit(node.body)
        code.append(body_code)

        for elif_cond, elif_body in getattr(node, "elifs", []):
            elif_cond_code = (
                self.expr_generator.visit(elif_cond)
                if hasattr(self, "expr_generator")
                else str(elif_cond)
            )
            code.append(f"else if (({elif_cond_code}).toBool())")
            code.append(self.visit(elif_body))

        if hasattr(node, "orelse") and node.orelse:
            code.append("else")
            code.append(self.visit(node.orelse))

        return "\n".join(code)

    def visit_While_cpp(self, node):
        cond_code = (
            self.expr_generator.visit(node.cond)
            if hasattr(self, "expr_generator")
            else str(node.cond)
        )
        if cond_code.startswith("DynamicType("):
            code = [f"while ({cond_code}.toBool())"]
        else:
            code = [f"while (DynamicType({cond_code}).toBool())"]
        code.append(self.visit(node.body))
        return "\n".join(code)

    def visit_For_cpp(self, node):
        iterable_code = (
            self.expr_generator.visit(node.iterable)
            if hasattr(self, "expr_generator")
            else str(node.iterable)
        )
        target_code = (
            self.expr_generator.visit(node.target)
            if hasattr(self, "expr_generator")
            else str(node.target)
        )

        self._iter_counter += 1
        temp_var = f"__iter_temp_{self._iter_counter}"
        elem_type = "auto"
        code = ["{"]
        code.append(f"  auto {temp_var} = ({iterable_code}).getList();")
        code.append(f"  for ({elem_type} {target_code} : {temp_var})")
        body_code = self.visit(node.body)
        for line in body_code.splitlines():
            code.append(f"  {line}")
        code.append("}")
        return "\n".join(code)

    def visit_Break_cpp(self, node):
        return "break;"

    def visit_Continue_cpp(self, node):
        return "continue;"

    def visit_Pass_cpp(self, node):
        return "/* pass */"

    def visit_ExprStmt_cpp(self, node):
        if hasattr(self, "expr_generator") and self.expr_generator:
            code = self.expr_generator.visit(node.value)
            return f"{code};"
        else:
            return f"/* Expression statement: {node.value.__class__.__name__} */;"

    def visit_Assign_cpp(self, node):
        if self.basic_stmt_generator:
            return self.basic_stmt_generator.visit(node)

        if hasattr(node.target, "name"):
            name = node.target.name
            rhs_code = self.expr_generator.visit(node.value)

            if self.scope_manager and not self.scope_manager.exists(name):
                self.scope_manager.declare(name)
                return f"DynamicType {name} = {rhs_code};"
            else:
                return f"{name} = {rhs_code};"
        else:
            raise RuntimeError(
                f"Cannot handle assignment to {type(node.target).__name__} without BasicStatementGenerator"
            )

    def visit_Return_cpp(self, node):
        if node.value is None:
            return "return DynamicType();"
        elif hasattr(self, "expr_generator") and self.expr_generator:
            return f"return {self.expr_generator.visit(node.value)};"
        else:
            return "return DynamicType();"

