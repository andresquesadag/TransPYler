# TODO(Randy): Implement data structure generator (Lists, tuples, etc.)

"""
List Operations Code Generator for Fangless Python to C++ Transpiler
Person 3 - List Data Structures

Handles:
- List literal creation: [1, 2, 3]
- List indexing: lst[0]
- List slicing (basic): lst[1:3]
- List methods: append, extend, etc.

Author: Person 3
"""

from typing import Optional


class ListOperationsGenerator:
    """
    Generates C++ code for list operations.
    Works with DynamicValue's vector-based list implementation.
    """
    
    def __init__(self, expression_generator=None):
        """
        Initialize list operations generator.
        
        Args:
            expression_generator: Reference to Person 2's expression generator
        """
        self.expression_gen = expression_generator
    
    def visit_List(self, node) -> str:
        """
        Generate C++ code for list literal.
        
        AST Structure:
            List(elts=[expr, expr, ...])
        
        Example:
            [1, 2, 3]  →  DynamicValue(std::vector<DynamicValue>{
                              DynamicValue(1), 
                              DynamicValue(2), 
                              DynamicValue(3)
                          })
        """
        if not node.elts:
            # Empty list
            return "DynamicValue(std::vector<DynamicValue>())"
        
        # Generate elements
        elements = []
        for elt in node.elts:
            if self.expression_gen:
                elem_code = self.expression_gen.visit(elt)
            else:
                elem_code = self._simple_element(elt)
            elements.append(elem_code)
        
        elements_str = ", ".join(elements)
        return f"DynamicValue(std::vector<DynamicValue>{{{elements_str}}})"
    
    def visit_Subscript(self, node) -> str:
        """
        Generate C++ code for subscript access.
        
        AST Structure:
            Subscript(value=expr, slice=Index(value=expr) | Slice(...))
        
        Examples:
            lst[0]      →  (lst).toList().at((DynamicValue(0)).toInt())
            lst[i]      →  (lst).toList().at((i).toInt())
            lst[-1]     →  (lst).toList().at((lst).toList().size() - 1)
        """
        # Get list expression
        if self.expression_gen:
            value = self.expression_gen.visit(node.value)
        else:
            value = self._simple_element(node.value)
        
        # Handle slice
        slice_node = node.slice
        
        # Check if it's simple index or slice
        if slice_node.__class__.__name__ == 'Index':
            # Old AST style: Subscript(slice=Index(value=...))
            index_expr = slice_node.value
        elif slice_node.__class__.__name__ == 'Slice':
            # Slice notation: lst[start:stop:step]
            return self._generate_slice(value, slice_node)
        else:
            # New AST style: Subscript(slice=<expr>)
            index_expr = slice_node
        
        # Generate index
        if self.expression_gen:
            index = self.expression_gen.visit(index_expr)
        else:
            index = self._simple_element(index_expr)
        
        # Handle negative indices
        if self._is_negative_literal(index_expr):
            # lst[-1] → lst.toList()[lst.toList().size() - 1]
            abs_index = abs(self._get_literal_value(index_expr))
            return f"({value}).toList().at(({value}).toList().size() - {abs_index})"
        
        # Standard positive index with bounds checking
        return f"({value}).toList().at(({index}).toInt())"
    
    def _generate_slice(self, value: str, slice_node) -> str:
        """
        Generate C++ code for list slicing.
        
        Python: lst[start:stop:step]
        C++: slice_list(lst, start, stop, step)
        
        Note: Requires helper function slice_list() in cpp_templates.py
        """
        start = "DynamicValue(0)" if slice_node.lower is None else (
            self.expression_gen.visit(slice_node.lower) if self.expression_gen 
            else self._simple_element(slice_node.lower)
        )
        
        stop = f"DynamicValue(({value}).toList().size())" if slice_node.upper is None else (
            self.expression_gen.visit(slice_node.upper) if self.expression_gen
            else self._simple_element(slice_node.upper)
        )
        
        step = "DynamicValue(1)" if slice_node.step is None else (
            self.expression_gen.visit(slice_node.step) if self.expression_gen
            else self._simple_element(slice_node.step)
        )
        
        return f"slice_list({value}, {start}, {stop}, {step})"
    
    def _is_negative_literal(self, node) -> bool:
        """Check if node is negative numeric literal"""
        if node.__class__.__name__ == 'UnaryOp':
            if node.op.__class__.__name__ == 'USub':
                operand = node.operand
                return operand.__class__.__name__ in ('Num', 'Constant')
        return False
    
    def _get_literal_value(self, node):
        """Extract literal value from node"""
        if node.__class__.__name__ == 'UnaryOp' and node.op.__class__.__name__ == 'USub':
            operand = node.operand
            return -(operand.value if hasattr(operand, 'value') else operand.n)
        if hasattr(node, 'value'):
            return node.value
        if hasattr(node, 'n'):
            return node.n
        return 0
    
    def _simple_element(self, node):
        """Fallback simple element generation"""
        node_type = node.__class__.__name__
        
        if node_type in ('Num', 'Constant'):
            value = node.value if hasattr(node, 'value') else node.n
            return f"DynamicValue({value})"
        elif node_type == 'Name':
            return node.id
        elif node_type == 'Str':
            return f'DynamicValue("{node.s}")'
        else:
            return "DynamicValue()"

    def visit_Tuple(self, node) -> str:
        """
        Generate a tuple as a DynamicValue containing a vector (tuples are
        represented as lists in the runtime stub for simplicity).
        """
        # Reuse list generation semantics (tuple -> vector)
        # node.elts is the list of elements
        if not getattr(node, 'elts', None):
            return "DynamicValue(std::vector<DynamicValue>())"

        elements = []
        for elt in node.elts:
            if self.expression_gen:
                elem_code = self.expression_gen.visit(elt)
            else:
                elem_code = self._simple_element(elt)
            elements.append(elem_code)

        elements_str = ", ".join(elements)
        return f"DynamicValue(std::vector<DynamicValue>{{{elements_str}}})"

    def visit_Dict(self, node) -> str:
        """
        Generate a dictionary literal as a DynamicValue wrapping an
        std::unordered_map<std::string, DynamicValue>.
        Assumes keys are simple string constants for now.
        """
        items = []
        keys = getattr(node, 'keys', []) or []
        values = getattr(node, 'values', []) or []
        for k, v in zip(keys, values):
            # Only support string constant keys for simplicity
            if hasattr(k, 'value') and isinstance(k.value, str):
                key_code = k.value
            else:
                # Fallback to stringifying the expression
                if self.expression_gen:
                    key_code = self.expression_gen.visit(k)
                else:
                    key_code = '""'

            if self.expression_gen:
                val_code = self.expression_gen.visit(v)
            else:
                val_code = self._simple_element(v)

            # ensure key is a C++ string literal
            if not key_code.startswith('"'):
                key_code = f'"{key_code}"'

            items.append(f"{{{key_code}, {val_code}}}")

        items_str = ", ".join(items)
        return f"DynamicValue(std::unordered_map<std::string, DynamicValue>{{{items_str}}})"


