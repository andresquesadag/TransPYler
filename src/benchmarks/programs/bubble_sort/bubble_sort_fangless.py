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

size = 100
arr = []
i = size
while i > 0:
    arr = arr + [i]
    i = i - 1

sorted_arr = bubble_sort(arr)
print(len(sorted_arr))
