"""
Fibonacci Recursivo - Versión Python Original
"""

def fibonacci_recursivo(n):
    if n <= 1:
        return n
    return fibonacci_recursivo(n - 1) + fibonacci_recursivo(n - 2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        result = fibonacci_recursivo(n)
        print(result)
    else:
        # Test básico
        for i in range(1, 11):
            print(f"fib({i}) = {fibonacci_recursivo(i)}")
