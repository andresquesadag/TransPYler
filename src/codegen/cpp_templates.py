"""
C++ Template Functions and Helpers
Person 3 - Support Functions for Control Flow and Lists

Provides C++ helper functions that support:
- List operations (append, len, slice)
- Range function
- Built-in Python functions

Author: Person 3
"""


def generate_list_helper_functions() -> str:
    """
    Generate C++ helper functions for list operations.
    These work with DynamicValue's vector<DynamicValue> representation.
    """
    return """
// ============================================================================
// List Helper Functions
// ============================================================================

// Append item to list (mutates list in-place)
DynamicValue list_append(DynamicValue& list, const DynamicValue& item) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: append() called on non-list");
    }
    list.toList().push_back(item);
    return DynamicValue();  // None
}

// Get length of list or string
DynamicValue list_len(const DynamicValue& obj) {
    if (obj.isList()) {
        return DynamicValue(static_cast<int>(obj.toList().size()));
    }
    if (obj.isString()) {
        return DynamicValue(static_cast<int>(obj.toString().length()));
    }
    throw std::runtime_error("TypeError: len() called on unsupported type");
}

// Extend list with another list (mutates list in-place)
DynamicValue list_extend(DynamicValue& list, const DynamicValue& other) {
    if (!list.isList() || !other.isList()) {
        throw std::runtime_error("TypeError: extend() requires two lists");
    }
    const auto& other_vec = other.toList();
    list.toList().insert(list.toList().end(), other_vec.begin(), other_vec.end());
    return DynamicValue();  // None
}

// Insert item at index
DynamicValue list_insert(DynamicValue& list, const DynamicValue& index, const DynamicValue& item) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: insert() called on non-list");
    }
    int idx = index.toInt();
    auto& vec = list.toList();
    if (idx < 0) idx = std::max(0, static_cast<int>(vec.size()) + idx);
    if (idx > static_cast<int>(vec.size())) idx = vec.size();
    vec.insert(vec.begin() + idx, item);
    return DynamicValue();  // None
}

// Remove first occurrence of item
DynamicValue list_remove(DynamicValue& list, const DynamicValue& item) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: remove() called on non-list");
    }
    auto& vec = list.toList();
    for (size_t i = 0; i < vec.size(); i++) {
        if (vec[i] == item) {
            vec.erase(vec.begin() + i);
            return DynamicValue();  // None
        }
    }
    throw std::runtime_error("ValueError: item not in list");
}

// Pop item at index (default: -1)
DynamicValue list_pop(DynamicValue& list, const DynamicValue& index = DynamicValue(-1)) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: pop() called on non-list");
    }
    auto& vec = list.toList();
    if (vec.empty()) {
        throw std::runtime_error("IndexError: pop from empty list");
    }
    int idx = index.toInt();
    if (idx < 0) idx = vec.size() + idx;
    if (idx < 0 || idx >= static_cast<int>(vec.size())) {
        throw std::runtime_error("IndexError: pop index out of range");
    }
    DynamicValue item = vec[idx];
    vec.erase(vec.begin() + idx);
    return item;
}

// List slicing
DynamicValue slice_list(const DynamicValue& list, const DynamicValue& start, 
                       const DynamicValue& stop, const DynamicValue& step) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: slice on non-list");
    }
    
    const auto& vec = list.toList();
    int size = vec.size();
    int s = start.toInt();
    int e = stop.toInt();
    int st = step.toInt();
    
    if (st == 0) throw std::runtime_error("ValueError: slice step cannot be zero");
    
    // Handle negative indices
    if (s < 0) s = std::max(0, size + s);
    if (e < 0) e = std::max(0, size + e);
    
    // Clamp to bounds
    s = std::max(0, std::min(s, size));
    e = std::max(0, std::min(e, size));
    
    std::vector<DynamicValue> result;
    if (st > 0) {
        for (int i = s; i < e; i += st) {
            result.push_back(vec[i]);
        }
    } else {
        for (int i = s; i > e; i += st) {
            result.push_back(vec[i]);
        }
    }
    
    return DynamicValue(result);
}
"""


