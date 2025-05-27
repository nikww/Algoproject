from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# from .views import submit_topic, topic_requests, approve_request, reject_request

urlpatterns = [
    path('', views.index, name='index'),
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('topic/<slug:topic_slug>/', views.topic_detail, name='topic_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='algosite/login.html', next_page = 'index'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page = 'index'), name='logout'),
    path('submit-topic/', views.submit_topic, name='submit_topic'),
    path('topic-requests/', views.topic_requests, name='topic_requests'),
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request')
]