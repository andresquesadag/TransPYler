#include "builtins.hpp"

inline void print(const DynamicType &obj) {
  std::cout << obj.toString() << std::endl;
}

inline DynamicType len(const DynamicType &obj) {
  if (obj.isList()) {
    auto &list = std::any_cast<const std::vector<DynamicType> &>(obj);
    return DynamicType(static_cast<int>(list.size()));
  }
  if (obj.isString()) {
    return DynamicType(static_cast<int>(obj.toString().length()));
  }
  throw std::runtime_error("len() not supported for this type");
}

inline DynamicType range(int stop)
{
  std::vector<DynamicType> result;
  for (int i = 0; i < stop; ++i)
  {
    result.push_back(DynamicType(i));
  }
  return DynamicType(result);
}

inline DynamicType range(int start, int stop)
{
  std::vector<DynamicType> result;
  for (int i = start; i < stop; ++i)
  {
    result.push_back(DynamicType(i));
  }
  return DynamicType(result);
}
