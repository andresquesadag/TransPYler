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
      const auto &list = std::any_cast<const std::vector<DynamicType>&>(value);
      std::string result = "[";
      for (size_t i = 0; i < list.size(); ++i) {
        if (i > 0) result += ", ";
        result += list[i].toString();
      }
      result += "]";
      return result;
    } else if (type == Type::DICT) {
      const auto &dict = std::any_cast<const std::map<std::string, DynamicType>&>(value);
      std::string result = "{";
      bool first = true;
      for (const auto &kv : dict) {
        if (!first) result += ", ";
        result += "'" + kv.first + "': " + kv.second.toString();
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
    }
  } catch (const std::bad_any_cast&) {
    throw std::runtime_error("Internal error: stored value type differs from enum Type (toBool)");
  }
  return false;
}

DynamicType DynamicType::operator+(const DynamicType &other) const {
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
      default:
        return false;
    }
}

bool DynamicType::operator!=(const DynamicType &other) const {
  return !(*this == other);
}

bool DynamicType::operator<(const DynamicType &other) const {
  if (isNumeric() && other.isNumeric()) {
    return toDouble() < other.toDouble();
  }
  if (type == Type::STRING && other.type == Type::STRING) {
    return toString() < other.toString();
  }
  throw std::runtime_error("Unsupported operand types for <");
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
