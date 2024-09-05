#include <bits/stdc++.h>

using namespace std;

vector <vector <int>> edges;
vector <int> color;
vector <int> top_sort;

bool dfs(int v) {
    color[v] = 1;
    for (int to: edges[v]) {
        if (color[to] == 1) {
            return true;
        }
        if (color[to] == 0) {
            if (dfs(to)) return true;
        }
    }
    top_sort.push_back(v);
    color[v] = 2;
    return false;
}

void solve() {
    int n, m;
    cin >> n >> m;
    
    map <pair <int, int>, bool> has;
    edges.resize(n + 1);
    color.resize(n + 1);

    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        if (has.count({u, v})) continue;
        has[{u, v}] = true;
        edges[u].push_back(v);
    }   

    for (int v = 1; v <= n; ++v) {
        if (!color[v]) {
            if (dfs(v)) {
                cout << "No" << endl;
                return;
            }
        }
    }
    reverse(top_sort.begin(), top_sort.end());
    cout << "Yes" << endl;
    for (int v : top_sort) {
        cout << v << " ";
    }
}

int main() {
    ios::sync_with_stdio(NULL), cin.tie(0), cout.tie(0);
    cout.setf(ios::fixed), cout.precision(7);
    
    solve();
    return 0;
}
