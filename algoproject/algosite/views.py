from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import TopicRequestForm
from .models import Topic, TopicRequest
from .utils import docx_bin_to_html

def submit_topic(request):
    if request.user.is_authenticated:
        return redirect('index')

    message = ''
    if request.method == 'POST':
        form = TopicRequestForm(request.POST, request.FILES)
        if form.is_valid():
            tr = form.save(commit=False)

            explanation_file = request.FILES.get('explanation_file')
            if explanation_file:
                tr.explanation = explanation_file.read()

            example_code_file = request.FILES.get('example_code_file')
            if example_code_file:
                tr.example_code = example_code_file.read()

            tr.user = None
            tr.approved = False
            tr.save()

            message = 'Заявка успешно отправлена!'
            form = TopicRequestForm()  # очистить форму
        else:
            message = 'Пожалуйста, исправьте ошибки в форме.'
    else:
        form = TopicRequestForm()

    return render(request, 'algosite/submit_topic.html', {'form': form, 'message': message})

@login_required
@user_passes_test(lambda u: u.is_staff)
def topic_requests(request):
    requests = TopicRequest.objects.filter(approved=False)

    explanation_html_dict = {}
    example_code_html_dict = {}

    for tr in requests:
        if tr.explanation:
            explanation_html_dict[tr.id] = docx_bin_to_html(tr.explanation)
        if tr.example_code:
            example_code_html_dict[tr.id] = docx_bin_to_html(tr.example_code)

    return render(request, 'algosite/topic_requests.html', {
        'requests': requests,
        'explanation_html_dict': explanation_html_dict,
        'example_code_html_dict': example_code_html_dict,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_request(request, request_id):
    tr = get_object_or_404(TopicRequest, id=request_id)

    explanation_html = docx_bin_to_html(tr.explanation) if tr.explanation else ''
    example_code_html = docx_bin_to_html(tr.example_code) if tr.example_code else ''

    if request.method == 'POST':
        from django.utils.text import slugify
        Topic.objects.create(
            slug=slugify(tr.title),
            title=tr.title,
            explanation=explanation_html,
            example_code=example_code_html,
            exercise_render_code=tr.exercise_render_code,
            exercise_logic_code=tr.exercise_logic_code,
        )
        tr.approved = True
        tr.save()
        return redirect('topic_requests')

    return render(request, 'algosite/approve_request.html', {
        'request': tr,
        'explanation_html': explanation_html,
        'example_code_html': example_code_html,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def reject_request(request, request_id):
    tr = get_object_or_404(TopicRequest, id=request_id)
    if request.method == 'POST':
        tr.delete()
        return redirect('topic_requests')
    return render(request, 'algosite/reject_request.html', {'request': tr})

def topic_detail(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    return render(request, 'algosite/detail.html', {'topic': topic})

def delete_topic(request, topic_id):
    if request.user.is_authenticated and request.user.is_staff:
        topic = get_object_or_404(Topic, id= topic_id)
        topic.delete()
    return redirect('index')

def index(request):
    topics = Topic.objects.all()
    return render(request, 'algosite/index.html', {
        'topics': topics,
        'show_applications_button': request.user.is_authenticated,
    })