/*
 * Bubble Sort - C++ Optimizado (Escrito a Mano)
 * Versión nativa de C++ para comparación de rendimiento
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>

void bubble_sort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc > 1) {
        int size = std::atoi(argv[1]);
        
        // Generar array descendente (peor caso)
        std::vector<int> arr(size);
        for (int i = 0; i < size; i++) {
            arr[i] = size - i;
        }
        
        bubble_sort(arr);
        std::cout << "Sorted " << size << " elements" << std::endl;
    } else {
        // Test básico
        std::vector<int> test_arr = {64, 34, 25, 12, 22, 11, 90};
        
        std::cout << "Original: ";
        for (int x : test_arr) std::cout << x << " ";
        std::cout << std::endl;
        
        bubble_sort(test_arr);
        
        std::cout << "Sorted: ";
        for (int x : test_arr) std::cout << x << " ";
        std::cout << std::endl;
    }
    
    return 0;
}
