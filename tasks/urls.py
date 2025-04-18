# tasks/urls.py

from django.urls import path
from .views import TaskListCreateAPIView,TaskUpdateAPIView,UserTaskUpdateAPIView,UserTaskListAPIView

urlpatterns = [
    # List all tasks (GET) or create a new one (POST)
    path('tasks/', TaskListCreateAPIView.as_view(), name='task-list-create'),
    
    path('my-tasks/', UserTaskListAPIView.as_view(), name='user-task-list'),
    
    path('my-tasks/<int:pk>/update/', UserTaskUpdateAPIView.as_view(), name='user-task-update'),
    
    path('tasks/<int:task_id>/update/', TaskUpdateAPIView.as_view()),

    
]
