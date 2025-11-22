# Professor's Full Feature Test
# ==============================
# This file demonstrates the TransPYler transpiler capabilities:
# - Basic functions
# - Recursion (Fibonacci)
# - Dynamic typing (variables changing types)
# - Complex data structures (lists, dicts, tuples)
# - For loops with range and iteration
# - While loops with type changes

def hola(a, b):
    return a + b

print(hola(1, 2))

def fib(n):
    if n == 1 or n == 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

print(fib(5))

a = 4
print(a)
b = 5
a = "hola"
b = a + (str(b))
print(b)

a = [1, "hola", {"z": 1, "x": "ECCI"}, [1, 2, 3, 4], (1, 2, 3, 4)]
print(a)
print("Fibonacci")

for i in range(len(a)-1):
    print(a[i])
    
for e in a[3]:
    print(e)
    
a = 5
b = 10
while a < b:
    print(fib(b-5))
    c = b
    b = "hola"
    b = c-2

print("Si printeo mis probabilidades de graduarme suben :)")
