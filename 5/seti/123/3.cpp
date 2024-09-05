#include <bits/stdc++.h>

using namespace std;

long long n, k, a, m;

long long lcg(long long e) {
    return (a * e + 11) % m;
}

void solve() {
    cin >> n >> k >> a >> m;

    if (n == 0) {
        cout << 0 << endl;
        return;
    }
    
    long long seed = 0;
    
    int ans = 0;
    long long paid = 0;

    while (n > 0) {
        seed = lcg(seed);
        long long coin = (abs(seed % 3 - 1) * 5 + abs(seed % 3) * 2) % 8;
        ans++;
        paid += coin;
        if (paid >= 3 * k) {
            n -= paid / 3;
            paid %= 3;
        }
        
    }
    cout << ans << endl;
}

int main() {
    ios::sync_with_stdio(NULL), cin.tie(0), cout.tie(0);
    cout.setf(ios::fixed), cout.precision(7);
    
    solve();
    return 0;
}
