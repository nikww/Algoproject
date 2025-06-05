from io import BytesIO

import mammoth
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
        form = TopicRequestForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)

            explanation_file = request.FILES.get('explanation_file')
            if explanation_file and explanation_file.name.endswith('.docx'):
                obj.explanation = explanation_file.read()

            example_code_file = request.FILES.get('example_code_file')
            if example_code_file and example_code_file.name.endswith('.docx'):
                obj.example_code = example_code_file.read()

            obj.user = None
            obj.approved = False
            obj.save()
            message = 'Заявка успешно отправлена!'
            form = TopicRequestForm()
        else:
            message = 'Пожалуйста, исправьте ошибки в форме.'
    else:
        form = TopicRequestForm()

    return render(request, 'algosite/submit_topic.html', {'form': form, 'message': message})

def topic_detail(request, topic_slug):
    topic = get_object_or_404(TopicRequest, slug=topic_slug)

    context = {
        'topic': topic,
        'explanation_blob': topic.explanation,
        'example_code_blob': topic.example_code,
    }
    return render(request, 'algosite/detail.html', context)


# def is_admin(user):
#     return user.is_authenticated and user.is_staff

@login_required
def topic_requests(request):
    topic_requests_list = TopicRequest.objects.filter(approved=False)

    explanation_html_dict = {}
    example_code_html_dict = {}

    for topic_request in topic_requests_list:
        if topic_request.explanation:
            # Создаем объект BytesIO из бинарных данных
            docx_file = BytesIO(topic_request.explanation)
            result = mammoth.convert_to_html(docx_file)
            explanation_html_dict[topic_request.id] = result.value

        if topic_request.example_code:
            # Аналогично для example_code
            docx_file = BytesIO(topic_request.example_code)
            result = mammoth.convert_to_html(docx_file)
            example_code_html_dict[topic_request.id] = result.value

    return render(request, 'algosite/topic_requests.html', {
        'requests': topic_requests_list,
        'explanation_html_dict': explanation_html_dict,
        'example_code_html_dict': example_code_html_dict,
    })

@login_required
def approve_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)

    explanation_html = ""
    example_code_html = ""

    if topic_request.explanation:
        docx_file = BytesIO(topic_request.explanation)
        result = mammoth.convert_to_html(docx_file)
        explanation_html = result.value

    if topic_request.example_code:
        docx_file = BytesIO(topic_request.example_code)
        result = mammoth.convert_to_html(docx_file)
        example_code_html = result.value

    if request.method == 'POST':
        from django.utils.text import slugify
        Topic.objects.create(
            slug=slugify(topic_request.title),
            title=topic_request.title,
            explanation=explanation_html,
            example_code=example_code_html,
            exercise_render_code=topic_request.exercise_render_code,
            exercise_logic_code=topic_request.exercise_logic_code,
        )
        topic_request.approved = True
        topic_request.save()
        return redirect('topic_requests')

    return render(request, 'algosite/approve_request.html', {
        'request': topic_request,
        'explanation_html': explanation_html,
        'example_code_html': example_code_html,
    })






@login_required
def reject_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        topic_request.delete()
        return redirect('topic_requests')


    return render(request, 'algosite/reject_request.html', {'request': topic_request})

def delete_topic(request, topic_id):
    if request.user.is_authenticated and request.user.is_staff:
        topic = get_object_or_404(Topic, id= topic_id)
        topic.delete()
    return redirect('index')