#include "builtins.hpp"
#include <cstdlib>
using namespace std;

DynamicType _fn_fibonacci_recursive(DynamicType num) {
	if (DynamicType((num) <= (DynamicType(1))).toBool())
	{
	    return num;
	}
	return (_fn_fibonacci_recursive((num) - (DynamicType(1)))) + (_fn_fibonacci_recursive((num) - (DynamicType(2))));
}

int main(int argc, char* argv[]) {
  if (argc != 2) { cout << "Usage: " << argv[0] << " <n>" << endl; return 1; }
  DynamicType number = DynamicType(atoi(argv[1]));
  DynamicType result = _fn_fibonacci_recursive(number);
  print(DynamicType(std::string("result:")), result);
  return 0;
}