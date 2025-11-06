"""
Temporary Stubs for Testing Person 3 Code Independently

These stubs allow Person 3 to test control flow generation
without waiting for Person 1 and Person 2 to complete their work.

WARNING: These are TEMPORARY and should be replaced with real implementations!
"""


class StubExpressionGenerator:
    """
    Stub implementation of Person 2's ExpressionGenerator.
    Provides basic expression generation for testing.
    """
    
    def visit(self, node):
        """Generate C++ code for expression AST node"""
        # The test suite uses a MockNode which mutates the class __name__ at
        # runtime. Relying solely on __class__.__name__ becomes fragile. Try
        # to infer the node type from attributes when the reported name is not
        # one of the expected AST node types.
        node_type = node.__class__.__name__
        known_types = {
            'Num', 'Constant', 'Name', 'Str', 'NameConstant', 'BinOp',
            'UnaryOp', 'Compare', 'BoolOp', 'Call'
        }

        if node_type not in known_types:
            # Heuristic detection based on typical AST attributes
            if hasattr(node, 'left') and hasattr(node, 'ops') and hasattr(node, 'comparators'):
                node_type = 'Compare'
            elif hasattr(node, 'func') and hasattr(node, 'args'):
                node_type = 'Call'
            elif hasattr(node, 'left') and hasattr(node, 'right') and hasattr(node, 'op'):
                node_type = 'BinOp'
            elif hasattr(node, 'operand') and hasattr(node, 'op'):
                node_type = 'UnaryOp'
            elif hasattr(node, 'values') and hasattr(node, 'op'):
                node_type = 'BoolOp'
            elif hasattr(node, 'id'):
                node_type = 'Name'
            elif hasattr(node, 's'):
                node_type = 'Str'
            elif hasattr(node, 'value'):
                # Could be Constant or NameConstant. Use value type to decide.
                node_type = 'Constant'
        
        if node_type in ('Num', 'Constant'):
            value = node.value if hasattr(node, 'value') else node.n
            if isinstance(value, int):
                return f"DynamicValue({value})"
            elif isinstance(value, float):
                return f"DynamicValue({value})"
            elif isinstance(value, str):
                return f'DynamicValue("{value}")'
            elif isinstance(value, bool):
                return f"DynamicValue({'true' if value else 'false'})"
            else:
                return "DynamicValue()"
        
        elif node_type == 'Name':
            return node.id
        
        elif node_type == 'Str':
            return f'DynamicValue("{node.s}")'
        
        elif node_type == 'NameConstant':
            if node.value is True:
                return "DynamicValue(true)"
            elif node.value is False:
                return "DynamicValue(false)"
            elif node.value is None:
                return "DynamicValue()"
            
        elif node_type == 'BinOp':
            left = self.visit(node.left)
            right = self.visit(node.right)
            op = node.op.__class__.__name__
            
            op_map = {
                'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/',
                'FloorDiv': '/', 'Mod': '%', 'Pow': 'pow',
                'Lt': '<', 'Gt': '>', 'LtE': '<=', 'GtE': '>=',
                'Eq': '==', 'NotEq': '!='
            }
            
            cpp_op = op_map.get(op, '+')
            if cpp_op == 'pow':
                return f"DynamicValue(std::pow(({left}).toFloat(), ({right}).toFloat()))"
            return f"({left} {cpp_op} {right})"
        
        elif node_type == 'UnaryOp':
            operand = self.visit(node.operand)
            op = node.op.__class__.__name__
            if op == 'USub':
                return f"(DynamicValue(0) - {operand})"
            elif op == 'Not':
                return f"DynamicValue(!({operand}).toBool())"
            return operand
        
        elif node_type == 'Compare':
            left = self.visit(node.left)
            # Handle first comparison
            op = node.ops[0].__class__.__name__
            right = self.visit(node.comparators[0])
            
            op_map = {
                'Lt': '<', 'Gt': '>', 'LtE': '<=', 'GtE': '>=',
                'Eq': '==', 'NotEq': '!='
            }
            cpp_op = op_map.get(op, '==')
            
            result = f"({left} {cpp_op} {right})"
            
            # Handle chained comparisons (if any)
            for i in range(1, len(node.ops)):
                op = node.ops[i].__class__.__name__
                cpp_op = op_map.get(op, '==')
                left = self.visit(node.comparators[i-1])
                right = self.visit(node.comparators[i])
                result = f"(({result}).toBool() && ({left} {cpp_op} {right}).toBool())"
            
            return f"DynamicValue({result})"
        
        elif node_type == 'BoolOp':
            op = node.op.__class__.__name__
            values = [self.visit(v) for v in node.values]
            
            if op == 'And':
                result = f"({values[0]}).toBool()"
                for v in values[1:]:
                    result = f"({result} && ({v}).toBool())"
            else:  # Or
                result = f"({values[0]}).toBool()"
                for v in values[1:]:
                    result = f"({result} || ({v}).toBool())"
            
            return f"DynamicValue({result})"
        
        elif node_type == 'Call':
            func_name = node.func.id if hasattr(node.func, 'id') else 'unknown'
            args = [self.visit(arg) for arg in node.args]
            args_str = ', '.join(args)
            
            # Built-in function mapping
            builtin_map = {
                'print': 'print_func',
                'len': 'len_func',
                'range': 'range_func',
                'str': 'str_func',
                'int': 'int_func',
                'float': 'float_func',
                'bool': 'bool_func',
                'min': 'min_func',
                'max': 'max_func',
                'sum': 'sum_func',
            }
            
            cpp_func = builtin_map.get(func_name, func_name)
            return f"{cpp_func}({args_str})"
        
        else:
            return f"/* Unhandled: {node_type} */"


