"""
statement_generator.py
----------------------
StatementVisitor: Generates code for control flow statements (if, while, for, break, continue, pass) in Python and C++.

This module provides the StatementVisitor class, which generates code for control flow statements (if, while, for, break, continue, pass) in Python and C++.
Key Features:
- Implements the visitor pattern for AST statement nodes.
- Supports indentation and modular extension for new targets.
- Used by CodeGenerator to handle all control flow code generation.
- Includes helpers for type deduction in C++ for for-each loops and other control flow helpers.
"""

from typing import List, Optional


class StatementVisitor:
    """
    Generates code for control flow statements (if, while, for, break, continue, pass) in Python and C++.
    Implements the visitor pattern for AST nodes, supports indentation, and is modular for new targets.
    Includes helpers for type deduction in C++ for for-each loops and other control flow helpers.
    Persona 3 responsibility: Implements control flow translation and helpers.
    """

    def __init__(self, expr_generator=None, scope_manager=None):
        """
        Initializes the StatementVisitor for C++ code generation.
        Args:
                expr_generator: Optional ExprGenerator instance for expression evaluation
                scope_manager: Optional ScopeManager for variable tracking
        """
        self.target = "cpp"
        self.indent_level = 0
        self.indent_str = "    "
        self.expr_generator = expr_generator
        self.scope_manager = scope_manager
        self._iter_counter = 0  # Counter for generating readable iterator variable names

    def indent(self) -> str:
        """
        Returns the current indentation string based on the indent level.
        Returns:
                str: Indentation string.
        """
        return self.indent_str * self.indent_level

    def visit(self, node) -> str:
        """
        Dispatches node to the appropriate handler based on its type and target language.
        Args:
                node: AST node object
        Returns:
                str: Generated code for the node.
        """
        method_name = f"visit_{node.__class__.__name__}_cpp"
        visitor = getattr(self, method_name, None)
        if visitor and callable(visitor):
                return visitor(node)
        return self.generic_visit(node)

    def generic_visit(self, node) -> str:
        """
        Fallback for unsupported nodes.
        Args:
                node: AST node object.
        Returns:
                str: TODO comment for unsupported node type.
        """
        # For basic statements, delegate back to calling generator
        if node.__class__.__name__ in ['ExprStmt', 'Assign', 'Return']:
            raise NotImplementedError(f"BasicStatementGenerator should handle {node.__class__.__name__}")
        return f"// TODO: {node.__class__.__name__}"



    # --- C++ ---
    def visit_Block_cpp(self, node):
        """
        Generates C++ code for a block of statements.
        Args:
                node (Block): AST node for a block.
        Returns:
                str: C++ code for the block.
        """
        code = []
        code.append("{")
        self.indent_level += 1
        for stmt in node.statements:
            stmt_code = self.visit(stmt)
            if stmt_code.strip():  # Only add non-empty statements
                # Add semicolon if statement doesn't end with } or ;
                if not stmt_code.strip().endswith((';', '}')):
                    stmt_code += ";"
                code.append(self.indent() + stmt_code)
        self.indent_level -= 1
        code.append(self.indent() + "}")
        return "\n".join(code)

    def visit_If_cpp(self, node):
        """
        Generates C++ code for an if statement.
        Args:
                node (If): AST node for an if statement.
        Returns:
                str: C++ code for the if statement.
        """
        code = []
        # Main condition - need to convert to boolean for C++
        cond_code = self.expr_generator.visit(node.cond) if hasattr(self, 'expr_generator') else str(node.cond)
        # If it's already a DynamicType, just call toBool(), otherwise wrap it
        if cond_code.startswith('DynamicType('):
            code.append(f"if ({cond_code}.toBool())")
        else:
            code.append(f"if (DynamicType({cond_code}).toBool())")
        
        # Body
        body_code = self.visit(node.body)
        code.append(body_code)
        
        # Elif clauses
        for elif_cond, elif_body in getattr(node, 'elifs', []):
            elif_cond_code = self.expr_generator.visit(elif_cond) if hasattr(self, 'expr_generator') else str(elif_cond)
            code.append(f"else if (({elif_cond_code}).toBool())")
            code.append(self.visit(elif_body))
        
        # Else clause
        if hasattr(node, 'orelse') and node.orelse:
            code.append("else")
            code.append(self.visit(node.orelse))
        
        return "\n".join(code)

    def visit_While_cpp(self, node):
        """
        Generates C++ code for a while loop.
        Args:
                node (While): AST node for a while loop.
        Returns:
                str: C++ code for the while loop.
        """
        cond_code = self.expr_generator.visit(node.cond) if hasattr(self, 'expr_generator') else str(node.cond)
        # If it's already a DynamicType, just call toBool(), otherwise wrap it
        if cond_code.startswith('DynamicType('):
            code = [f"while ({cond_code}.toBool())"]
        else:
            code = [f"while (DynamicType({cond_code}).toBool())"]
        code.append(self.visit(node.body))
        return "\n".join(code)

    def visit_For_cpp(self, node):
        """
        Generates C++ code for a for-each loop.
        Args:
                node (For): AST node for a for loop.
        Returns:
                str: C++ code for the for-each loop.
        """
        iterable_code = self.expr_generator.visit(node.iterable) if hasattr(self, 'expr_generator') else str(node.iterable)
        target_code = self.expr_generator.visit(node.target) if hasattr(self, 'expr_generator') else str(node.target)
        
        # For DynamicType, we need to avoid dangling references when the iterable
        # is a temporary (e.g., range(...)). We do this by creating a local copy.
        # Use a readable counter-based name instead of UUID
        self._iter_counter += 1
        temp_var = f"__iter_temp_{self._iter_counter}"
        elem_type = "auto"
        code = ["{"]
        code.append(f"  auto {temp_var} = ({iterable_code}).getList();")
        code.append(f"  for ({elem_type} {target_code} : {temp_var})")
        # Indent the body
        body_code = self.visit(node.body)
        for line in body_code.splitlines():
            code.append(f"  {line}")
        code.append("}")
        return "\n".join(code)

    def visit_Break_cpp(self, node):
        """
        Generates C++ code for a break statement.
        Args:
                node (Break): AST node for a break statement.
        Returns:
                str: C++ code for break.
        """
        return "break;"

    def visit_Continue_cpp(self, node):
        """
        Generates C++ code for a continue statement.
        Args:
                node (Continue): AST node for a continue statement.
        Returns:
                str: C++ code for continue.
        """
        return "continue;"

    def visit_Pass_cpp(self, node):
        """
        Generates C++ code for a pass statement (as a comment).
        Args:
                node (Pass): AST node for a pass statement.
        Returns:
                str: C++ code for pass (comment).
        """
        return "/* pass */"

    def visit_ExprStmt_cpp(self, node):
        """
        Generates C++ code for an expression statement.
        Args:
                node (ExprStmt): AST node for an expression statement.
        Returns:
                str: C++ code for the expression statement.
        """
        if hasattr(self, 'expr_generator') and self.expr_generator:
            code = self.expr_generator.visit(node.value)
            return f"{code};"
        else:
            # Fallback if no expr_generator available
            return f"/* Expression statement: {node.value.__class__.__name__} */;"

    def visit_Assign_cpp(self, node):
        """
        Generates C++ code for an assignment statement.
        Args:
                node (Assign): AST node for an assignment.
        Returns:
                str: C++ code for the assignment.
        """
        # This should be handled by BasicStatementGenerator, not here
        # But we provide a basic implementation as fallback
        if hasattr(node.target, 'name') and hasattr(self, 'expr_generator') and self.expr_generator:
            name = node.target.name
            rhs_code = self.expr_generator.visit(node.value)
            
            # Check if variable needs declaration
            if self.scope_manager and not self.scope_manager.exists(name):
                self.scope_manager.declare(name)
                return f"DynamicType {name} = {rhs_code};"
            else:
                return f"{name} = {rhs_code};"
        else:
            return f"/* Assignment statement */;"

    def visit_Return_cpp(self, node):
        """
        Generates C++ code for a return statement.
        Args:
                node (Return): AST node for a return.
        Returns:
                str: C++ code for the return.
        """
        if node.value is None:
            return "return DynamicType();"
        elif hasattr(self, 'expr_generator') and self.expr_generator:
            return f"return {self.expr_generator.visit(node.value)};"
        else:
            return "return DynamicType();"

    def visit_ListExpr_cpp(self, node):
        """
        Generates C++ code for a list expression (std::vector).
        Args:
                node (ListExpr): AST node for a list.
        Returns:
                str: C++ code for the vector.
        """
        elements = ", ".join(self.visit(e) for e in node.elements)
        return f"std::vector<auto>{{{elements}}}"

    def _deduce_cpp_type(self, node):
        """
        Helper to deduce type in C++ for for-each loops and collections.
        Only supports lists for now; can be extended for other types.
        Args:
                node: AST node for the iterable.
        Returns:
                str: Deduced C++ type (int, double, string, auto).
        """
        if hasattr(node, "elements") and node.elements:
            first = node.elements[0]
            if hasattr(first, "value"):
                if isinstance(first.value, int):
                    return "int"
                elif isinstance(first.value, float):
                    return "double"
                elif isinstance(first.value, str):
                    return "string"
            return "auto"
        return "auto"
