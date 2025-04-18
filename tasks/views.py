from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions,generics

from .models import Task
from .serializers import TaskSerializer
from users.permissions import IsManager
from django.utils import timezone


from django.utils.timezone import now
from users.models import CustomUser
from django.core.mail import send_mail 

class TaskListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Default for all methods

    def get(self, request):
        user = request.user

        if user.role == 'manager':
            tasks = Task.objects.filter(assigned_by=user)
        elif user.role == 'user':
            tasks = Task.objects.filter(assigned_to=user)
        else:
            tasks = Task.objects.none()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'manager':
            return Response(
                {'error': 'Only managers can create tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assigned_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class UserTaskListAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)


# 🔹 PATCH/PUT: Update a specific task assigned to the user
class UserTaskUpdateAPIView(generics.UpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)
    
    
    
class TaskUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
        
        # Store original completed status to compare later
        original_completed = task.completed
        
        # Update the 'completed' status based on user input
        task.completed = request.data.get('completed', task.completed)

        # If the 'completed' status changed, update the timestamp
        if task.completed != original_completed:
            task.completion_status_updated_at = timezone.now()  # Update the timestamp if status changed
        
        # Check if the deadline has passed
        if task.deadline < timezone.now():
            if not task.completed:
                # If task is not completed and deadline is missed, mark as missed
                task.missed = True
                self._notify_manager(task)
            elif task.completed and task.completion_status_updated_at > task.deadline:
                # If task is completed but updated after the deadline, mark as missed
                task.missed = True
                self._notify_manager(task)

        # Save task changes
        task.save()
        
        # Auto deactivate if 5 missed tasks
        missed_count = Task.objects.filter(assigned_to=request.user, missed=True).count()
        if missed_count >= 5:
            request.user.is_active = False
            request.user.save()

        return Response(TaskSerializer(task).data)

    def _notify_manager(self, task):
        manager = task.assigned_by
        send_mail(
            subject='User missed deadline!',
            message=f"{task.assigned_to.username} missed task: {task.title}",
            from_email='noreply@example.com',
            recipient_list=[manager.email],
        )