def get_stub_dynamic_value_class() -> str:
    """
    Stub DynamicValue class for testing.
    This is a TEMPORARY replacement for Person 1's implementation.
    """
    return """
// ============================================================================
// STUB DynamicValue Class - TEMPORARY FOR TESTING ONLY
// Replace with Person 1's actual implementation!
// ============================================================================

class DynamicValue {
public:
    enum Type { NONE, INT, FLOAT, STRING, BOOL, LIST };
    
private:
    Type type;
    int int_val;
    double float_val;
    std::string string_val;
    bool bool_val;
    std::vector<DynamicValue> list_val;

public:
    // Constructors
    DynamicValue() : type(NONE), int_val(0), float_val(0.0), bool_val(false) {}
    DynamicValue(int v) : type(INT), int_val(v), float_val(0.0), bool_val(false) {}
    DynamicValue(double v) : type(FLOAT), int_val(0), float_val(v), bool_val(false) {}
    DynamicValue(const std::string& v) : type(STRING), int_val(0), float_val(0.0), string_val(v), bool_val(false) {}
    DynamicValue(bool v) : type(BOOL), int_val(0), float_val(0.0), bool_val(v) {}
    DynamicValue(const std::vector<DynamicValue>& v) : type(LIST), int_val(0), float_val(0.0), bool_val(false), list_val(v) {}
    
    // Type checking
    Type getType() const { return type; }
    bool isInt() const { return type == INT; }
    bool isFloat() const { return type == FLOAT; }
    bool isString() const { return type == STRING; }
    bool isBool() const { return type == BOOL; }
    bool isList() const { return type == LIST; }
    bool isNone() const { return type == NONE; }
    
    // Conversions
    int toInt() const {
        if (type == INT) return int_val;
        if (type == FLOAT) return static_cast<int>(float_val);
        if (type == BOOL) return bool_val ? 1 : 0;
        throw std::runtime_error("Cannot convert to int");
    }
    
    double toFloat() const {
        if (type == FLOAT) return float_val;
        if (type == INT) return static_cast<double>(int_val);
        if (type == BOOL) return bool_val ? 1.0 : 0.0;
        throw std::runtime_error("Cannot convert to float");
    }
    
    std::string toString() const {
        if (type == STRING) return string_val;
        if (type == INT) return std::to_string(int_val);
        if (type == FLOAT) return std::to_string(float_val);
        if (type == BOOL) return bool_val ? "True" : "False";
        if (type == NONE) return "None";
        throw std::runtime_error("Cannot convert to string");
    }
    
    bool toBool() const {
        if (type == BOOL) return bool_val;
        if (type == INT) return int_val != 0;
        if (type == FLOAT) return float_val != 0.0;
        if (type == STRING) return !string_val.empty();
        if (type == LIST) return !list_val.empty();
        return false;
    }
    
    std::vector<DynamicValue>& toList() {
        if (type == LIST) return list_val;
        throw std::runtime_error("Value is not a list");
    }
    
    const std::vector<DynamicValue>& toList() const {
        if (type == LIST) return list_val;
        throw std::runtime_error("Value is not a list");
    }
    
    // Operators
    DynamicValue operator+(const DynamicValue& other) const {
        if (type == INT && other.type == INT) return DynamicValue(int_val + other.int_val);
        if ((type == FLOAT || type == INT) && (other.type == FLOAT || other.type == INT))
            return DynamicValue(toFloat() + other.toFloat());
        if (type == STRING && other.type == STRING) return DynamicValue(string_val + other.string_val);
        throw std::runtime_error("Unsupported operation +");
    }
    
    DynamicValue operator-(const DynamicValue& other) const {
        if (type == INT && other.type == INT) return DynamicValue(int_val - other.int_val);
        if ((type == FLOAT || type == INT) && (other.type == FLOAT || other.type == INT))
            return DynamicValue(toFloat() - other.toFloat());
        throw std::runtime_error("Unsupported operation -");
    }
    
    DynamicValue operator*(const DynamicValue& other) const {
        if (type == INT && other.type == INT) return DynamicValue(int_val * other.int_val);
        if ((type == FLOAT || type == INT) && (other.type == FLOAT || other.type == INT))
            return DynamicValue(toFloat() * other.toFloat());
        throw std::runtime_error("Unsupported operation *");
    }
    
    DynamicValue operator/(const DynamicValue& other) const {
        if ((type == FLOAT || type == INT) && (other.type == FLOAT || other.type == INT)) {
            double divisor = other.toFloat();
            if (divisor == 0.0) throw std::runtime_error("Division by zero");
            return DynamicValue(toFloat() / divisor);
        }
        throw std::runtime_error("Unsupported operation /");
    }
    
    bool operator==(const DynamicValue& other) const {
        if (type != other.type) return false;
        switch(type) {
            case INT: return int_val == other.int_val;
            case FLOAT: return float_val == other.float_val;
            case STRING: return string_val == other.string_val;
            case BOOL: return bool_val == other.bool_val;
            case NONE: return true;
            default: return false;
        }
    }
    
    bool operator!=(const DynamicValue& other) const { return !(*this == other); }
    
    bool operator<(const DynamicValue& other) const {
        if (type == INT && other.type == INT) return int_val < other.int_val;
        if ((type == FLOAT || type == INT) && (other.type == FLOAT || other.type == INT))
            return toFloat() < other.toFloat();
        if (type == STRING && other.type == STRING) return string_val < other.string_val;
        throw std::runtime_error("Unsupported comparison <");
    }
    
    bool operator<=(const DynamicValue& other) const { return *this < other || *this == other; }
    bool operator>(const DynamicValue& other) const { return !(*this <= other); }
    bool operator>=(const DynamicValue& other) const { return !(*this < other); }
    
    void print() const {
        switch(type) {
            case INT: std::cout << int_val; break;
            case FLOAT: std::cout << float_val; break;
            case STRING: std::cout << string_val; break;
            case BOOL: std::cout << (bool_val ? "True" : "False"); break;
            case NONE: std::cout << "None"; break;
            case LIST:
                std::cout << "[";
                for (size_t i = 0; i < list_val.size(); i++) {
                    list_val[i].print();
                    if (i < list_val.size() - 1) std::cout << ", ";
                }
                std::cout << "]";
                break;
        }
    }
};
"""
