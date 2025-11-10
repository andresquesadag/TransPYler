// Copyright (c) 2025 Andres Quesada, David Obando, Randy Aguero
#ifndef DYNAMIC_TYPE_HPP
#define DYNAMIC_TYPE_HPP

#include <any>
#include <string>
#include <vector>
#include <map>
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
class DynamicType
{
  public:
    enum class Type
    {
      NONE,
      INT,
      DOUBLE,
      STRING,
      BOOL,
      LIST,
      DICT
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

    // Comparison operators
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

    // Output stream
    friend std::ostream &operator<<(std::ostream &os, const DynamicType &dt) {
      os << dt.toString();
      return os;
    }

    // Collection getters
    std::vector<DynamicType>& getList();
    std::map<std::string, DynamicType>& getDict();
};

#endif // DYNAMIC_TYPE_HPP