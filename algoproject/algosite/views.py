from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, TopicRequest
from .forms import TopicRequestForm



def index(request):
    topics = Topic.objects.all()
    return render(request, 'algosite/index.html', {
        'topics': topics,
        'show_applications_button': request.user.is_authenticated,
    })


def submit_topic(request):
    if request.user.is_authenticated:
        return redirect('index')
    message = ''
    if request.method == 'POST':
        form = TopicRequestForm(request.POST)
        if form.is_valid():
            form.instance.user = None
            form.instance.approved = False
            form.save()
            message = 'Заявка успешно отправлена!'
        else:
            message = 'Пожалуйста, исправьте ошибки в форме.'
    else:
        form = TopicRequestForm()
    return render(request, 'algosite/submit_topic.html', {'form': form, 'message': message})


# def is_admin(user):
#     return user.is_authenticated and user.is_staff


@login_required
def topic_requests(request):
    requests = TopicRequest.objects.filter(approved=False)
    return render(request, 'algosite/topic_requests.html', {'requests': requests})



@login_required
def approve_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        from django.utils.text import slugify
        Topic.objects.create(
            slug=slugify(topic_request.title),
            title=topic_request.title,
            explanation=topic_request.explanation,
            example_code=topic_request.example_code,
            exercise_render_code=topic_request.exercise_render_code,
            exercise_logic_code=topic_request.exercise_logic_code,
        )
        topic_request.approved = True
        topic_request.save()
        return redirect('topic_requests')

    return render(request, 'algosite/approve_request.html', {'request': topic_request})



@login_required
def reject_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        topic_request.delete()
        return redirect('topic_requests')


    return render(request, 'algosite/reject_request.html', {'request': topic_request})



def topic_detail(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    context = {
        'topic': topic,
    }
    return render(request, 'algosite/detail.html', context)

def delete_topic(request, topic_id):
    if request.user.is_authenticated and request.user.is_staff:
        topic = get_object_or_404(Topic, id= topic_id)
        topic.delete()
    return redirect('index')