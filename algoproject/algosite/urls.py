from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('topic/<slug:topic_slug>/', views.topic_detail, name='topic_detail'),
]