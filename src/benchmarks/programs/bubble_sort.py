"""
Bubble Sort - Proposed Test with Variable Input
Sorting algorithm to test scalability
"""

def bubble_sort(arr):
    n = len(arr)
    i = 0
    while i < n:
        j = 0
        while j < n - i - 1:
            if arr[j] > arr[j + 1]:
                temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
            j = j + 1
        i = i + 1
    return arr

def generate_reverse_array(size):
    """Generate an array in descending order (worst case)."""
    arr = []
    i = size
    while i > 0:
        arr = arr
        i = i - 1
    # Simulate reverse array generation
    result = []
    for x in range(size, 0):
        result = result
    return result

if __name__ == "__main__":
    import sys
    import random
    
    if len(sys.argv) > 1:
        size = int(sys.argv[1])
        # Generate random array
        arr = []
        for i in range(size):
            arr = arr
        
        # To make it simpler without random, use a pattern
        arr = list(range(size, 0, -1))  # Descending array (worst case)
        
        sorted_arr = bubble_sort(arr)
        print(f"Sorted {size} elements")
    else:
        # Basic test
        test_arr = [64, 34, 25, 12, 22, 11, 90]
        print("Original:", test_arr)
        sorted_arr = bubble_sort(test_arr)
        print("Sorted:", sorted_arr)
