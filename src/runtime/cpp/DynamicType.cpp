// Copyright (c) 2025 Andres Quesada, David Obando, Randy Aguero
#include "DynamicType.hpp"


namespace std {
  size_t hash<DynamicType>::operator()(const DynamicType& value) const {
    size_t hashValue = 0;
    
    switch (value.getType()) {
      case DynamicType::Type::NONE:
        // None type always hashes to 0
        hashValue = 0;
        break;
          
      case DynamicType::Type::INT:
        hashValue = std::hash<int>{}(value.toInt());
        break;
          
      case DynamicType::Type::DOUBLE:
        hashValue = std::hash<double>{}(value.toDouble());
        break;
          
      case DynamicType::Type::STRING:
        hashValue = std::hash<std::string>{}(value.toString());
        break;
          
      case DynamicType::Type::BOOL:
        hashValue = std::hash<bool>{}(value.toBool());
        break;
          
      default:
        // For complex types (LIST, DICT, SET), use string representation
        // Note: This is slower but ensures all types are hashable
        hashValue = std::hash<std::string>{}(value.toString());
        break;
    }
    
    return hashValue;
  }
}


int DynamicType::toInt() const {
  try {
    if (type == Type::INT) {
      return std::any_cast<int>(value);
    } else if (type == Type::DOUBLE) {
      return static_cast<int>(std::any_cast<double>(value));
    } else if (type == Type::BOOL) {
      return std::any_cast<bool>(value) ? 1 : 0;
    } else if (type == Type::STRING) {
      return std::stoi(std::any_cast<std::string>(value));
    }
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value has unexpected type");
  } catch (const std::invalid_argument&) {
    throw std::runtime_error("Cannot convert string to int (invalid argument)");
  } catch (const std::out_of_range&) {
    throw std::runtime_error("Cannot convert string to int (out of range)");
  }

  throw std::runtime_error("Cannot convert to int");
}

double DynamicType::toDouble() const {
  try {
    if (type == Type::DOUBLE) {
      return std::any_cast<double>(value);
    } else if (type == Type::INT) {
      return static_cast<double>(std::any_cast<int>(value));
    } else if (type == Type::BOOL) {
      return std::any_cast<bool>(value) ? 1.0 : 0.0;
    } else if (type == Type::STRING) {
      try {
        return std::stod(std::any_cast<const std::string&>(value));
      } catch (const std::invalid_argument&) {
        throw std::runtime_error("Cannot convert string to double (invalid argument)");
      } catch (const std::out_of_range&) {
        throw std::runtime_error("Cannot convert string to double (out of range)");
      }
    }
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Internal error: stored value type differs from enum Type (toDouble)");
  }
  throw std::runtime_error("Cannot convert to double");
}

std::string DynamicType::toString() const {
  try {
    if (type == Type::STRING) {
      return std::any_cast<const std::string&>(value);
    } else if (type == Type::INT) {
      return std::to_string(std::any_cast<int>(value));
    } else if (type == Type::DOUBLE) {
      return std::to_string(std::any_cast<double>(value));
    } else if (type == Type::BOOL) {
      return std::any_cast<bool>(value) ? "True" : "False";
    } else if (type == Type::NONE) {
      return "None";
    } else if (type == Type::LIST) {
      const std::vector<DynamicType> &list = std::any_cast<const std::vector<DynamicType>&>(value);
      std::string result = "[";
      for (size_t i = 0; i < list.size(); ++i) {
        if (i > 0) result += ", ";
        result += list[i].toString();
      }
      result += "]";
      return result;
    } else if (type == Type::DICT) {
      const std::map<std::string, DynamicType> &dict = std::any_cast<const std::map<std::string, DynamicType>&>(value);
      std::string result = "{";
      bool first = true;
      for (const std::pair<const std::string, DynamicType> &kv : dict) {
        if (!first) result += ", ";
        result += "'" + kv.first + "': " + kv.second.toString();
        first = false;
      }
      result += "}";
      return result;
    } else if(type == Type::SET) {
      const std::unordered_set<DynamicType> &set = std::any_cast<const std::unordered_set<DynamicType>&>(value);
      std::string result = "{";
      bool first = true;
      for (const DynamicType &item : set) {
        if (!first) result += ", ";
        result += item.toString();
        first = false;
      }
      result += "}";
      return result;
    }

  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Internal error: stored value type differs from enum Type (toString)");
  }
  return "Unknown";
}

