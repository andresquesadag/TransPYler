#include <iostream>
using namespace std;

int fibonacci(int n) {
    if (n < 0) {
        cout << "Please enter a non-negative integer." << endl;
        return -1;
    } else if (n == 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    }

    int a = 0;
    int b = 1;
    int c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int main() {
    int n;
    cout << "Enter which Fibonacci number to calculate: ";
    cin >> n;
    int result = fibonacci(n);
    if (result != -1) {
        cout << "Fibonacci number " << n << " is " << result << endl;
    }
    return 0;
}
