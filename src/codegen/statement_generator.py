
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

	def __init__(self, target: str = "python"):
		"""
		Initializes the StatementVisitor for a specific target language.
		Args:
			target (str): 'python' or 'cpp'
		"""
		self.target = target
		self.indent_level = 0
		self.indent_str = "    "

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
		method_name = f"visit_{node.__class__.__name__}_{self.target}"
		visitor = getattr(self, method_name, None)
		if visitor:
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
		return f"// TODO: {node.__class__.__name__}"

	# --- Python ---
	def visit_Block_python(self, node):
		"""
		Generates Python code for a block of statements.
		Args:
			node (Block): AST node for a block.
		Returns:
			str: Python code for the block.
		"""
		code = []
		self.indent_level += 1
		for stmt in node.statements:
			code.append(self.indent() + self.visit(stmt))
		self.indent_level -= 1
		return "\n".join(code)

	def visit_If_python(self, node):
		"""
		Generates Python code for an if statement.
		Args:
			node (If): AST node for an if statement.
		Returns:
			str: Python code for the if statement.
		"""
		code = []
		code.append(f"{self.indent()}if {self.visit(node.cond)}:")
		code.append(self.visit(node.body))
		for cond, block in node.elifs:
			code.append(f"{self.indent()}elif {self.visit(cond)}:")
			code.append(self.visit(block))
		if node.orelse:
			code.append(f"{self.indent()}else:")
			code.append(self.visit(node.orelse))
		return "\n".join(code)

	def visit_While_python(self, node):
		"""
		Generates Python code for a while loop.
		Args:
			node (While): AST node for a while loop.
		Returns:
			str: Python code for the while loop.
		"""
		code = [f"{self.indent()}while {self.visit(node.cond)}:"]
		code.append(self.visit(node.body))
		return "\n".join(code)

	def visit_For_python(self, node):
		"""
		Generates Python code for a for loop.
		Args:
			node (For): AST node for a for loop.
		Returns:
			str: Python code for the for loop.
		"""
		code = [f"{self.indent()}for {self.visit(node.target)} in {self.visit(node.iterable)}:"]
		code.append(self.visit(node.body))
		return "\n".join(code)

	def visit_Break_python(self, node):
		"""
		Generates Python code for a break statement.
		Args:
			node (Break): AST node for a break statement.
		Returns:
			str: Python code for break.
		"""
		return f"break"

	def visit_Continue_python(self, node):
		"""
		Generates Python code for a continue statement.
		Args:
			node (Continue): AST node for a continue statement.
		Returns:
			str: Python code for continue.
		"""
		return f"continue"

	def visit_Pass_python(self, node):
		"""
		Generates Python code for a pass statement.
		Args:
			node (Pass): AST node for a pass statement.
		Returns:
			str: Python code for pass.
		"""
		return f"pass"

	def visit_ListExpr_python(self, node):
		"""
		Generates Python code for a list expression.
		Args:
			node (ListExpr): AST node for a list.
		Returns:
			str: Python code for the list.
		"""
		elements = ", ".join(self.visit(e) for e in node.elements)
		return f"[{elements}]"

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
			code.append(self.indent() + self.visit(stmt))
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
		code.append(f"{self.indent()}if ({self.visit(node.cond)})")
		code.append(self.visit(node.body))
		for cond, block in node.elifs:
			code.append(f"{self.indent()}else if ({self.visit(cond)})")
			code.append(self.visit(block))
		if node.orelse:
			code.append(f"{self.indent()}else")
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
		code = [f"{self.indent()}while ({self.visit(node.cond)})"]
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
		# Helper: deduce element type
		iterable_code = self.visit(node.iterable)
		elem_type = self._deduce_cpp_type(node.iterable)
		code = [f"{self.indent()}for ({elem_type} {self.visit(node.target)} : {iterable_code})"]
		code.append(self.visit(node.body))
		return "\n".join(code)

	def visit_Break_cpp(self, node):
		"""
		Generates C++ code for a break statement.
		Args:
			node (Break): AST node for a break statement.
		Returns:
			str: C++ code for break.
		"""
		return f"break;"

	def visit_Continue_cpp(self, node):
		"""
		Generates C++ code for a continue statement.
		Args:
			node (Continue): AST node for a continue statement.
		Returns:
			str: C++ code for continue.
		"""
		return f"continue;"

	def visit_Pass_cpp(self, node):
		"""
		Generates C++ code for a pass statement (as a comment).
		Args:
			node (Pass): AST node for a pass statement.
		Returns:
			str: C++ code for pass (comment).
		"""
		return f"/* pass */"

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
		if hasattr(node, 'elements') and node.elements:
			first = node.elements[0]
			if hasattr(first, 'value'):
				if isinstance(first.value, int):
					return 'int'
				elif isinstance(first.value, float):
					return 'double'
				elif isinstance(first.value, str):
					return 'string'
			return 'auto'
		return 'auto'

