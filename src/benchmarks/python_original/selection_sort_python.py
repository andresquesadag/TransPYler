def selection_sort(arr):
    n = len(arr)
    comparisons = 0
    
    # Selection sort always makes O(n²) comparisons, regardless of order
    i = 0
    while i < n - 1:
        min_idx = i
        j = i + 1
        while j < n:
            comparisons = comparisons + 1
            if arr[j] < arr[min_idx]:
                min_idx = j
            j = j + 1
        
        # Swap elements
        temp = arr[i]
        arr[i] = arr[min_idx]
        arr[min_idx] = temp
        
        i = i + 1
    
    return comparisons

def main():
    import sys
    
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n>")
        return 1
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            print("Error: n must be positive")
            return 1
    except ValueError:
        print("Error: n must be an integer")
        return 1
    
    arr = []
    i = n
    while i > 0:
        arr.append(i)
        i = i - 1
    
    comparisons = selection_sort(arr)
    print("result:", comparisons)
    return 0

if __name__ == "__main__":
    main()