bool DynamicType::toBool() const {
  try {
    if (type == Type::BOOL) {
      return std::any_cast<bool>(value);
    } else if (type == Type::NONE) {
      return false;
    } else if (type == Type::INT) {
      return std::any_cast<int>(value) != 0;
    } else if (type == Type::DOUBLE) {
      return std::any_cast<double>(value) != 0.0;
    } else if (type == Type::STRING) {
      return !std::any_cast<const std::string&>(value).empty();
    } else if (type == Type::LIST) {
      return !std::any_cast<const std::vector<DynamicType>&>(value).empty();
    } else if (type == Type::DICT) {
      return !std::any_cast<const std::map<std::string, DynamicType>&>(value).empty();
    } else if (type == Type::SET) {
      return !std::any_cast<const std::unordered_set<DynamicType>&>(value).empty();
    }
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Internal error: stored value type differs from enum Type (toBool)");
  }
  return false;
}

DynamicType DynamicType::operator+(const DynamicType &other) const {
  // List concatenation
  if (type == Type::LIST && other.type == Type::LIST) {
    auto left = std::any_cast<std::vector<DynamicType>>(value);
    auto right = std::any_cast<std::vector<DynamicType>>(other.value);
    
    // Concatenate vectors
    std::vector<DynamicType> result = left;
    result.insert(result.end(), right.begin(), right.end());
    
    return DynamicType(result);
  }

  // String concat
  if (type == Type::STRING || other.type == Type::STRING) {
    return DynamicType(toString() + other.toString());
  }

  // Numeric addition
  if (type == Type::DOUBLE || other.type == Type::DOUBLE) {
    return DynamicType(toDouble() + other.toDouble());
  }
  if (type == Type::INT && other.type == Type::INT) {
    return DynamicType(toInt() + other.toInt());
  }
  throw std::runtime_error("Unsupported operand types for +");
}

DynamicType DynamicType::operator-(const DynamicType &other) const {
  if (type == Type::DOUBLE || other.type == Type::DOUBLE) {
    return DynamicType(toDouble() - other.toDouble());
  }
  if (type == Type::INT && other.type == Type::INT) {
    return DynamicType(toInt() - other.toInt());
  }
  throw std::runtime_error("Unsupported operand types for -");
}


DynamicType DynamicType::operator*(const DynamicType &other) const {
  // String repetition
  if (type == Type::STRING && other.isNumeric()) {
    std::string result;
    int count = other.toInt();
    for (int i = 0; i < count; ++i)
    {
      result += std::any_cast<std::string>(value);
    }
    return DynamicType(result);
  }

  // Numeric multiplication
  if (type == Type::DOUBLE || other.type == Type::DOUBLE) {
    return DynamicType(toDouble() * other.toDouble());
  }
  return DynamicType(toInt() * other.toInt());
}

DynamicType DynamicType::operator/(const DynamicType &other) const {
  double divisor = other.toDouble();
  if (divisor == 0.0) {
    throw std::runtime_error("Division by zero");
  }
  return DynamicType(toDouble() / divisor);
}

DynamicType DynamicType::operator%(const DynamicType &other) const {
  int divisor = other.toInt();
  if (divisor == 0) {
    throw std::runtime_error("Modulo by zero");
  }
  return DynamicType(toInt() % divisor);
}

DynamicType DynamicType::pow(const DynamicType &exponent) const {
  return DynamicType(std::pow(toDouble(), exponent.toDouble()));
}

DynamicType DynamicType::floor_div(const DynamicType &other) const {
  int divisor = other.toInt();
  if (divisor == 0) {
    throw std::runtime_error("Floor division by zero");
  }
  return DynamicType(toInt() / divisor);
}

bool DynamicType::operator==(const DynamicType &other) const {
    if (type != other.type) {
      return false;
    }
    switch (type) {
      case Type::NONE:
        return true;
      case Type::INT:
        return toInt() == other.toInt();
      case Type::DOUBLE:
        return toDouble() == other.toDouble();
      case Type::STRING:
        return toString() == other.toString();
      case Type::BOOL:
        return toBool() == other.toBool();
      case Type::LIST: {
        const auto &list1 = std::any_cast<const std::vector<DynamicType>&>(value);
        const auto &list2 = std::any_cast<const std::vector<DynamicType>&>(other.value);
        return list1 == list2;
      }
      case Type::DICT: {
        const auto &dict1 = std::any_cast<const std::map<std::string, DynamicType>&>(value);
        const auto &dict2 = std::any_cast<const std::map<std::string, DynamicType>&>(other.value);
        return dict1 == dict2;
      }
      case Type::SET: {
        const auto &set1 = std::any_cast<const std::set<DynamicType>&>(value);
        const auto &set2 = std::any_cast<const std::set<DynamicType>&>(other.value);
        return set1 == set2;
      }
      default:
        return false;
    }
}

