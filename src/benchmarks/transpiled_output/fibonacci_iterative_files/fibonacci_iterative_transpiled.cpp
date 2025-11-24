#include "builtins.hpp"
#include <cstdlib>
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

int main(int argc, char* argv[]) {
  if (argc != 2) { cout << "Usage: " << argv[0] << " <n>" << endl; return 1; }
  DynamicType number = DynamicType(atoi(argv[1]));
  DynamicType result = _fn_fibonacci_iterative(number);
  print(DynamicType(std::string("result:")), result);
  return 0;
}