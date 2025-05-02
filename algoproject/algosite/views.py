from django.shortcuts import render

ALGORITHM_TOPICS = {
    'bfs': {
        'title': 'BFS (Поиск в ширину)',
        'explanation': '''Поиск в ширину (BFS) – это алгоритм обхода графа, который исследует вершины по уровням от начальной вершины.
Использует очередь для определения порядка обхода.
''',

        'example_code': '''#include <iostream>
#include <queue>
#include <vector>
using namespace std;
void bfs(int start, const vector<vector<int>>& adj) {
    vector<bool> visited(adj.size(), false);
    queue<int> q;
    visited[start] = true;
    q.push(start);
    while (!q.empty()) {
        int v = q.front();
        q.pop();
        cout << v << " ";
        for (int u : adj[v]) {
            if (!visited[u]) {
                visited[u] = true;
                q.push(u);
            }
        }
    }
}


int main() {
    int n = 4; // число вершин
    vector<vector<int>> adj(n);
    adj[0] = {1, 2};
    adj[1] = {2};
    adj[2] = {0, 3};
    adj[3] = {3};
    bfs(2, adj);
    return 0;
}

'''
    },

    'lca': {
        'title': 'LCA (Нижний общий предок)',
        'explanation': '''
Нижний общий предок (LCA) – самый глубокий узел в дереве, являющийся предком двух заданных узлов.
Используется для ответа на запросы о взаимосвязях в дереве. Часто применяются методы бинарного подъема.
''',
        'example_code': '''#include <bits/stdc++.h>
using namespace std;


const int MAX = 1000;
const int LOG = 10;


int up[MAX][LOG]; // up[v][j] – 2^j-й предок v
int depth[MAX];
vector<int> adj[MAX];


void dfs(int v, int p) {
    up[v][0] = p;
    for (int i = 1; i < LOG; i++) {
        up[v][i] = up[up[v][i - 1]][i - 1];
    }

    for (int u : adj[v]) {
        if (u != p) {
            depth[u] = depth[v] + 1;
            dfs(u, v);
        }
    }
}


int lca(int a, int b) {

    if (depth[a] < depth[b]) swap(a, b);


    int k = depth[a] - depth[b];

    for (int i = 0; i < LOG; i++) {

        if (k & (1 << i)) {

            a = up[a][i];

        }

    }


    if (a == b) return a;

    for (int i = LOG - 1; i >= 0; i--) {

        if (up[a][i] != up[b][i]) {

            a = up[a][i];

            b = up[b][i];

        }

    }


    return up[a][0];

}


int main() {

    int n = 9;

    adj[0] = {1, 2};

    adj[1] = {0, 3, 4};

    adj[2] = {0, 5, 6};

    adj[3] = {1};

    adj[4] = {1, 7, 8};

    adj[5] = {2};

    adj[6] = {2};

    adj[7] = {4};

    adj[8] = {4};


    depth[0] = 0;

    dfs(0, -1);


    int a = 7, b = 8;
    cout << "LCA of " << a << " and " << b << " is " << lca(a, b) << endl;
    return 0;
}

'''
    }
}

def index(request):
    topics = [{'slug': slug, 'title': data['title']} for slug, data in ALGORITHM_TOPICS.items()]
    return render(request, 'algosite/index.html', {'topics': topics})


def topic_detail(request, topic_slug):
    topic = ALGORITHM_TOPICS.get(topic_slug)
    return render(request, 'algosite/detail.html', {'topic': topic})