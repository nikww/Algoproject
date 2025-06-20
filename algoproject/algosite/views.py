
from .utils import docx_bin_to_html
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, TopicRequest
from .forms import TopicRequestForm


def submit_topic(request):
    if request.user.is_authenticated:
        return redirect('index')

    message = ''
    if request.method == 'POST':
        form = TopicRequestForm(request.POST, request.FILES)
        file_errors = []

        explanation_file = request.FILES.get('explanation_file')
        if explanation_file and not explanation_file.name.endswith('.docx'):
            file_errors.append('Файл объяснения должен быть в формате .docx')

        example_code_file = request.FILES.get('example_code_file')
        if example_code_file and not example_code_file.name.endswith('.docx'):
            file_errors.append('Файл с примером кода должен быть в формате .docx')

        if file_errors:
            for error in file_errors:
                form.add_error(None, error)
            message = 'Пожалуйста, исправьте ошибки в форме.'
        elif form.is_valid():
            obj = form.save(commit=False)

            if explanation_file:
                obj.explanation = docx_bin_to_html(explanation_file.read())

            if example_code_file:
                obj.example_code = docx_bin_to_html(example_code_file.read())

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
        'topic': topic
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
            explanation_html_dict[topic_request.id] = topic_request.explanation

        if topic_request.example_code:
            example_code_html_dict[topic_request.id] = topic_request.example_code

    return render(request, 'algosite/topic_requests.html', {
        'requests': topic_requests_list,
        'explanation_html_dict': explanation_html_dict,
        'example_code_html_dict': example_code_html_dict,
    })

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




@login_required
def reject_request(request, request_id):
    topic_request = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        topic_request.delete()
    return redirect('topic_requests')


def delete_topic(request, topic_id):
    if request.user.is_authenticated and request.user.is_staff:
        topic = get_object_or_404(Topic, id= topic_id)
        topic.delete()
    return redirect('index')
#Ден доделай
def index(request):
    topics = Topic.objects.all()
    return render(request, 'algosite/index.html', {
        'topics': topics,
        'show_applications_button': request.user.is_authenticated,
    })