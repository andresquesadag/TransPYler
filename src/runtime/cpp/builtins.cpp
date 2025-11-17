// Copyright (c) 2025 Andres Quesada, David Obando, Randy Aguero
#include "builtins.hpp"
#include <algorithm>


template<typename... Args>
void print(const Args&... args) {
    if constexpr (sizeof...(args) == 0) { // No arguments
        std::cout << std::endl;
    } else {
        bool first = true;
        /*This prints all the arguments, if the argument isn't the first one,
        then it should leave a space before the argument*/
        ((std::cout << (first ? (first = false, "") : " ") << args.toString()), ...);
        std::cout << std::endl;
    }
}

inline DynamicType len(const DynamicType &obj) {
  if (obj.isList()) {
    const std::vector<DynamicType> &list = std::any_cast<const std::vector<DynamicType> &>(obj);
    return DynamicType(static_cast<int>(list.size()));
  }
  if (obj.isString()) {
    return DynamicType(static_cast<int>(obj.toString().length()));
  }
  throw std::runtime_error("len() not supported for this type");
}

inline DynamicType range(int stop) {
  std::vector<DynamicType> result;
  for (int i = 0; i < stop; ++i) {
    result.push_back(DynamicType(i));
  }
  return DynamicType(result);
}

inline DynamicType range(int start, int stop) {
  std::vector<DynamicType> result;
  for (int i = start; i < stop; ++i) {
    result.push_back(DynamicType(i));
  }
  return DynamicType(result);
}

DynamicType range(int start, int stop, int step) {
    std::vector<DynamicType> result;
    if (step > 0) {
        for (int i = start; i < stop; i += step) {
            result.push_back(DynamicType(i));
        }
    } else if (step < 0) {
        for (int i = start; i > stop; i += step) {
            result.push_back(DynamicType(i));
        }
    } else {
        throw std::runtime_error("range() step argument must not be zero");
    }
    return DynamicType(result);
}

DynamicType str(const DynamicType& value) {
    return DynamicType(value.toString());
}

DynamicType int_(const DynamicType& value) {
    return DynamicType(value.toInt());
}

DynamicType float_(const DynamicType& value) {
    return DynamicType(value.toDouble());
}

DynamicType bool_(const DynamicType& value) {
    return DynamicType(value.toBool());
}

DynamicType abs(const DynamicType& value) {
    if (value.isInt()) {
        return DynamicType(std::abs(value.toInt()));
    }
    if (value.isDouble()) {
        return DynamicType(std::abs(value.toDouble()));
    }
    throw std::runtime_error("abs() requires numeric argument");
}

DynamicType min(const DynamicType& a, const DynamicType& b) {
    return (a < b) ? a : b;
}

DynamicType max(const DynamicType& a, const DynamicType& b) {
    return (a > b) ? a : b;
}

DynamicType sum(DynamicType& iterable) {
    if (!iterable.isList()) {
        throw std::runtime_error("sum() requires a list");
    }
    
    const std::vector<DynamicType>& list = iterable.getList();
    DynamicType result(0);
    
    for (const DynamicType& item : list) {
        result = result + item;
    }
    return result;
}

DynamicType type(const DynamicType& value) {
    switch (value.getType()) {
        case DynamicType::Type::NONE:   return DynamicType("<class 'NoneType'>");
        case DynamicType::Type::INT:    return DynamicType("<class 'int'>");
        case DynamicType::Type::DOUBLE: return DynamicType("<class 'float'>");
        case DynamicType::Type::STRING: return DynamicType("<class 'str'>");
        case DynamicType::Type::BOOL:   return DynamicType("<class 'bool'>");
        case DynamicType::Type::LIST:   return DynamicType("<class 'list'>");
        case DynamicType::Type::DICT:   return DynamicType("<class 'dict'>");
        default: return DynamicType("<class 'unknown'>");
    }
}

DynamicType input(const std::string& prompt) {
    if (!prompt.empty()) {
        std::cout << prompt;
    }
    std::string line;
    std::getline(std::cin, line);
    return DynamicType(line);
}

DynamicType input() {
    return input("");
}
