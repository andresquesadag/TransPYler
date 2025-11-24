def fibonacci_recursive(num):
    if num <= 1:
        return num
    return fibonacci_recursive(num - 1) + fibonacci_recursive(num - 2)

def main():
    import sys
    
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n>")
        return 1
    
    try:
        number = int(sys.argv[1])
        if number < 0:
            print("Error: n must be non-negative")
            return 1
    except ValueError:
        print("Error: n must be an integer")
        return 1
    
    result = fibonacci_recursive(number)
    print("result:", result)
    return 0

if __name__ == "__main__":
    main()