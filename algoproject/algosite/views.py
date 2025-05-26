import random
from collections import deque
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify

from .models import Topic, TopicRequest

LOG = 15

def index(request):
    topics = Topic.objects.all()
    context = {'topics': topics}
    return render(request, 'algosite/index.html', context)



def topic_detail(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    context = {
        'topic': topic,
    }
    return render(request, 'algosite/detail.html', context)

def submit_topic(request):
    if request.user.is_authenticated:
        return redirect('index')
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
        return redirect('index')
    return render(request, 'algosite/submit_topic.html')

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
def topic_requests(request):
    requests = TopicRequest.objects.filter(approved=False)
    return render(request, 'algosite/topic_requests.html', {'requests': requests})

@login_required
def approve_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        base_slug = slugify(topic_request.title)
        slug = base_slug
        counter = 1
        while Topic.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        Topic.objects.create(
            slug=slug,
            title=topic_request.title,
            explanation=topic_request.explanation,
            example_code=topic_request.example_code
        )
        topic_request.approved = True
        topic_request.save()
        return redirect('topic_requests')

@login_required
def reject_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        topic_request.delete()
        return redirect('topic_requests')
    return render(request, 'algosite/reject_request.html', {'request': topic_request})

