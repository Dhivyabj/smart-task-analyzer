# tasks/urls.py
from django.urls import path
from .views import analyze_tasks, suggest_tasks

urlpatterns = [
    path('tasks/analyze/', analyze_tasks, name='analyze_tasks'),
    path('tasks/suggest/', suggest_tasks, name='suggest_tasks'),
]