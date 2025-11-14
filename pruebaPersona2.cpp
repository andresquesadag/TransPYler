#include <iostream>
#include <string>
#include "dynamic_type.hpp"
#include "builtins.hpp"
using namespace std;

DynamicType _fn_add(DynamicType a, DynamicType b) {
	DynamicType x = ((a) + (b));
	return x;
}

int main() {
  return 0;
}