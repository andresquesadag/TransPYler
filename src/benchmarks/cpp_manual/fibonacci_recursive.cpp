#include <iostream>
using namespace std;

long long fibonacci_recursive(int n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
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
    
    long long result = fibonacci_recursive(n);
    cout << "result:" << result << endl;

    return 0;
}