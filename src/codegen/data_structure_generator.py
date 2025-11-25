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


class DataStructureGenerator:
    """
    Generates code for data structure JSON nodes (lists, tuples, sets, dicts).
    Handles both Python and C++ targets, including type deduction for C++ STL containers.
    """

    def __init__(self, expr_generator=None):
        """
        Initialize the DataStructureGenerator for C++ code generation.
        Args:
                        expr_generator: Optional ExprGenerator for evaluating element expressions
        """
        self.target = "cpp"
        self.expr_generator = expr_generator

    def _create_dynamic_vector(self, elements: list) -> str:
        """Helper method to create DynamicType vector code with consistent formatting."""
        if len(elements) <= 3:
            elements_str = ", ".join(elements)
            return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"
        else:
            elements_str = ",\n    ".join(elements)
            return f"DynamicType(std::vector<DynamicType>{{\n    {elements_str}\n}})"

    def visit(self, node) -> str:
        """
        Dispatch code generation to the appropriate method based on node type and target.
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
                node: AST node.
        Returns:
                str: Error comment for unsupported node type.
        """
        raise NotImplementedError(
            f"DataStructureGenerator does not support node type {type(node).__name__}"
        )

    # --- C++ ---
    def visit_ListExpr_cpp(self, node) -> str:
        """
        Generate C++ code for a list expression using DynamicType vector.
        Args:
                node (ListExpr): AST node for a list.
        Returns:
                str: C++ DynamicType vector code.
        """
        elements = []
        for e in node.elements:
            if self.expr_generator:
                elements.append(self.expr_generator.visit(e))
            else:
                elements.append(self.visit(e))
        
        return self._create_dynamic_vector(elements)



    def visit_TupleExpr_cpp(self, node) -> str:
        """
        Generate C++ code for a tuple expression using DynamicType.
        For now, represent tuples as vectors since DynamicType doesn't have native tuple support.
        Args:
                node (TupleExpr): AST node for a tuple.
        Returns:
                str: C++ DynamicType code representing a tuple.
        """
        elements = []
        for e in node.elements:
            if self.expr_generator:
                elements.append(self.expr_generator.visit(e))
            else:
                elements.append(self.visit(e))
        
        # For now, represent tuples as immutable lists
        return self._create_dynamic_vector(elements)



    def visit_SetExpr_cpp(self, node) -> str:
        """
        Generate C++ code for a set expression using DynamicType set.
        Args:
                node (SetExpr): AST node for a set.
        Returns:
                str: C++ DynamicType set code.
        """
        elements = []
        for e in node.elements:
            if self.expr_generator:
                elements.append(self.expr_generator.visit(e))
            else:
                elements.append(self.visit(e))
        
        # Use std::unordered_set<DynamicType> for proper set semantics
        elements_str = ', '.join(elements)
        return f"DynamicType(std::unordered_set<DynamicType>{{{elements_str}}})"



    def visit_DictExpr_cpp(self, node) -> str:
        """
        Generate C++ code for a dictionary expression using DynamicType.
        Args:
                node (DictExpr): AST node for a dictionary.
        Returns:
                str: C++ DynamicType map code.
        """
        pairs = []
        for k, v in node.pairs:
            key_code = self.expr_generator.visit(k) if self.expr_generator else self.visit(k)
            val_code = self.expr_generator.visit(v) if self.expr_generator else self.visit(v)
            # Keys need to be converted to string for map
            pairs.append(f"{{({key_code}).toString(), {val_code}}}")
        
        if len(pairs) <= 2:
            # Short dictionaries on one line
            pairs_str = ', '.join(pairs)
            return f"DynamicType(std::map<std::string, DynamicType>{{{pairs_str}}})"
        else:
            # Long dictionaries with line breaks
            pairs_str = ',\n'.join(pairs)
            return f"DynamicType(std::map<std::string, DynamicType>{{\n{pairs_str}}})"

