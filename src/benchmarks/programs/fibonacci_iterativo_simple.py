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

n = 10
result = fibonacci_iterativo(n)
print(result)
