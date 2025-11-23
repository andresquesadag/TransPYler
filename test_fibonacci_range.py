"""
Script de prueba para verificar fibonacci recursivo e iterativo del 1 al 50
"""
import time
import sys

# Fibonacci Recursivo
def fibonacci_recursivo(n):
    if n <= 1:
        return n
    return fibonacci_recursivo(n - 1) + fibonacci_recursivo(n - 2)

# Fibonacci Iterativo
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

print("="*80)
print("PRUEBA: FIBONACCI RECURSIVO (n = 1 a 50)")
print("="*80)

timeout_reached = False
for n in range(1, 51):
    start = time.time()
    try:
        result = fibonacci_recursivo(n)
        elapsed = time.time() - start
        
        # Si tarda más de 5 minutos (300 segundos), detenemos
        if elapsed > 300:
            print(f"⏱️  fib_rec({n}) = TIMEOUT (>{elapsed:.2f}s) - Deteniendo prueba")
            timeout_reached = True
            break
        
        # Mostrar advertencia si tarda más de 60 segundos
        if elapsed > 60:
            print(f"⚠️  fib_rec({n}) = {result} (LENTO: {elapsed:.2f}s)")
        elif n <= 10 or n % 5 == 0:  # Mostrar solo algunos valores
            print(f"✅ fib_rec({n}) = {result} ({elapsed:.4f}s)")
    except KeyboardInterrupt:
        print(f"\n⏹️  Prueba interrumpida por el usuario en n={n}")
        timeout_reached = True
        break

if not timeout_reached:
    print(f"✅ Fibonacci recursivo completado hasta n=50")
else:
    print(f"⚠️  Fibonacci recursivo se detuvo antes de n=50")

print("\n" + "="*80)
print("PRUEBA: FIBONACCI ITERATIVO (n = 1 a 50)")
print("="*80)

for n in range(1, 51):
    start = time.time()
    result = fibonacci_iterativo(n)
    elapsed = time.time() - start
    
    if n <= 10 or n % 5 == 0:  # Mostrar solo algunos valores
        print(f"✅ fib_iter({n}) = {result} ({elapsed:.6f}s)")

print(f"✅ Fibonacci iterativo completado hasta n=50")

print("\n" + "="*80)
print("VERIFICACIÓN DE CORRECTITUD")
print("="*80)
print("Comparando resultados de ambos algoritmos para n=1 a 40:")

all_match = True
for n in range(1, 41):
    rec = fibonacci_recursivo(n)
    iter_result = fibonacci_iterativo(n)
    if rec != iter_result:
        print(f"❌ ERROR: fib({n}) - Recursivo={rec}, Iterativo={iter_result}")
        all_match = False

if all_match:
    print("✅ Todos los resultados coinciden (n=1 a 40)")

print("\nMostrando valores finales (41-50) solo con iterativo:")
for n in range(41, 51):
    result = fibonacci_iterativo(n)
    print(f"  fib_iter({n}) = {result}")
