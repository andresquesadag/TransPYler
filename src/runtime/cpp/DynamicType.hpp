// Copyright (c) 2025 Andres Quesada, David Obando, Randy Aguero
#ifndef DYNAMIC_TYPE_HPP
#define DYNAMIC_TYPE_HPP

#include <any>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <stdexcept>
#include <iostream>
#include <sstream>
#include <cmath>

/**
 * DynamicType: Emulates Python's dynamic typing in C++
 * Supports: int, double, string, bool, None (nullptr)
 * and collections: list, dict
 */
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
  std::set<DynamicType>& getSet();
  // Const accessors (read-only)
  const std::vector<DynamicType>& getList() const;
  const std::map<std::string, DynamicType>& getDict() const;
  const std::set<DynamicType>& getSet() const;

  // === DATA STRUCTURE MANIPULATION METHODS ===
  
  // List operations
  void append(const DynamicType& item);              // list.append(item)
  DynamicType sublist(const DynamicType& start, const DynamicType& end) const; // list[start:end] 
  void removeAt(const DynamicType& index);           // del list[index] / list.pop(index)
  
  // Dict operations  
  void set(const DynamicType& key, const DynamicType& value);  // dict[key] = value
  DynamicType get(const DynamicType& key) const;               // dict[key] or dict.get(key)
  void removeKey(const DynamicType& key);                      // del dict[key]
  
  // Set operations
  void add(const DynamicType& item);                 // set.add(item)
  DynamicType contains(const DynamicType& item) const; // item in set
  void remove(const DynamicType& item);              // set.remove(item)
};

#endif // DYNAMIC_TYPE_HPP