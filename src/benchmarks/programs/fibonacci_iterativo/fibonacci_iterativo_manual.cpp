/*
 * Fibonacci Iterativo - C++ Optimizado (Escrito a Mano)
 * Versión nativa de C++ para comparación de rendimiento
 */

#include <iostream>
#include <cstdlib>

long long fibonacci_iterativo(int n) {
    if (n <= 1) {
        return n;
    }
    
    long long a = 0;
    long long b = 1;
    
    for (int i = 2; i <= n; i++) {
        long long temp = a + b;
        a = b;
        b = temp;
    }
    
    return b;
}

int main(int argc, char* argv[]) {
    if (argc > 1) {
        int n = std::atoi(argv[1]);
        long long result = fibonacci_iterativo(n);
        std::cout << result << std::endl;
    } else {
        // Test básico
        for (int i = 1; i <= 10; i++) {
            std::cout << "fib(" << i << ") = " << fibonacci_iterativo(i) << std::endl;
        }
    }
    return 0;
}