def generate_range_functions() -> str:
    """
    Generate C++ range() function implementations.
    Supports range(stop), range(start, stop), range(start, stop, step).
    """
    return """
// ============================================================================
// Range Functions
// ============================================================================

// range(stop)
DynamicValue range_func(int stop) {
    std::vector<DynamicValue> result;
    for (int i = 0; i < stop; i++) {
        result.push_back(DynamicValue(i));
    }
    return DynamicValue(result);
}

// range(start, stop)
DynamicValue range_func(int start, int stop) {
    std::vector<DynamicValue> result;
    if (start < stop) {
        for (int i = start; i < stop; i++) {
            result.push_back(DynamicValue(i));
        }
    }
    return DynamicValue(result);
}

// range(start, stop, step)
DynamicValue range_func(int start, int stop, int step) {
    std::vector<DynamicValue> result;
    
    if (step == 0) {
        throw std::runtime_error("ValueError: range() step cannot be zero");
    }
    
    if (step > 0) {
        for (int i = start; i < stop; i += step) {
            result.push_back(DynamicValue(i));
        }
    } else {
        for (int i = start; i > stop; i += step) {
            result.push_back(DynamicValue(i));
        }
    }
    
    return DynamicValue(result);
}
"""


def generate_builtin_functions() -> str:
    """
    Generate C++ implementations of Python built-in functions.
    """
    return """
// ============================================================================
// Built-in Functions
// ============================================================================

// print() function - supports multiple arguments
void print_func() {
    std::cout << std::endl;
}

template<typename T, typename... Args>
void print_func(const T& first, const Args&... args) {
    first.print();
    if (sizeof...(args) > 0) {
        std::cout << " ";
        print_func(args...);
    } else {
        std::cout << std::endl;
    }
}

// len() function
DynamicValue len_func(const DynamicValue& obj) {
    return list_len(obj);
}

// type() function - returns type name as string
DynamicValue type_func(const DynamicValue& obj) {
    switch(obj.getType()) {
        case DynamicValue::NONE: return DynamicValue("NoneType");
        case DynamicValue::INT: return DynamicValue("int");
        case DynamicValue::FLOAT: return DynamicValue("float");
        case DynamicValue::STRING: return DynamicValue("str");
        case DynamicValue::BOOL: return DynamicValue("bool");
        case DynamicValue::LIST: return DynamicValue("list");
        default: return DynamicValue("unknown");
    }
}

// str() function - convert to string
DynamicValue str_func(const DynamicValue& obj) {
    return DynamicValue(obj.toString());
}

// int() function - convert to int
DynamicValue int_func(const DynamicValue& obj) {
    return DynamicValue(obj.toInt());
}

// float() function - convert to float
DynamicValue float_func(const DynamicValue& obj) {
    return DynamicValue(obj.toFloat());
}

// bool() function - convert to bool
DynamicValue bool_func(const DynamicValue& obj) {
    return DynamicValue(obj.toBool());
}

// min() function for lists
DynamicValue min_func(const DynamicValue& list) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: min() requires a list");
    }
    const auto& vec = list.toList();
    if (vec.empty()) {
        throw std::runtime_error("ValueError: min() arg is an empty sequence");
    }
    DynamicValue min_val = vec[0];
    for (size_t i = 1; i < vec.size(); i++) {
        if (vec[i] < min_val) {
            min_val = vec[i];
        }
    }
    return min_val;
}

// max() function for lists
DynamicValue max_func(const DynamicValue& list) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: max() requires a list");
    }
    const auto& vec = list.toList();
    if (vec.empty()) {
        throw std::runtime_error("ValueError: max() arg is an empty sequence");
    }
    DynamicValue max_val = vec[0];
    for (size_t i = 1; i < vec.size(); i++) {
        if (vec[i] > max_val) {
            max_val = vec[i];
        }
    }
    return max_val;
}

// sum() function for lists
DynamicValue sum_func(const DynamicValue& list, const DynamicValue& start = DynamicValue(0)) {
    if (!list.isList()) {
        throw std::runtime_error("TypeError: sum() requires a list");
    }
    DynamicValue result = start;
    for (const auto& item : list.toList()) {
        result = result + item;
    }
    return result;
}
"""


def generate_complete_cpp_header() -> str:
    """
    Generate complete C++ header with all helper functions.
    This is the full header that goes at the top of generated C++ files.
    """
    header = """// ============================================================================
// Generated by Fangless Python to C++ Transpiler
// Person 3: Control Flow and List Operations Support
// ============================================================================

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <stdexcept>
#include <cmath>
#include <functional>
#include <algorithm>

// Note: DynamicValue class should be provided by Person 1
// This header assumes DynamicValue is already defined

"""
    
    header += generate_list_helper_functions()
    header += "\n"
    header += generate_range_functions()
    header += "\n"
    header += generate_builtin_functions()
    
    return header


__all__ = [
    'generate_list_helper_functions',
    'generate_range_functions',
    'generate_builtin_functions',
    'generate_complete_cpp_header',
]

