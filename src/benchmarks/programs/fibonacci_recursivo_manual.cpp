/*
 * Fibonacci Recursivo - C++ Optimizado (Escrito a Mano)
 * Versión nativa de C++ para comparación de rendimiento
 */

#include <iostream>
#include <cstdlib>

long long fibonacci_recursivo(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci_recursivo(n - 1) + fibonacci_recursivo(n - 2);
}

int main(int argc, char* argv[]) {
    if (argc > 1) {
        int n = std::atoi(argv[1]);
        long long result = fibonacci_recursivo(n);
        std::cout << result << std::endl;
    } else {
        // Test básico
        for (int i = 1; i <= 10; i++) {
            std::cout << "fib(" << i << ") = " << fibonacci_recursivo(i) << std::endl;
        }
    }
    return 0;
}
