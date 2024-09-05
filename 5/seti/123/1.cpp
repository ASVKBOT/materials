#include <bits/stdc++.h>

using namespace std;

void solve() {
    int n;
    cin >> n;

    bool ok = true;
    for (int i = 0; i < n; ++i) {
        long long x;
        cin >> x;
        if (x % 2) ok = false;
    }
    if (ok) {
        cout << "YES" << endl;
    } else {
        cout << "NO" << endl;
    }
}

int main() {
    ios::sync_with_stdio(NULL), cin.tie(0), cout.tie(0);
    cout.setf(ios::fixed), cout.precision(7);
    
    solve();
    return 0;
}
