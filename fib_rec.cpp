#include "builtins.hpp"
using namespace std;

DynamicType _fn_fibonacci_recursive(DynamicType num) {
	if (DynamicType((num) <= (DynamicType(1))).toBool())
	{
	    return num;
	}
	return (_fn_fibonacci_recursive((num) - (DynamicType(1)))) + (_fn_fibonacci_recursive((num) - (DynamicType(2))));
}

int main() {
  DynamicType number = DynamicType(25);
  DynamicType result = _fn_fibonacci_recursive(number);
  print(DynamicType(std::string("result:")), result);
  return 0;
}