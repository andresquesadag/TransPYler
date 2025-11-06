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
        # Track declared variables to emit declarations only once
        self.declared_vars = set()

    # NOTE (Persona 3 provisional): This module implements the Persona 3
    # responsibilities (control-flow and data-structure code generation).
    # It is intentionally lightweight and provisional — meant to be used
    # together with the project's ExpressionGenerator (Persona 2) and the
    # runtime DynamicValue implementation (Persona 1). Keep interfaces
    # minimal and avoid complex C++ idioms so generated code remains
    # readable and easy to debug during the project development.
        
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

        # Support nodes coming from src/core/ast dataclasses as well as
        # loosely-structured MockNode used by tests. Prefer explicit node
        # type attributes when present (node_type), otherwise fall back to
        # class name and dataclass type names like 'If', 'Assign', etc.
        node_name = getattr(node, 'node_type', None)
        if node_name is None:
            # dataclasses from core.ast may expose their class name directly
            node_name = node.__class__.__name__

        method_name = f'visit_{node_name}'
        visitor = getattr(self, method_name, None)
        if visitor:
            return visitor(node)
        # Fallback: try generic_visit which raises a helpful error
        return self.generic_visit(node)
    
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

        # Support core AST If (with .cond and Block.body) and older MockNode
        cond_node = getattr(node, 'cond', None) or getattr(node, 'test', None) or getattr(node, 'condition', None)
        if cond_node is None:
            raise AttributeError(f"If node missing condition attribute. Actual attributes: {dir(node)}")

        condition = self.visit_expression(cond_node)
        cond_code = self._format_condition(condition)
        self.emit(f"if ({cond_code}) {{")
        self.indent()
        # Body may be a Block (with .statements) or a plain list
        body = getattr(node, 'body', None) or getattr(node, 'body', [])
        stmts = getattr(body, 'statements', body)
        for stmt in stmts:
            self.visit(stmt)
        self.dedent()
        self.emit("}")

        # Handle elifs (core AST uses .elifs as list of (cond, block))
        elifs = getattr(node, 'elifs', [])
        for econd, eblock in elifs:
            econd_code = self._format_condition(self.visit_expression(econd))
            self.emit(f"else if ({econd_code}) {{")
            self.indent()
            estmts = getattr(eblock, 'statements', eblock)
            for stmt in estmts:
                self.visit(stmt)
            self.dedent()
            self.emit("}")

        # orelse may be a Block or list
        orelse = getattr(node, 'orelse', None)
        if orelse:
            self.emit("else {")
            self.indent()
            orelse_stmts = getattr(orelse, 'statements', orelse)
            for stmt in orelse_stmts:
                self.visit(stmt)
            self.dedent()
            self.emit("}")
    
    def visit_Assign(self, node) -> str:
        """Generate assignment statements. Handles single-target assigns."""
        # Support core AST Assign: node.target (Identifier) or dataclass Assign.target
        target = getattr(node, 'target', None) or (getattr(node, 'targets', [None])[0] if hasattr(node, 'targets') else None)
        if target is None:
            raise NotImplementedError("Assignment target not found")

        # Extract name from Identifier or other name-like nodes
        if hasattr(target, 'name'):
            var_name = target.name
        elif hasattr(target, 'id'):
            var_name = target.id
        elif hasattr(target, 'arg'):
            var_name = target.arg
        else:
            raise NotImplementedError("Only simple name assignment supported")

        expr = self.visit_expression(getattr(node, 'value', node.value if hasattr(node, 'value') else None))
        if var_name not in self.declared_vars:
            self.declared_vars.add(var_name)
            self.emit(f"DynamicValue {var_name} = {expr};")
        else:
            self.emit(f"{var_name} = {expr};")
        return ""

    def visit_Expr(self, node) -> str:
        """Expression statement (e.g., a call like print(...))"""
        expr = self.visit_expression(node.value)
        # Emit as statement
        self.emit(f"{expr};")
        return ""

    def visit_ExprStmt(self, node) -> str:
        """Support core AST ExprStmt which wraps an expression as a statement."""
        expr = self.visit_expression(getattr(node, 'value', None))
        self.emit(f"{expr};")
        return ""

    def visit_FunctionDef(self, node) -> str:
        """Generate a simple function definition. Parameters are DynamicValue.

        The function returns DynamicValue. Body is emitted as-is.
        """
        name = getattr(node, 'name', None)
        if name is None:
            raise NotImplementedError("Unnamed function")

        # Extract parameters. Support core AST FunctionDef.params (list of names)
        # as well as older Python-ast-like shapes.
        params = []
        if hasattr(node, 'params') and isinstance(node.params, (list, tuple)):
            # params may be simple strings in core AST or Identifier nodes
            params = []
            for p in node.params:
                if isinstance(p, str):
                    params.append(p)
                else:
                    pname = getattr(p, 'name', None) or getattr(p, 'id', None) or getattr(p, 'arg', None)
                    if not pname:
                        raise NotImplementedError("Unsupported parameter node in FunctionDef.params")
                    params.append(pname)
        else:
            args_node = getattr(node, 'args', None)
            if args_node is not None:
                args_list = getattr(args_node, 'args', [])
                for a in args_list:
                    # support MockNode with .arg or simple nodes with .id/.name
                    pname = getattr(a, 'arg', None) or getattr(a, 'id', None) or getattr(a, 'name', None)
                    if not pname:
                        raise NotImplementedError("Unsupported argument node")
                    params.append(pname)

        params_decl = ', '.join([f"DynamicValue {p}" for p in params])

        # Emit function header
        self.emit(f"DynamicValue {name}({params_decl}) {{")
        self.indent()

        # Track declared vars locally
        old_declared = self.declared_vars
        self.declared_vars = set(params)

        # Emit body (body may be a Block with .statements or a plain list)
        body = getattr(node, 'body', []) or []
        stmts = getattr(body, 'statements', body)
        for stmt in stmts:
            self.visit(stmt)

        # Ensure function returns something
        self.emit("return DynamicValue();")

        # Restore declared vars
        self.declared_vars = old_declared
        self.dedent()
        self.emit("}")
        return ""
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
        cond_code = self._format_condition(condition)
        self.emit(f"while ({cond_code}) {{")
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
        target = getattr(node, 'target', None)
        var_name = self._get_target_name(target)

        # Get iterable expression (core AST uses 'iterable')
        iterable = getattr(node, 'iterable', None) or getattr(node, 'iter', None)

        # Check if iterating over range() - optimize this
        if self._is_range_call(iterable):
            self._generate_range_for(var_name, iterable, getattr(node, 'body', None) or [], getattr(node, 'orelse', None) or [])
        else:
            # General case: iterate over iterable
            self._generate_iterable_for(var_name, iterable, getattr(node, 'body', None) or [], getattr(node, 'orelse', None) or [])
        
        return ""
    
    def _get_target_name(self, target) -> str:
        """Extract variable name from for loop target"""
        if hasattr(target, 'id'):
            name = target.id
        elif hasattr(target, 'name'):
            name = target.name
        else:
            name = f"_loop_var_{id(target)}"
        return self._sanitize_name(name)

    def _sanitize_name(self, name: str) -> str:
        """Return a C++-safe identifier for the given name.

        Simple heuristic: if name is a C++ keyword (or 'new'), append an underscore.
        Also replace invalid characters with '_' to avoid syntax errors.
        """
        if not isinstance(name, str):
            name = str(name)
        keywords = {
            'alignas','alignof','and','and_eq','asm','auto','bitand','bitor','bool','break',
            'case','catch','char','char16_t','char32_t','class','compl','const','constexpr',
            'const_cast','continue','decltype','default','delete','do','double','dynamic_cast',
            'else','enum','explicit','export','extern','false','float','for','friend','goto',
            'if','inline','int','long','mutable','namespace','new','noexcept','not','not_eq',
            'nullptr','operator','or','or_eq','private','protected','public','register',
            'reinterpret_cast','return','short','signed','sizeof','static','static_assert',
            'static_cast','struct','switch','template','this','thread_local','throw','true',
            'try','typedef','typeid','typename','union','unsigned','using','virtual','void',
            'volatile','wchar_t','while','xor','xor_eq'
        }
        safe = ''.join([c if (c.isalnum() or c == '_') else '_' for c in name])
        if safe in keywords or safe == 'new':
            safe = safe + '_'
        # Avoid names that start with a digit
        if safe and safe[0].isdigit():
            safe = '_' + safe
        return safe
    
    def _is_range_call(self, node) -> bool:
        """Check if node is a range() function call"""
        # Avoid relying on __class__.__name__ because test MockNode mutates
        # the class name at runtime. Instead detect a call by attributes.
        if node is None:
            return False
        # core AST CallExpr: node.callee is Identifier with .name
        if hasattr(node, 'callee') and hasattr(node, 'args'):
            callee = node.callee
            if hasattr(callee, 'name') and callee.name == 'range':
                return True
            if hasattr(callee, 'id') and callee.id == 'range':
                return True
        # Python-ast-like nodes: node.func.id
        if hasattr(node, 'func') and hasattr(node, 'args') and hasattr(node.func, 'id') and node.func.id == 'range':
            return True
        return False
    
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
    
    def _format_condition(self, condition: str) -> str:
        """
        Format a condition expression string for use in an if/while header.

        The expression generator may return either a DynamicValue-wrapped
        expression (e.g. "DynamicValue(...)"), or a raw boolean expression
        (e.g. "(a == b)" or "(x < 3)"). This helper chooses whether to
        append ".toBool()" or leave the expression as-is.
        """
        s = condition.strip()
        # If the expression already performs a boolean conversion, keep it
        if ".toBool()" in s:
            return f"({s})"
        # If it's explicitly a DynamicValue, call .toBool()
        if s.startswith("DynamicValue("):
            return f"({s}).toBool()"
        # If it looks like a comparison or boolean expression, use as-is
        for token in ("==", "!=", "<=", ">=", "<", ">", "&&", "||", "!"):
            if token in s:
                return f"({s})"
        # Default: assume DynamicValue and call .toBool()
        return f"({s}).toBool()"
    
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
