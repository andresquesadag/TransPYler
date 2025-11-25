def fibonacci_recursive(num):
    if num <= 1:
        return num
    return fibonacci_recursive(num - 1) + fibonacci_recursive(num - 2)

# For TransPYler compatibility - no sys imports
# The number will be replaced by pattern matching during transpilation  
number = 25
result = fibonacci_recursive(number)
print("result:", result)