def fibonacci_recursive(num):
    if num <= 1:
        return num
    return fibonacci_recursive(num - 1) + fibonacci_recursive(num - 2)

# For TransPYler compatibility - no sys imports
# The number will be replaced by pattern matching during transpilation  
import sys
if len(sys.argv) != 2:
    print('Usage: python', sys.argv[0], '<n>')
    sys.exit(1)
number = int(sys.argv[1])
result = fibonacci_recursive(number)
print("result:", result)