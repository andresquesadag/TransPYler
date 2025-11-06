
#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <stdexcept>


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


int main() {
    // Example variable used by generated code
    DynamicValue x(10);

if ((DynamicValue((x == DynamicValue(5)))).toBool()) {
    ;  // pass
}

    return 0;
}
