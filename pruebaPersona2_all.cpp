#include <iostream>
#include <string>
#include "dynamic_type.hpp"
#include "builtins.hpp"
using namespace std;

DynamicType _fn_add(DynamicType a, DynamicType b) {
	DynamicType x = ((a) + (b));
	return x;
}

DynamicType _fn_power(DynamicType a, DynamicType b) {
	DynamicType res = builtins::pow(a, b);
	return res;
}

DynamicType _fn_unary_test(DynamicType a) {
	DynamicType b = (DynamicType(0) - (a));
	return b;
}

DynamicType _fn_call_test() {
	return _fn_add(DynamicType(), DynamicType());
}

int main() {
  DynamicType g = DynamicType();
  g = ((g) + (DynamicType()));
  return 0;
}