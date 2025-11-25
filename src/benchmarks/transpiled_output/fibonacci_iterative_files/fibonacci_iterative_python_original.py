def fibonacci_iterative(num):
    if num <= 1:
        return num
    
    previous = 0
    current = 1
    counter = 2
    while counter <= num:
        next_val = previous + current
        previous = current
        current = next_val
        counter = counter + 1
    return current

# For TransPYler compatibility - no sys imports
# The number will be replaced by pattern matching during transpilation
import sys
if len(sys.argv) != 2:
    print('Usage: python', sys.argv[0], '<n>')
    sys.exit(1)
number = int(sys.argv[1])
result = fibonacci_iterative(number)
print("result:", result)