// Copyright (c) 2025 Andres Quesada, David Obando, Randy Aguero
#ifndef DYNAMIC_TYPE_HPP
#define DYNAMIC_TYPE_HPP

#include <any>
#include <cmath>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <memory>
#include <stdexcept>
#include <string>
#include <sstream>
#include <unordered_set>
#include <vector>

/**
 * DynamicType: Emulates Python's dynamic typing in C++
 * Supports: int, double, string, bool, None (nullptr)
 * and collections: list, dict, set
 */
class DynamicType;

/**
 * Hash function specialization for DynamicType
 * 
 * This allows DynamicType objects to be used in hash-based containers
 * like std::unordered_set<DynamicType> and std::unordered_map<DynamicType, T>
 * 
 * The hash is computed based on the underlying value type:
 * - INT: uses std::hash<int>
 * - DOUBLE: uses std::hash<double>
 * - STRING: uses std::hash<std::string>
 * - BOOL: uses std::hash<bool>
 * - NONE: returns 0
 * - Complex types (LIST, DICT, SET): uses hash of their string representation
 */
namespace std {
    template<>
    struct hash<DynamicType> {
        size_t operator()(const DynamicType& value) const;
    };
}


class DynamicType{
  public:
    enum class Type {
      NONE,
      INT,
      DOUBLE,
      STRING,
      BOOL,
      LIST,
      DICT,
      SET
    };

  private:
    std::any value;
    Type type;

  public:
    // Constructors
    DynamicType() : type(Type::NONE) {}

    DynamicType(int val) : value(val), type(Type::INT) {}

    DynamicType(double val) : value(val), type(Type::DOUBLE) {}

    DynamicType(const std::string &val) : value(val), type(Type::STRING) {}

    DynamicType(const char *val) : value(std::string(val)), type(Type::STRING) {}

    DynamicType(bool val) : value(val), type(Type::BOOL) {}

    DynamicType(const std::vector<DynamicType> &val) : value(val), type(Type::LIST) {}

    DynamicType(const std::map<std::string, DynamicType> &val) : value(val), type(Type::DICT) {}

    DynamicType(const std::unordered_set<DynamicType> &val) : value(val), type(Type::SET) {}
    
    DynamicType(const std::set<DynamicType> &val) : value(val), type(Type::SET) {}

    // Type checking
    /**
     * Get the type of the DynamicType instance
     * @return Type enum representing the type
     */
    Type getType() const { return type; }

    bool isNone() const { return type == Type::NONE; }
    bool isInt() const { return type == Type::INT; }
    bool isDouble() const { return type == Type::DOUBLE; }
    bool isString() const { return type == Type::STRING; }
    bool isBool() const { return type == Type::BOOL; }
    bool isList() const { return type == Type::LIST; }
    bool isDict() const { return type == Type::DICT; }
    bool isSet() const { return type == Type::SET; }
    bool isNumeric() const { return type == Type::INT || type == Type::DOUBLE; }

    // Type conversion helpers
    int toInt() const;
    double toDouble() const;
    std::string toString() const;
    bool toBool() const;

    // Arithmetic operators
    DynamicType operator+(const DynamicType &other) const;
    DynamicType operator-(const DynamicType &other) const;
    DynamicType operator*(const DynamicType &other) const;
    DynamicType operator/(const DynamicType &other) const;
    DynamicType operator%(const DynamicType &other) const;
    DynamicType pow(const DynamicType &exponent) const;
    DynamicType floor_div(const DynamicType &other) const;

    // Comparison operators (needed for std::set<DynamicType>)
    bool operator==(const DynamicType &other) const;
    bool operator!=(const DynamicType &other) const;
    bool operator<(const DynamicType &other) const;
    bool operator<=(const DynamicType &other) const;
    bool operator>(const DynamicType &other) const;
    bool operator>=(const DynamicType &other) const;

    // Logical operators
    DynamicType operator&&(const DynamicType &other) const;
    DynamicType operator||(const DynamicType &other) const;
    DynamicType operator!() const;

    // Unary operators
    DynamicType operator-() const;
    DynamicType operator+() const;

    // List/Dict operations
    DynamicType &operator[](const size_t index);
    DynamicType &operator[](const std::string &key);
    DynamicType &operator[](const DynamicType &key);

    // Output stream
    friend std::ostream &operator<<(std::ostream &os, const DynamicType &dt) {
      os << dt.toString();
      return os;
    }

    // Collection getters
    // Non-const accessors (mutation allowed)
    std::vector<DynamicType>& getList();
    std::map<std::string, DynamicType>& getDict();
    std::unordered_set<DynamicType>& getSet();
    // Const accessors (read-only)
    const std::vector<DynamicType>& getList() const;
    const std::map<std::string, DynamicType>& getDict() const;
    const std::unordered_set<DynamicType>& getSet() const;

    // Lists methods
    void append(const DynamicType &item);
    void remove(size_t index);
    /**
     * Get a sublist from start to end (exclusive).
     * Python example: lst[2:5]
     * @param start Starting index
     * @param end Ending index (exclusive)
     * @return DynamicType containing the sublist
     * @throws std::runtime_error if not a list or indices are out of range
     */
    DynamicType sublist(size_t start, size_t end);
    /**
     * Get a sublist from start to end (exclusive) with a step.
     * Python example: lst[2:10:2]
     * @param start Starting index
     * @param end Ending index (exclusive)
     * @param step Step size
     * @return DynamicType containing the sublist
     * @throws std::runtime_error if not a list or indices are out of range
     */
    DynamicType sublist(size_t start, size_t end, size_t step);
    
    // DynamicType wrapper overloads for sublist
    DynamicType sublist(const DynamicType& start, const DynamicType& end) {
      return sublist(static_cast<size_t>(start.toInt()), static_cast<size_t>(end.toInt()));
    }
    DynamicType sublist(const DynamicType& start, const DynamicType& end, const DynamicType& step) {
      return sublist(static_cast<size_t>(start.toInt()), static_cast<size_t>(end.toInt()), static_cast<size_t>(step.toInt()));
    }

    // Dict methods
    void remove(const std::string &key);
    void set(const std::string &key, const DynamicType &value);
    void set(const DynamicType &key, const DynamicType &value) { set(key.toString(), value); }
    DynamicType get(const std::string &key) const;
    DynamicType get(const DynamicType &key) const { return get(key.toString()); }
    void removeKey(const std::string &key) { remove(key); }
    void removeKey(const DynamicType &key) { remove(key.toString()); }
    /**
     * Get all keys from dictionary as a list.
     * Python example: my_dict.keys()
     * @return DynamicType containing list of keys as strings
     * @throws std::runtime_error if not a dict
    */
    DynamicType keys() const;
    /**
     * Get all values from dictionary as a list.
     * Python example: my_dict.values()
     * @return DynamicType containing list of values
     * @throws std::runtime_error if not a dict
     */
    DynamicType values() const;
    /**
     * Get all key-value pairs from dictionary as a list of lists.
     * Python example: my_dict.items()
     * Each item is a 2-element list [key, value]
     * @return DynamicType containing list of [key, value] pairs
     * @throws std::runtime_error if not a dict
     */
    DynamicType items() const;
    
    // List methods
    void removeAt(size_t index) { remove(index); }
    void removeAt(const DynamicType &index) { remove(static_cast<size_t>(index.toInt())); }
    
    // Dict, List common methods  
    bool contains(const DynamicType& key) const;
    
    // Set operations
    void add(const DynamicType &item);
    void remove(const DynamicType &item);
};

#endif // DYNAMIC_TYPE_HPP