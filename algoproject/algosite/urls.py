from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('topic/<slug:topic_slug>/', views.topic_detail, name='topic_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='algosite/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('applications/', views.applications, name='applications'),
]