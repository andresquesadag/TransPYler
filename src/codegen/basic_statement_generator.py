"""
BasicStatementGenerator
-----------------------
This module provides the BasicStatementGenerator class, which generates C++ code for basic 
statements including assignments, expression statements, and return statements.

Key Features:
- Handles simple and augmented assignment statements (x = value, x += value, etc.)
- Generates C++ code with automatic variable declaration on first assignment
- Supports return statements with optional values
- Integrates with ExprGenerator for expression code generation
- Maintains scope information for variable tracking
- Uses DynamicType for dynamic typing in C++

Architecture:
- Uses visitor pattern for different statement types
- Delegates expression generation to ExprGenerator
- Tracks variable declarations via ScopeManager
- Generates C++ code with proper semicolon termination

Restrictions:
- Assignment targets must be simple identifiers (no subscripts or attributes)
- Supports C++ target only (future: Python support)
- Variables are declared as DynamicType on first assignment

Usage:
    from src.codegen.basic_statement_generator import BasicStatementGenerator
    from src.codegen.scope_manager import ScopeManager
    
    scope = ScopeManager()
    gen = BasicStatementGenerator(scope)
    
    Generate code from AST nodes
   
"""

from src.core import AstNode, Assign, ExprStmt, Return, Identifier
from .expr_generator import ExprGenerator
from .scope_manager import ScopeManager


class BasicStatementGenerator:
   
    def __init__(self, scope: ScopeManager):
        """
        Initialize the BasicStatementGenerator.        
        Args:
            scope (ScopeManager): Scope manager for tracking variable declarations.
        """
        self.scope = scope
        self.expr = ExprGenerator(scope=self.scope)

    def visit(self, node: AstNode) -> str:
        """
        Generate C++ code for a statement node.        
        This method dispatches to the appropriate visit_* method based on node type.
        All generated code is terminated with a semicolon where applicable.        
        Args:
            node (AstNode): AST node representing a statement.            
        Returns:
            str: Generated C++ code.            
        Raises:
            NotImplementedError: If the node type is not supported.
        """
        method = getattr(self, f"visit_{type(node).__name__}", None)
        if not method:
            raise NotImplementedError(
                f"BasicStatementGenerator does not support node type {type(node).__name__}"
            )
        return method(node)
    
    # ---------- Assignment Statements ----------
    def visit_Assign(self, node: Assign) -> str:
        """
        Generate C++ code for an assignment statement.               
        Args:
            node (Assign): AST node representing an assignment.            
        Returns:
            str: C++ assignment code.          
        Raises:
            NotImplementedError: If assignment target is not a simple identifier.
        """
        if not isinstance(node.target, Identifier):
            raise NotImplementedError(
                "Assignment only supports simple identifiers (no subscripts or attributes)"
            )
        
        name = node.target.name
        rhs_code = self.expr.visit(node.value)

        # Declare variable on first assignment
        if not self.scope.exists(name):
            self.scope.declare(name)
            return f"DynamicType {name} = {rhs_code};"
        
        # Reassign existing variable
        return f"{name} = {rhs_code};"
    
    # ---------- Expression Statements ----------
    def visit_ExprStmt(self, node: ExprStmt) -> str:
        """
        Generate C++ code for an expression statement.        
        Args:
            node (ExprStmt): AST node representing an expression statement.            
        Returns:
            str: C++ expression code terminated with semicolon.
        """
        code = self.expr.visit(node.value)
        return f"{code};"
    
    # ---------- Return Statements ----------
    def visit_Return(self, node: Return) -> str:
        """
        Generate C++ code for a return statement.
        Args:
            node (Return): AST node representing a return statement.            
        Returns:
            str: C++ return statement code.
        """
        if node.value is None:
            return "return DynamicType();"
        return f"return {self.expr.visit(node.value)};"