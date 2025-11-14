# scope_manager.py
"""
ScopeManager: Manages variable scopes and symbol tables during code generation.
Ensures correct variable resolution and scope nesting for both Python and C++ targets.
Persona 3 responsibility: Implements scope tracking and symbol management helpers.
"""

# Import statements
from collections import deque

class ScopeManager:
	"""
	Handles nested scopes for variables and symbols during code generation.
	Maintains a stack of scopes, each represented as a dictionary.
	Provides methods to enter/exit scopes, add symbols, and resolve names.
	"""

	def __init__(self):
		"""
		Initializes the scope manager with a global scope.
		Uses a deque for efficient stack operations.
		"""
		self.scopes = deque()
		self.enter_scope()  # Start with global scope

	def enter_scope(self):
		"""
		Creates a new scope and pushes it onto the stack.
		Typically called when entering a function, class, or block.
		"""
		self.scopes.append({})

	def exit_scope(self):
		"""
		Removes the topmost scope from the stack.
		Typically called when exiting a function, class, or block.
		"""
		if len(self.scopes) > 1:
			self.scopes.pop()
		else:
			raise RuntimeError("Cannot exit global scope")

	def add_symbol(self, name, value):
		"""
		Adds a symbol to the current (topmost) scope.
		Args:
			name (str): The variable or symbol name.
			value: The associated value or metadata.
		"""
		self.scopes[-1][name] = value

	def resolve_symbol(self, name):
		"""
		Resolves a symbol by searching from innermost to outermost scope.
		Args:
			name (str): The variable or symbol name to resolve.
		Returns:
			The value or metadata associated with the symbol, or None if not found.
		"""
		for scope in reversed(self.scopes):
			if name in scope:
				return scope[name]
		return None

	def current_scope(self):
		"""
		Returns the current (topmost) scope dictionary.
		Useful for debugging or direct access.
		"""
		return self.scopes[-1]

	def all_scopes(self):
		"""
		Returns a list of all scopes from outermost to innermost.
		Useful for inspection or serialization.
		"""
		return list(self.scopes)

 # -------- implementado por persona 2 --------
	def push(self):
		"""Alias de enter_scope()."""
		self.enter_scope()

	def pop(self):
		"""Alias de exit_scope(); no revienta si estás en global."""
		if len(self.scopes) > 1:
			self.scopes.pop()
		else:
			# Fail-soft: no lanzamos para no romper pipelines
			pass

	def reset(self):
		"""Reinicia a un único scope global."""
		self.scopes.clear()
		self.enter_scope()

	def declare(self, name):
		"""Declara un nombre en el scope actual."""
		self.add_symbol(name, True)

	def exists(self, name) -> bool:
		"""¿El nombre existe en algún scope visible?"""
		return self.resolve_symbol(name) is not None