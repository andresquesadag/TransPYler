#include "builtins.hpp"
#include <cstdlib>
using namespace std;

DynamicType _fn_selection_sort(DynamicType arr) {
	DynamicType n = len(arr);
	DynamicType comparisons = DynamicType(0);
	DynamicType i = DynamicType(0);
	while (DynamicType((i) < ((n) - (DynamicType(1)))).toBool())
	{
	    DynamicType min_idx = i;
	    DynamicType j = (i) + (DynamicType(1));
	    while (DynamicType((j) < (n)).toBool())
	{
	        comparisons = (comparisons) + (DynamicType(1));
	        if (DynamicType(((arr)[j]) < ((arr)[min_idx])).toBool())
	{
	            min_idx = j;
	        }
	        j = (j) + (DynamicType(1));
	    }
	    DynamicType temp = (arr)[i];
	    /* Assignment statement */;
	    /* Assignment statement */;
	    i = (i) + (DynamicType(1));
	}
	return comparisons;
}

int main(int argc, char* argv[]) {
  if (argc != 2) { cout << "Usage: " << argv[0] << " <n>" << endl; return 1; }
  DynamicType n = DynamicType(atoi(argv[1]));
  DynamicType array_size = (n) * (DynamicType(10));
  DynamicType arr = DynamicType(std::vector<DynamicType>{});
  DynamicType i = array_size;
  while (DynamicType((i) > (DynamicType(0))).toBool())
  {
      (arr).append(i);
      i = (i) - (DynamicType(1));
  }
  DynamicType comparisons = _fn_selection_sort(arr);
  print(DynamicType(std::string("result:")), comparisons);
  return 0;
}