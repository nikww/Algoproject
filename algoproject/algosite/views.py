import random
from collections import deque
from django.shortcuts import render, redirect
from django.http import Http404

ALGORITHM_TOPICS = {
    'bfs': {
        'title': 'BFS (Поиск в ширину)',
        'explanation': '''
Поиск в ширину (BFS) — это алгоритм обхода графа, который исследует вершины в порядке их расстояния от начальной вершины (по слоям).
Он использует очередь для отслеживания следующего места для посещения.
''',
        'example_code': '''
#include &lt;iostream&gt;
#include &lt;queue&gt;
#include &lt;vector&gt;

using namespace std;

void bfs(int start, const vector&lt;vector&lt;int&gt;&gt;&amp; adj) {
    vector&lt;bool&gt; visited(adj.size(), false);
    queue&lt;int&gt; q;
    visited[start] = true;
    q.push(start);

    while (!q.empty()) {
        int v = q.front();
        q.pop();
        cout &lt;&lt; v &lt;&lt; " ";

        for (int u : adj[v]) {
            if (!visited[u]) {
                visited[u] = true;
                q.push(u);
            }
        }
    }
}

int main() {
    int n = 4; // количество вершин
    vector&lt;vector&lt;int&gt;&gt; adj(n);
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
Нижний общий предок (LCA) двух узлов u и v в дереве — это самый низкий (глубокий) узел, который является предком как u, так и v.
Эта задача используется во многих алгоритмах работы с деревьями для эффективного ответа на запросы о взаимосвязи узлов.
Распространенные методы включают бинарный подъем или обход Эйлера + сегментное дерево.
''',
        'example_code': '''
#include &lt;bits/stdc++.h&gt;
using namespace std;

const int MAX = 1000;
const int LOG = 10;

int up[MAX][LOG]; // up[v][j] — это 2^j-й предок v
int depth[MAX];
vector<int> adj[MAX];

void dfs(int v, int p) {
    up[v][0] = p;
    for (int i = 1; i < LOG; i++) {
        up[v][i] = up[up[v][i-1]][i-1];
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
        if (k &amp; (1 &lt;&lt; i)) {
            a = up[a][i];
        }
    }

    if (a == b) return a;
    for (int i = LOG-1; i &gt;= 0; i--) {
        if (up[a][i] != up[b][i]) {
            a = up[a][i];
            b = up[b][i];
        }
    }

    return up[a][0];
}

int main() {
    int n = 9;
    adj[0] = {1,2};
    adj[1] = {0,3,4};
    adj[2] = {0,5,6};
    adj[3] = {1};
    adj[4] = {1,7,8};
    adj[5] = {2};
    adj[6] = {2};
    adj[7] = {4};
    adj[8] = {4};

    depth[0] = 0;
    dfs(0, -1);

    int a = 7, b = 8;
    cout &lt;&lt; "LCA of " &lt;&lt; a &lt;&lt; " and " &lt;&lt; b &lt;&lt; " is " &lt;&lt; lca(a, b) &lt;&lt; endl;
    return 0;
}
'''
    }
}

def index(request):
    topics = [{'slug': slug, 'title': data['title']} for slug, data in ALGORITHM_TOPICS.items()]
    return render(request, 'algosite/index.html', {'topics': topics})

def generate_random_tree(n):
    edges = []
    for i in range(1, n):
        parent = random.randint(0, i - 1)
        edges.append((parent, i))
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj, edges

LOG = 15

def dfs_lca(v, p, adj, up, depth):
    up[v][0] = p
    for i in range(1, LOG):
        if up[v][i - 1] != -1:
            up[v][i] = up[up[v][i - 1]][i - 1]
        else:
            up[v][i] = -1
    for u in adj[v]:
        if u != p:
            depth[u] = depth[v] + 1
            dfs_lca(u, v, adj, up, depth)

def lca_query(a, b, up, depth):
    if depth[a] < depth[b]:
        a, b = b, a
    diff = depth[a] - depth[b]
    for i in range(LOG):
        if diff & (1 << i):
            a = up[a][i]
    if a == b:
        return a
    for i in reversed(range(LOG)):
        if up[a][i] != -1 and up[a][i] != up[b][i]:
            a = up[a][i]
            b = up[b][i]
    return up[a][0]

def get_levels(adj, root=0):
    n = len(adj)
    levels = [-1]*n
    levels[root] = 0
    queue = deque([root])
    while queue:
        u = queue.popleft()
        for w in adj[u]:
            if levels[w] == -1:
                levels[w] = levels[u] + 1
                queue.append(w)
    return levels

def topic_detail(request, topic_slug):
    topic = ALGORITHM_TOPICS.get(topic_slug)
    if not topic:
        raise Http404("Тема не найдена")

    if topic_slug == 'lca':
        message = ''
        new_task = False

        if request.method == 'POST':
            user_answer = request.POST.get('answer', '').strip()
            try:
                user_answer_int = int(user_answer)
            except ValueError:
                message = 'Пожалуйста, введите корректный номер вершины.'
                user_answer_int = None

            correct_answer = request.session.get('lca_correct')
            if correct_answer is None:
                return redirect('topic_detail', topic_slug='lca')

            if user_answer_int is not None:
                # Строгое сравнение с int
                if user_answer_int == correct_answer:
                    new_task = True
                    message = 'Верно! Сгенерирована новая задача.'
                else:
                    message = 'Неверно, попробуйте ещё раз.'

        # Генерируем задачу при первом заходе или после правильного ответа
        if not request.session.get('lca_correct') or new_task:
            n = random.randint(4, 10)
            adj, edges = generate_random_tree(n)
            up = [[-1]*LOG for _ in range(n)]
            depth = [0]*n
            dfs_lca(0, -1, adj, up, depth)
            v1, v2 = random.sample(range(n), 2)
            correct = lca_query(v1, v2, up, depth)

            request.session['lca_n'] = n
            request.session['lca_adj'] = adj
            request.session['lca_edges'] = edges
            request.session['lca_v1'] = v1
            request.session['lca_v2'] = v2
            request.session['lca_correct'] = correct

            message = 'Решите задачу: найдите LCA для заданных вершин.'
        else:
            adj = request.session.get('lca_adj')
            n = request.session.get('lca_n')
            v1 = request.session.get('lca_v1')
            v2 = request.session.get('lca_v2')
            edges = request.session.get('lca_edges')

        # Получим уровни вершин для вертикальной раскладки
        levels = get_levels(adj, 0)

        context = {
            'topic': topic,
            'exercise': True,
            'v1': v1,
            'v2': v2,
            'message': message,
            'edges': edges,
            'num_vertices': n,
            'levels': levels,
        }
        return render(request, 'algosite/detail.html', context)

    else:
        return render(request, 'algosite/detail.html', {'topic': topic, 'exercise': False})