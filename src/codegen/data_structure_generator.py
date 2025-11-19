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
        return f"/* Unsupported data structure: {type(node).__name__} */"



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
        
        if len(elements) <= 3:
            # Short lists on one line
            elements_str = ', '.join(elements)
            return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"
        else:
            # Long lists with line breaks for readability  
            elements_str = ',\n    '.join(elements)
            return f"DynamicType(std::vector<DynamicType>{{\n    {elements_str}\n}})"

    def _deduce_cpp_vector_type(self, node):
        """
        Deduce the type for std::vector in C++ based on the first element.
        Args:
                node (ListExpr): AST node for a list.
        Returns:
                str: Deduced C++ type.
        """
        elements = node.elements
        if elements:
            first = elements[0]
            if hasattr(first, "value"):
                if isinstance(first.value, int):
                    return "int"
                elif isinstance(first.value, float):
                    return "double"
                elif isinstance(first.value, str):
                    return "string"
            return "auto"
        return "auto"

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
        elements_str = ', '.join(elements)
        return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"

    def _deduce_cpp_tuple_types(self, node):
        """
        Deduce types for std::tuple in C++ based on elements.
        Args:
                node (TupleExpr): AST node for a tuple.
        Returns:
                str: Deduced C++ types.
        """
        types = []
        for elem in node.elements:
            if hasattr(elem, "value"):
                if isinstance(elem.value, int):
                    types.append("int")
                elif isinstance(elem.value, float):
                    types.append("double")
                elif isinstance(elem.value, str):
                    types.append("string")
                else:
                    types.append("auto")
            else:
                types.append("auto")
        return ", ".join(types)

    def visit_SetExpr_cpp(self, node) -> str:
        """
        Generate C++ code for a set expression using DynamicType.
        For now, represent sets as vectors since DynamicType doesn't have native set support.
        Args:
                node (SetExpr): AST node for a set.
        Returns:
                str: C++ DynamicType code representing a set.
        """
        elements = []
        for e in node.elements:
            if self.expr_generator:
                elements.append(self.expr_generator.visit(e))
            else:
                elements.append(self.visit(e))
        
        # For now, represent sets as vectors (would need unique elements logic)
        elements_str = ', '.join(elements)
        return f"DynamicType(std::vector<DynamicType>{{{elements_str}}})"

    def _deduce_cpp_set_type(self, node):
        """
        Deduce the type for std::set in C++ based on the first element.
        Args:
                node (SetExpr): AST node for a set.
        Returns:
                str: Deduced C++ type.
        """
        elements = node.elements
        if elements:
            first = elements[0]
            if hasattr(first, "value"):
                if isinstance(first.value, int):
                    return "int"
                elif isinstance(first.value, float):
                    return "double"
                elif isinstance(first.value, str):
                    return "string"
            return "auto"
        return "auto"

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

    def _deduce_cpp_dict_types(self, node):
        """
        Deduce key and value types for std::map in C++ based on the first pair.
        Args:
                node (DictExpr): AST node for a dictionary.
        Returns:
                tuple: (key_type, value_type)
        """
        pairs = node.pairs
        if pairs:
            k, v = pairs[0]
            k_type = "auto"
            v_type = "auto"
            if hasattr(k, "value"):
                if isinstance(k.value, int):
                    k_type = "int"
                elif isinstance(k.value, float):
                    k_type = "double"
                elif isinstance(k.value, str):
                    k_type = "string"
            if hasattr(v, "value"):
                if isinstance(v.value, int):
                    v_type = "int"
                elif isinstance(v.value, float):
                    v_type = "double"
                elif isinstance(v.value, str):
                    v_type = "string"
            return k_type, v_type
        return "auto", "auto"
