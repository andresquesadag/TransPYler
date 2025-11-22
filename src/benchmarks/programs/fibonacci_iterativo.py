"""
Fibonacci Iterativo - Versión Python Original
"""

def fibonacci_iterativo(n):
    if n <= 1:
        return n
    
    a = 0
    b = 1
    i = 2
    
    while i <= n:
        temp = a + b
        a = b
        b = temp
        i = i + 1
    
    return b

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        result = fibonacci_iterativo(n)
        print(result)
    else:
        # Basic test
        for i in range(1, 11):
            print(f"fib({i}) = {fibonacci_iterativo(i)}")
