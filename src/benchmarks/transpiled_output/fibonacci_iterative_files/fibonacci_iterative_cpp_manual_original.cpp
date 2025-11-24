#include <iostream>
using namespace std;

long long fibonacci_iterative(int n) {
    if (n <= 1) return n;
    
    long long a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        long long temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cout << "Usage: " << argv[0] << " <n>" << endl;
        return 1;
    }
    
    int n = atoi(argv[1]);
    if (n < 0) {
        cout << "Error: n must be non-negative" << endl;
        return 1;
    }
    
    long long result = fibonacci_iterative(n);
    cout << "result:" << result << endl;
    
    return 0;
}