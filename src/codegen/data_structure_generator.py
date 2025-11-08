"""
DataStructureGenerator
----------------------
This module provides the DataStructureGenerator class, which is responsible for generating code for data structures such as lists, tuples, sets, and dictionaries in both Python and C++.

Key Features:
- Type deduction for C++ STL containers (e.g., std::vector, std::tuple, std::set, std::map).
- Modular visitor pattern for AST nodes representing collections.
- Used by the main CodeGenerator to handle all collection-related code generation.

Usage:
- Instantiate with a target language ('python' or 'cpp').
- Call visit(node) with an AST node representing a collection.
- Returns a string of generated code for the target language.
"""

"""
DataStructureGenerator: Generates code for data structures (lists, tuples, sets, dicts) in Python and C++.

Provides helpers for type deduction and code generation for collections.
Supports both Python and C++ targets, automatically deducing types for C++ STL containers.
"""

from ..core.ast.ast_expressions import ListExpr, TupleExpr, SetExpr, DictExpr



class DataStructureGenerator:
	"""
	Generates code for data structure AST nodes (lists, tuples, sets, dicts).
	Handles both Python and C++ targets, including type deduction for C++ STL containers.
	"""

	def __init__(self, target: str = "python"):
		"""
		Initialize the DataStructureGenerator.
		Args:
			target (str): Target language ('python' or 'cpp').
		"""
		self.target = target

	def visit(self, node) -> str:
		"""
		Dispatch code generation to the appropriate method based on node type and target.
		Args:
			node: AST node representing a data structure.
		Returns:
			str: Generated code for the node.
		"""
		method_name = f"visit_{type(node).__name__}_{self.target}"
		visitor = getattr(self, method_name, None)
		if visitor:
			return visitor(node)
		return self.generic_visit(node)

	def generic_visit(self, node) -> str:
		"""
		Fallback for unsupported nodes.
		Args:
			node: AST node.
		Returns:
			str: TODO comment for unsupported node type.
		"""
		return f"// TODO: {type(node).__name__}"

	# --- Python ---
	def visit_ListExpr_python(self, node: ListExpr) -> str:
		"""
		Generate Python code for a list expression.
		Args:
			node (ListExpr): AST node for a list.
		Returns:
			str: Python list code.
		"""
		elements = ", ".join(self.visit(e) for e in node.elements)
		return f"[{elements}]"

	def visit_TupleExpr_python(self, node: TupleExpr) -> str:
		"""
		Generate Python code for a tuple expression.
		Args:
			node (TupleExpr): AST node for a tuple.
		Returns:
			str: Python tuple code.
		"""
		elements = ", ".join(self.visit(e) for e in node.elements)
		return f"({elements})"

	def visit_SetExpr_python(self, node: SetExpr) -> str:
		"""
		Generate Python code for a set expression.
		Args:
			node (SetExpr): AST node for a set.
		Returns:
			str: Python set code.
		"""
		elements = ", ".join(self.visit(e) for e in node.elements)
		return f"{{{elements}}}"

	def visit_DictExpr_python(self, node: DictExpr) -> str:
		"""
		Generate Python code for a dictionary expression.
		Args:
			node (DictExpr): AST node for a dictionary.
		Returns:
			str: Python dict code.
		"""
		pairs = ", ".join(f"{self.visit(k)}: {self.visit(v)}" for k, v in node.pairs)
		return f"{{{pairs}}}"

	# --- C++ ---
	def visit_ListExpr_cpp(self, node: ListExpr) -> str:
		"""
		Generate C++ code for a list expression (std::vector).
		Args:
			node (ListExpr): AST node for a list.
		Returns:
			str: C++ vector code.
		"""
		elem_type = self._deduce_cpp_vector_type(node)
		elements = ", ".join(self.visit(e) for e in node.elements)
		return f"std::vector<{elem_type}>{{{elements}}}"

	def _deduce_cpp_vector_type(self, node):
		"""
		Deduce the type for std::vector in C++ based on the first element.
		Args:
			node (ListExpr): AST node for a list.
		Returns:
			str: Deduced C++ type.
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

	def visit_TupleExpr_cpp(self, node: TupleExpr) -> str:
		"""
		Generate C++ code for a tuple expression (std::tuple).
		Args:
			node (TupleExpr): AST node for a tuple.
		Returns:
			str: C++ tuple code.
		"""
		types = self._deduce_cpp_tuple_types(node)
		elements = ", ".join(self.visit(e) for e in node.elements)
		return f"std::tuple<{types}>({elements})"

	def _deduce_cpp_tuple_types(self, node):
		"""
		Deduce types for std::tuple in C++ based on elements.
		Args:
			node (TupleExpr): AST node for a tuple.
		Returns:
			str: Comma-separated C++ types.
		"""
		types = []
		for elem in node.elements:
			if hasattr(elem, 'value'):
				if isinstance(elem.value, int):
					types.append('int')
				elif isinstance(elem.value, float):
					types.append('double')
				elif isinstance(elem.value, str):
					types.append('string')
				else:
					types.append('auto')
			else:
				types.append('auto')
		return ', '.join(types)

	def visit_SetExpr_cpp(self, node: SetExpr) -> str:
		"""
		Generate C++ code for a set expression (std::set).
		Args:
			node (SetExpr): AST node for a set.
		Returns:
			str: C++ set code.
		"""
		elem_type = self._deduce_cpp_set_type(node)
		elements = ", ".join(self.visit(e) for e in node.elements)
		return f"std::set<{elem_type}>{{{elements}}}"

	def _deduce_cpp_set_type(self, node):
		"""
		Deduce the type for std::set in C++ based on the first element.
		Args:
			node (SetExpr): AST node for a set.
		Returns:
			str: Deduced C++ type.
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

	def visit_DictExpr_cpp(self, node: DictExpr) -> str:
		"""
		Generate C++ code for a dictionary expression (std::map).
		Args:
			node (DictExpr): AST node for a dictionary.
		Returns:
			str: C++ map code.
		"""
		k_type, v_type = self._deduce_cpp_dict_types(node)
		pairs = ", ".join(f"{{{self.visit(k)}, {self.visit(v)}}}" for k, v in node.pairs)
		return f"std::map<{k_type}, {v_type}>{{{pairs}}}"

	def _deduce_cpp_dict_types(self, node):
		"""
		Deduce key and value types for std::map in C++ based on the first pair.
		Args:
			node (DictExpr): AST node for a dictionary.
		Returns:
			tuple: (key_type, value_type)
		"""
		if hasattr(node, 'pairs') and node.pairs:
			k, v = node.pairs[0]
			k_type = 'auto'
			v_type = 'auto'
			if hasattr(k, 'value'):
				if isinstance(k.value, int):
					k_type = 'int'
				elif isinstance(k.value, float):
					k_type = 'double'
				elif isinstance(k.value, str):
					k_type = 'string'
			if hasattr(v, 'value'):
				if isinstance(v.value, int):
					v_type = 'int'
				elif isinstance(v.value, float):
					v_type = 'double'
				elif isinstance(v.value, str):
					v_type = 'string'
			return k_type, v_type
		return 'auto', 'auto'

