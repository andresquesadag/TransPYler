"""
Code Generator for Control Flow and Data Structures
Part of the Fangless Python to C++ Transpiler

Handles:
- if/elif/else conditionals
- while loops (with while-else)
- for loops (with for-else and range optimization)
- break/continue/pass/return statements
- Nested control structures
- Integration with Person 2's expression generator
"""

from typing import List, Optional, Any
from io import StringIO

class ControlFlowGenerator:
    """
    Generates C++ code for control flow structures from Python AST nodes.
    Uses visitor pattern to traverse AST and emit equivalent C++ code.
    """
    
    def __init__(self, expression_generator=None):
        """
        Initialize control flow generator.
        
        Args:
            expression_generator: Instance of Person 2's ExpressionGenerator
                                 for delegating expression code generation
        """
        self.expression_gen = expression_generator
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces per indent
        self.output = StringIO()
        
        # Loop tracking for break/continue validation and else clause support
        self.in_loop = 0  # Nested loop depth
        self.loop_flag_stack = []  # Stack of completion flags for loop-else
        
    def get_indent(self) -> str:
        """Get current indentation string"""
        return self.indent_str * self.indent_level
    
    def emit(self, code: str, newline: bool = True):
        """
        Emit code with current indentation.
        
        Args:
            code: C++ code string to emit
            newline: Whether to append newline
        """
        self.output.write(self.get_indent() + code)
        if newline:
            self.output.write("\n")
    
    def emit_raw(self, code: str):
        """Emit code without indentation (for same-line continuations)"""
        self.output.write(code)
    
    def get_code(self) -> str:
        """Get all generated C++ code"""
        return self.output.getvalue()
    
    def clear(self):
        """Clear output buffer"""
        self.output = StringIO()
    
    # ==================== VISITOR PATTERN ====================
    
    def visit(self, node) -> str:
        """
        Main visitor dispatcher.
        Routes AST nodes to appropriate visit_* methods.
        
        Args:
            node: AST node to visit
            
        Returns:
            Generated C++ code (may be empty string for statements)
        """
        if node is None:
            return ""

        node_name = getattr(node, 'node_type', node.__class__.__name__)
        method_name = f'visit_{node_name}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """Fallback for unhandled node types"""
        raise NotImplementedError(
            f"Control flow generator has no visit method for {node.__class__.__name__}. "
            f"This node may need to be handled by Person 2's expression generator."
        )
    
    # ==================== IF/ELIF/ELSE ====================
    
    def visit_If(self, node):
        # Debug prints removed; keep function lean. Use unit tests to validate
        # behavior rather than noisy console output.

        # Detecta la condición correctamente
        if hasattr(node, "cond"):
            condition = self.visit_expression(node.cond)
        elif hasattr(node, "test"):
            condition = self.visit_expression(node.test)
        elif hasattr(node, "condition"):
            condition = self.visit_expression(node.condition)
        else:
            raise AttributeError(
                f"If node missing condition attribute ('cond', 'test', or 'condition'). "
                f"Actual attributes: {dir(node)}"
            )

        # Ensure condition is evaluated as a boolean (DynamicValue -> bool)
        self.emit(f"if (({condition}).toBool()) {{")
        self.indent()
        # Visit all statements in the body. Avoid fragile isinstance checks
        # because the test MockNode mutates class names; rely on visitor to
        # handle node-specific logic instead.
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        self.emit("}")

        # Genera el else si existe
        if getattr(node, "orelse", None):
            self.emit("else {")
            self.indent()
            for stmt in node.orelse:
                self.visit(stmt)
            self.dedent()
            self.emit("}")
    # ==================== WHILE LOOPS ====================
    
    def visit_While(self, node) -> str:
        """
        Generate C++ while loop from AST node.
        Handles nodes with condition attribute named 'cond', 'test', or 'condition'.
        Supports while-else by using a completion flag.
        """
        # Detect the correct condition attribute
        condition_node = None
        for attr in ("cond", "test", "condition"):
            if hasattr(node, attr):
                condition_node = getattr(node, attr)
                break

        if condition_node is None:
            raise AttributeError("While node missing condition attribute ('cond', 'test', or 'condition')")

        condition = self.visit_expression(condition_node)

        # Prepare orelse (could be list or Block)
        orelse = getattr(node, "orelse", []) or []

        # Create completion flag for while-else support if needed
        flag_name = None
        if orelse:
            flag_name = f"_while_completed_{id(node)}"
            self.emit(f"bool {flag_name} = true;")
            self.loop_flag_stack.append(flag_name)

        # Generate while loop header
        self.emit(f"while (({condition}).toBool()) {{")
        self.indent_level += 1
        self.in_loop += 1

        # Visit body statements (body may be a Block or a list)
        body = getattr(node, "body", []) or []
        stmts = getattr(body, "statements", body)
        for stmt in stmts:
            self.visit(stmt)

        # Close loop
        self.in_loop -= 1
        self.indent_level -= 1
        self.emit("}")

        # Pop flag from stack if we pushed one
        if orelse:
            # remove the flag we pushed earlier
            self.loop_flag_stack.pop()

        # Generate else clause: runs if loop completed without break
        if orelse:
            self.emit(f"if ({flag_name}) {{")
            self.indent_level += 1
            orelse_stmts = getattr(orelse, "statements", orelse)
            for stmt in orelse_stmts:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")

        return ""

    
    # ==================== FOR LOOPS ====================
    
    def visit_For(self, node) -> str:
        """
        Generate C++ for loop from Python For AST node.
        Optimizes range() calls, supports for-else.
        
        AST Structure:
            For(target=Name, iter=expr, body=[stmt, ...], orelse=[stmt, ...])
        
        Cases:
            1. for x in [1,2,3]:     →  for (auto x : list.toList()) { ... }
            2. for x in range(10):   →  for (int x = 0; x < 10; x++) { ... }
            3. for x in my_list:     →  for (auto x : (my_list).toList()) { ... }
        """
        # Get loop variable name
        var_name = self._get_target_name(node.target)
        
        # Check if iterating over range() - optimize this
        if self._is_range_call(node.iter):
            self._generate_range_for(var_name, node.iter, node.body, node.orelse)
        else:
            # General case: iterate over iterable
            self._generate_iterable_for(var_name, node.iter, node.body, node.orelse)
        
        return ""
    
    def _get_target_name(self, target) -> str:
        """Extract variable name from for loop target"""
        if hasattr(target, 'id'):
            return target.id
        elif hasattr(target, 'name'):
            return target.name
        else:
            return f"_loop_var_{id(target)}"
    
    def _is_range_call(self, node) -> bool:
        """Check if node is a range() function call"""
        # Avoid relying on __class__.__name__ because test MockNode mutates
        # the class name at runtime. Instead detect a call by attributes.
        return (
            hasattr(node, 'func') and hasattr(node, 'args') and
            hasattr(node.func, 'id') and node.func.id == 'range'
        )
    
    def _generate_range_for(self, var_name: str, range_node, body, orelse):
        """
        Generate optimized integer for loop for range() calls.
        Avoids creating vector, directly uses integer loop.
        """
        args = range_node.args
        
        # Parse range arguments: range(stop) or range(start, stop) or range(start, stop, step)
        if len(args) == 1:
            start = "0"
            stop = self.visit_expression(args[0])
            step = "1"
        elif len(args) == 2:
            start = self.visit_expression(args[0])
            stop = self.visit_expression(args[1])
            step = "1"
        elif len(args) == 3:
            start = self.visit_expression(args[0])
            stop = self.visit_expression(args[1])
            step = self.visit_expression(args[2])
        else:
            raise ValueError(f"range() takes 1 to 3 arguments, got {len(args)}")
        
        # Create completion flag for for-else
        flag_name = None
        if orelse:
            flag_name = f"_for_completed_{id(range_node)}"
            self.emit(f"bool {flag_name} = true;")
            self.loop_flag_stack.append(flag_name)
        
        # Generate optimized integer for loop
        self.emit(
            f"for (int {var_name} = ({start}).toInt(); "
            f"{var_name} < ({stop}).toInt(); "
            f"{var_name} += ({step}).toInt()) {{"
        )
        self.indent_level += 1
        self.in_loop += 1
        
        for stmt in body:
            self.visit(stmt)
        
        self.in_loop -= 1
        self.indent_level -= 1
        self.emit("}")
        
        # Pop flag
        if orelse:
            self.loop_flag_stack.pop()
        
        # Generate else clause
        if orelse:
            self.emit(f"if ({flag_name}) {{")
            self.indent_level += 1
            for stmt in orelse:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")
    
    def _generate_iterable_for(self, var_name: str, iter_expr, body, orelse):
        """Generate range-based for loop for general iterables"""
        iterable = self.visit_expression(iter_expr)
        
        # Create completion flag for for-else
        flag_name = None
        if orelse:
            flag_name = f"_for_completed_{id(iter_expr)}"
            self.emit(f"bool {flag_name} = true;")
            self.loop_flag_stack.append(flag_name)
        
        # Generate range-based for loop
        self.emit(f"for (auto {var_name} : ({iterable}).toList()) {{")
        self.indent_level += 1
        self.in_loop += 1
        
        for stmt in body:
            self.visit(stmt)
        
        self.in_loop -= 1
        self.indent_level -= 1
        self.emit("}")
        
        # Pop flag
        if orelse:
            self.loop_flag_stack.pop()
        
        # Generate else clause
        if orelse:
            self.emit(f"if ({flag_name}) {{")
            self.indent_level += 1
            for stmt in orelse:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")
    
    # ==================== FLOW CONTROL STATEMENTS ====================
    
    def visit_Break(self, node) -> str:
        """
        Generate break statement.
        Sets loop completion flag to false for loop-else support.
        
        Validates that break is inside a loop.
        """
        if self.in_loop == 0:
            raise SyntaxError(
                f"'break' outside loop at line {getattr(node, 'line', '?')}"
            )
        
        # Set completion flag to false if we're in a loop with else
        if self.loop_flag_stack:
            current_flag = self.loop_flag_stack[-1]
            self.emit(f"{current_flag} = false;")
        
        self.emit("break;")
        return ""
    
    def visit_Continue(self, node) -> str:
        """
        Generate continue statement.
        Validates that continue is inside a loop.
        """
        if self.in_loop == 0:
            raise SyntaxError(
                f"'continue' outside loop at line {getattr(node, 'line', '?')}"
            )
        
        self.emit("continue;")
        return ""
    
    def visit_Pass(self, node) -> str:
        """
        Generate pass statement (no-op in C++).
        Emits empty statement with comment.
        """
        self.emit(";  // pass")
        return ""
    
    def visit_Return(self, node) -> str:
        """
        Generate return statement.
        
        AST Structure:
            Return(value=expr | None)
        
        Returns DynamicValue for consistency with function signatures.
        """
        if node.value is None:
            self.emit("return DynamicValue();  // return None")
        else:
            expr = self.visit_expression(node.value)
            self.emit(f"return {expr};")
        return ""
    
    # ==================== EXPRESSION DELEGATION ====================
    
    def visit_expression(self, node) -> str:
        """
        Delegate expression generation to Person 2's expression generator.
        
        Args:
            node: Expression AST node
            
        Returns:
            C++ expression code as string
        """
        if self.expression_gen:
            return self.expression_gen.visit(node)
        else:
            # Fallback: try to handle simple cases ourselves
            # This allows Person 3 to work independently for testing
            return self._fallback_expression(node)
    
    def _fallback_expression(self, node) -> str:
        """
        Simple fallback for basic expressions when Person 2's generator unavailable.
        Only for testing purposes - real implementation should use Person 2's code.
        """
        node_type = node.__class__.__name__
        
        if node_type == 'Num' or node_type == 'Constant':
            # Numeric literal
            value = node.value if hasattr(node, 'value') else node.n
            if isinstance(value, int):
                return f"DynamicValue({value})"
            else:
                return f"DynamicValue({value})"
        
        elif node_type == 'Name':
            # Variable reference
            return node.id
        
        elif node_type == 'Str':
            # String literal
            return f'DynamicValue("{node.s}")'
        
        elif node_type == 'BinOp':
            # Binary operation - basic implementation
            left = self._fallback_expression(node.left)
            right = self._fallback_expression(node.right)
            op = node.op.__class__.__name__
            
            op_map = {
                'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/',
                'Mod': '%', 'Pow': '**',
                'Lt': '<', 'Gt': '>', 'LtE': '<=', 'GtE': '>=',
                'Eq': '==', 'NotEq': '!='
            }
            
            cpp_op = op_map.get(op, '+')
            return f"({left} {cpp_op} {right})"
        
        else:
            # Unknown - must be handled by Person 2
            raise NotImplementedError(
                f"Expression type {node_type} must be handled by Person 2's "
                "expression generator. Use real generator for this node."
            )
    
    # ==================== HELPER METHODS ====================
    
    def generate_block(self, statements: List[Any]):
        """
        Generate arbitrary code block with braces.
        Useful for manual code generation.
        """
        self.emit("{")
        self.indent_level += 1
        for stmt in statements:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")
    
    def with_indent(self, func, *args, **kwargs):
        """Execute function with temporarily increased indentation"""
        self.indent_level += 1
        try:
            result = func(*args, **kwargs)
        finally:
            self.indent_level -= 1
        return result
    
    def indent(self):
        """Increase current indentation level by one."""
        self.indent_level += 1

    def dedent(self):
        """Decrease current indentation level by one."""
        if self.indent_level > 0:
            self.indent_level -= 1
