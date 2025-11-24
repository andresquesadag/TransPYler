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
    
    result = fibonacci_iterative(number)
    print("result:", result)
    return 0

if __name__ == "__main__":
    main()