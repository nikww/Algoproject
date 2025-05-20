import random
from collections import deque
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, TopicRequest

LOG = 15

def index(request):
    topics = Topic.objects.all()
    context = {'topics': topics}

    if request.user.is_authenticated:
        context['show_applications_button'] = True
    else:
        context['show_applications_button'] = False
    return render(request, 'algosite/index.html', context)

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

def create_new_task(session):
    n = random.randint(4, 10)
    adj, edges = generate_random_tree(n)
    up = [[-1]*LOG for _ in range(n)]
    depth = [0]*n
    dfs_lca(0, -1, adj, up, depth)
    v1, v2 = random.sample(range(n), 2)
    correct = lca_query(v1, v2, up, depth)

    session['lca_n'] = n
    session['lca_adj'] = adj
    session['lca_edges'] = edges
    session['lca_v1'] = v1
    session['lca_v2'] = v2
    session['lca_correct'] = correct

def topic_detail(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)

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
                if user_answer_int == correct_answer:
                    new_task = True
                    message = 'Верно! Сгенерирована новая задача.'
                else:
                    message = 'Неверно, попробуйте ещё раз.'

        if not request.session.get('lca_correct') or new_task:
            create_new_task(request.session)
            message = message or 'Решите задачу: найдите LCA для заданных вершин.'

        adj = request.session.get('lca_adj')
        n = request.session.get('lca_n')
        v1 = request.session.get('lca_v1')
        v2 = request.session.get('lca_v2')
        edges = request.session.get('lca_edges')
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



def submit_topic(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        explanation = request.POST.get('explanation')
        example_code = request.POST.get('example_code')

        TopicRequest.objects.create(
            title=title,
            explanation=explanation,
            example_code=example_code,
            user=None
        )
        #return redirect('index')
        #return redirect('index')

    return render(request, 'algosite/submit_topic.html')


# def is_admin(user):
#     return user.is_authenticated and user.is_staff

@login_required
#@user_passes_test(is_admin)
def topic_requests(request):
    requests = TopicRequest.objects.filter(approved=False)
    return render(request, 'algosite/topic_request.html', {'requests': requests})

@login_required
#@user_passes_test(is_admin)
def approve_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        from django.utils.text import slugify
        Topic.objects.create(
            slug=slugify(topic_request.title),
            title=topic_request.title,
            explanation=topic_request.explanation,
            example_code=topic_request.example_code,
        )
        topic_request.approved = True
        topic_request.save()
        return redirect('topic_requests')
    return render(request, 'algosite/approve_request.html', {'request': topic_request})

@login_required
#@user_passes_test(is_admin)
def reject_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        topic_request.delete()  # Удаляем заявку
        return redirect('topic_requests')
    return render(request, 'algosite/reject_request.html', {'request': topic_request})
