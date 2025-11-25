#include "builtins.hpp"
using namespace std;

DynamicType _fn_fibonacci_iterative(DynamicType num) {
	if (DynamicType((num) <= (DynamicType(1))).toBool())
	{
	    return num;
	}
	DynamicType previous = DynamicType(0);
	DynamicType current = DynamicType(1);
	DynamicType counter = DynamicType(2);
	while (DynamicType((counter) <= (num)).toBool())
	{
	    DynamicType next_val = (previous) + (current);
	    previous = current;
	    current = next_val;
	    counter = (counter) + (DynamicType(1));
	}
	return current;
}

int main() {
  DynamicType number = DynamicType(25);
  DynamicType result = _fn_fibonacci_iterative(number);
  print(DynamicType(std::string("result:")), result);
  return 0;
}