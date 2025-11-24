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

DynamicType _fn_main() {
	DynamicType values = DynamicType(std::vector<DynamicType>{DynamicType(1), DynamicType(5), DynamicType(10), DynamicType(15), DynamicType(20), DynamicType(25), DynamicType(30), DynamicType(35), DynamicType(40), DynamicType(45), DynamicType(50)});
	{
	  auto __iter_temp_1 = (values).getList();
	  for (auto number : __iter_temp_1)
	  {
	      DynamicType result = _fn_fibonacci_iterative(number);
	      print(DynamicType(std::string("n:")), number);
	      print(DynamicType(std::string("result:")), result);
	  }
	}
	return DynamicType();
}

int main() {
  if (DynamicType((DynamicType(std::string("__main__"))) == (DynamicType(std::string("__main__")))).toBool())
  {
      _fn_main();
  }
  return 0;
}