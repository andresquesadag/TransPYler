
"""
function_generator.py
---------------------
FunctionGenerator: Generates code for function definitions and scope management (Persona 2).

This module provides the FunctionGenerator class, which generates code for function definitions, parameters, and return statements in both Python and C++.
Key Features:
- Supports parameter handling, return statements, and extensibility for advanced function features.
- Includes helpers for scope and parameter management.
- Used by CodeGenerator to handle all function-related code generation.
"""

from typing import List
from src.core import (
	AstNode, FunctionDef, Identifier, 
	Assign, ExprStmt, Return, Block, If, While, For
)
from .scope_manager import ScopeManager
from .expr_generator import ExprGenerator
from .basic_statement_generator import BasicStatementGenerator
from .statement_generator import StatementVisitor

class FunctionGenerator:
	"""
	Generates code for function definitions and scope management.
	Handles both Python and C++ targets, including parameter and return statement generation.
	Persona 2 responsibility: Implements function translation and helpers.
	"""

	def __init__(self, scope: ScopeManager):
		"""
		Initializes the FunctionGenerator for a specific target language.
		Args:
			scope (ScopeManager): Scope manager for tracking variable declarations.
		"""
		self.scope = scope
		self.basic_stmt = BasicStatementGenerator(self.scope)
		self.ctrl_stmt = StatementVisitor(target="cpp")
		
	def emit(self, node: FunctionDef) -> str:
		if not isinstance(node, FunctionDef):
			raise TypeError("FunctionGenerator.emit() expects a FunctionDef")

	#  ------- Function Definition -------
		param_names: List[str] = []
		for p in node.params:
			if isinstance(p, Identifier):
				param_names.append(p.name)
			else:
				param_names.append(str(p))
		
		cpp_params = ", ".join(f"DynamicType {n}" for n in param_names)
		header = f"DynamicType _fn_{node.name}({cpp_params}) {{"
		#  ------- Function scope -------
		self.scope.push()
		try:
			for n in param_names:
				if not self.scope.exist(n):
					self.scope.declare(n)
			#  ------- Function Body -------
			body_lines: List[str] = []
			for stmt in node.body:
				body_lines.append(self._emit_stmt(stmt))
			has_top_return = any(isinstance(s, Return) for s in node.body)
			lines = [header] 
			for line in body_lines:
				if line is None:
					continue
				for sub in line.splitlines():
					lines.append("	" + sub)
			if not has_top_return:
				lines.append("	return DynamicType();")
			lines.append("}")
			return "\n".join(lines)
		finally:
			self.scope.pop()

	def _emit_stmt(self, stmt: AstNode) -> str:
		if isinstance(stmt, (Assign, ExprStmt, Return)):
			return self.basic_stmt.emit(stmt)
		if isinstance(stmt, (If, While, For, Block)):
			return self.ctrl_stmt.visit(stmt)
		raise NotImplementedError(f"[FunctionGenerator] Statement type {type(stmt).__name__} not supported")