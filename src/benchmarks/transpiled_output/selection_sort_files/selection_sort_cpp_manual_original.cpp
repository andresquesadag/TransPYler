#include <iostream>
#include <vector>
using namespace std;

int selection_sort(vector<int>& arr) {
    int n = arr.size();
    int comparisons = 0;
    
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            comparisons++;
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        // Swap elements
        int temp = arr[i];
        arr[i] = arr[min_idx];
        arr[min_idx] = temp;
    }
    return comparisons;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cout << "Usage: " << argv[0] << " <n>" << endl;
        return 1;
    }
    
    int n = atoi(argv[1]);
    if (n <= 0) {
        cout << "Error: n must be positive" << endl;
        return 1;
    }
    
    // Create array of size n*10 to match Python implementation
    int array_size = n * 10;
    vector<int> arr(array_size);
    for (int i = 0; i < array_size; i++) {
        arr[i] = array_size - i;
    }
    
    int comparisons = selection_sort(arr);
    cout << "result:" << comparisons << endl;
    
    return 0;
}