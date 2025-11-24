#include "builtins.hpp"
using namespace std;

DynamicType _fn_fibonacci_iterativo(DynamicType num) {
	if (DynamicType((num) <= (DynamicType(1))).toBool())
	{
	    return num;
	}
	DynamicType anterior = DynamicType(0);
	DynamicType actual = DynamicType(1);
	DynamicType contador = DynamicType(2);
	while (DynamicType((contador) <= (num)).toBool())
	{
	    DynamicType siguiente = (anterior) + (actual);
	    anterior = actual;
	    actual = siguiente;
	    contador = (contador) + (DynamicType(1));
	}
	return actual;
}

DynamicType _fn_main() {
	print(DynamicType(std::string("Fibonacci Iterativo")));
	DynamicType valores = DynamicType(std::vector<DynamicType>{DynamicType(1), DynamicType(5), DynamicType(10), DynamicType(15), DynamicType(20), DynamicType(25), DynamicType(30), DynamicType(35), DynamicType(40), DynamicType(45), DynamicType(50)});
	{
	  auto __iter_temp_1 = (valores).getList();
	  for (auto numero : __iter_temp_1)
	  {
	      DynamicType resultado = _fn_fibonacci_iterativo(numero);
	      print(DynamicType(std::string("n:")), numero);
	      print(DynamicType(std::string("resultado:")), resultado);
	  }
	}
	return DynamicType();
}

int main() {
  _fn_main();
  return 0;
}