bool DynamicType::operator!=(const DynamicType &other) const {
  return !(*this == other);
}

bool DynamicType::operator<(const DynamicType &other) const {
  // First compare by type (for mixed type sets)
  if (type != other.type) {
    return static_cast<int>(type) < static_cast<int>(other.type);
  }
  
  // Same types - compare values
  if (isNumeric() && other.isNumeric()) {
    return toDouble() < other.toDouble();
  }
  if (type == Type::STRING && other.type == Type::STRING) {
    return toString() < other.toString();
  }
  if (type == Type::BOOL && other.type == Type::BOOL) {
    return toBool() < other.toBool();
  }
  if (type == Type::NONE && other.type == Type::NONE) {
    return false;  // None == None
  }
  
  // For complex types, compare string representations as fallback
  return toString() < other.toString();
}

bool DynamicType::operator<=(const DynamicType &other) const {
  return *this < other || *this == other;
}

bool DynamicType::operator>(const DynamicType &other) const {
  return !(*this <= other);
}

bool DynamicType::operator>=(const DynamicType &other) const {
  return !(*this < other);
}

DynamicType DynamicType::operator&&(const DynamicType &other) const {
  return DynamicType(toBool() && other.toBool());
}

DynamicType DynamicType::operator||(const DynamicType &other) const {
  return DynamicType(toBool() || other.toBool());
}

DynamicType DynamicType::operator!() const {
  return DynamicType(!toBool());
}

DynamicType DynamicType::operator-() const {
  if (type == Type::INT){
    return DynamicType(-toInt());
  }
  if (type == Type::DOUBLE){
    return DynamicType(-toDouble());
  }
  throw std::runtime_error("Unsupported operand type for unary -");
}

DynamicType DynamicType::operator+() const {
  if (isNumeric()) {
    return *this;
  }
  throw std::runtime_error("Unsupported operand type for unary +");
}

DynamicType &DynamicType::operator[](const size_t index) {
  if(type != Type::LIST){
    throw std::runtime_error("Type is not a list");
  }
  try{
    std::vector<DynamicType> &list = std::any_cast<std::vector<DynamicType> &>(value);
    return list.at(index);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (operator[])");
  }
}

DynamicType &DynamicType::operator[](const std::string &key) {
  if(type != Type::DICT){
    throw std::runtime_error("Type is not a dict");
  }
  try {
    std::map<std::string, DynamicType> &dict = std::any_cast<std::map<std::string, DynamicType> &>(value);
    return dict[key];
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (operator[])");
  }
}

DynamicType &DynamicType::operator[](const DynamicType &key) {
  // If the key is numeric, treat as list index
  if (key.type == Type::INT) {
    return (*this)[static_cast<size_t>(key.toInt())];
  }
  // If the key is string or can be converted to string, treat as dict key
  else {
    return (*this)[key.toString()];
  }
}


std::vector<DynamicType>& DynamicType::getList() {
  if(type != Type::LIST){
    throw std::runtime_error("Type is not a list");
  }
  try{
    return std::any_cast<std::vector<DynamicType>&>(value);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (getList)");
  }
}

const std::vector<DynamicType>& DynamicType::getList() const {
  if(type != Type::LIST){
    throw std::runtime_error("Type is not a list");
  }
  try{
    return std::any_cast<const std::vector<DynamicType>&>(value);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (getList const)");
  }
}

std::map<std::string, DynamicType>& DynamicType::getDict() {
  if(type != Type::DICT){
    throw std::runtime_error("Type is not a dict");
  }
  try{
    return std::any_cast<std::map<std::string, DynamicType>&>(value);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (getDict)");
  }
}

const std::map<std::string, DynamicType>& DynamicType::getDict() const {
  if(type != Type::DICT) {
    throw std::runtime_error("Type is not a dict");
  }
  try{
    return std::any_cast<const std::map<std::string, DynamicType>&>(value);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (getDict const)");
  }
}
