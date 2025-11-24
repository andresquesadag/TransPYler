// Copyright (c) 2025 Andres Quesada, David Obando, Randy Aguero
#include "DynamicType.hpp"

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
    } else if (type == Type::SET) {
      const std::set<DynamicType> &set = std::any_cast<const std::set<DynamicType>&>(value);
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
      return !std::any_cast<const std::set<DynamicType>&>(value).empty();
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
  if(type != Type::DICT){
    throw std::runtime_error("Type is not a dict");
  }
  try{
    return std::any_cast<const std::map<std::string, DynamicType>&>(value);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (getDict const)");
  }
}

std::set<DynamicType>& DynamicType::getSet() {
  if(type != Type::SET){
    throw std::runtime_error("Type is not a set");
  }
  try{
    return std::any_cast<std::set<DynamicType>&>(value);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (getSet)");
  }
}

const std::set<DynamicType>& DynamicType::getSet() const {
  if(type != Type::SET){
    throw std::runtime_error("Type is not a set");
  }
  try{
    return std::any_cast<const std::set<DynamicType>&>(value);
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Stored value is not an enum Type (getSet const)");
  }
}

// List manipulation methods
void DynamicType::append(const DynamicType &item) {
    if (type != Type::LIST) {
        throw std::runtime_error("Cannot call append on non-list type");
    }
    try {
        std::vector<DynamicType> &list = std::any_cast<std::vector<DynamicType>&>(value);
        list.push_back(item);
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a vector");
    }
}

DynamicType DynamicType::sublist(const DynamicType &start, const DynamicType &end) const {
    if (type != Type::LIST) {
        throw std::runtime_error("Cannot call sublist on non-list type");
    }
    try {
        const std::vector<DynamicType> &list = std::any_cast<const std::vector<DynamicType>&>(value);
        int startIdx = start.toInt();
        int endIdx = end.toInt();
        
        // Handle negative indices
        if (startIdx < 0) startIdx += list.size();
        if (endIdx < 0) endIdx += list.size();
        
        // Bounds checking
        if (startIdx < 0 || startIdx > (int)list.size()) {
            throw std::runtime_error("Start index out of range");
        }
        if (endIdx < 0 || endIdx > (int)list.size()) {
            throw std::runtime_error("End index out of range");
        }
        if (startIdx > endIdx) {
            throw std::runtime_error("Start index must be <= end index");
        }
        
        std::vector<DynamicType> subvec(list.begin() + startIdx, list.begin() + endIdx);
        return DynamicType(subvec);
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a vector");
    }
}

void DynamicType::removeAt(const DynamicType &index) {
    if (type != Type::LIST) {
        throw std::runtime_error("Cannot call removeAt on non-list type");
    }
    try {
        std::vector<DynamicType> &list = std::any_cast<std::vector<DynamicType>&>(value);
        int idx = index.toInt();
        
        // Handle negative indices
        if (idx < 0) idx += list.size();
        
        // Bounds checking
        if (idx < 0 || idx >= (int)list.size()) {
            throw std::runtime_error("Index out of range");
        }
        
        list.erase(list.begin() + idx);
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a vector");
    }
}

// Dictionary manipulation methods
void DynamicType::set(const DynamicType &key, const DynamicType &val) {
    if (type != Type::DICT) {
        throw std::runtime_error("Cannot call set on non-dict type");
    }
    try {
        std::map<std::string, DynamicType> &dict = std::any_cast<std::map<std::string, DynamicType>&>(value);
        dict[key.toString()] = val;
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a map");
    }
}

DynamicType DynamicType::get(const DynamicType &key) const {
    if (type != Type::DICT) {
        throw std::runtime_error("Cannot call get on non-dict type");
    }
    try {
        const std::map<std::string, DynamicType> &dict = std::any_cast<const std::map<std::string, DynamicType>&>(value);
        std::string keyStr = key.toString();
        auto it = dict.find(keyStr);
        if (it == dict.end()) {
            return DynamicType();  // Return None/null when key not found (Python behavior)
        }
        return it->second;
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a map");
    }
}

void DynamicType::removeKey(const DynamicType &key) {
    if (type != Type::DICT) {
        throw std::runtime_error("Cannot call removeKey on non-dict type");
    }
    try {
        std::map<std::string, DynamicType> &dict = std::any_cast<std::map<std::string, DynamicType>&>(value);
        std::string keyStr = key.toString();
        auto it = dict.find(keyStr);
        if (it == dict.end()) {
            throw std::runtime_error("Key not found: " + keyStr);
        }
        dict.erase(it);
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a map");
    }
}

// Set manipulation methods
void DynamicType::add(const DynamicType &item) {
    if (type != Type::SET) {
        throw std::runtime_error("Cannot call add on non-set type");
    }
    try {
        std::set<DynamicType> &set = std::any_cast<std::set<DynamicType>&>(value);
        set.insert(item);
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a set");
    }
}

DynamicType DynamicType::contains(const DynamicType &item) const {
    if (type != Type::SET) {
        throw std::runtime_error("Cannot call contains on non-set type");
    }
    try {
        const std::set<DynamicType> &set = std::any_cast<const std::set<DynamicType>&>(value);
        return DynamicType(set.find(item) != set.end());
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a set");
    }
}

void DynamicType::remove(const DynamicType &item) {
    if (type != Type::SET) {
        throw std::runtime_error("Cannot call remove on non-set type");
    }
    try {
        std::set<DynamicType> &set = std::any_cast<std::set<DynamicType>&>(value);
        auto it = set.find(item);
        if (it == set.end()) {
            throw std::runtime_error("Item not found in set");
        }
        set.erase(it);
    } catch (const std::bad_any_cast&) {
        throw std::runtime_error("Internal error: stored value is not a set");
    }
}
