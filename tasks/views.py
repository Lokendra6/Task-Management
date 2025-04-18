from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics

from .models import Task
from .serializers import TaskSerializer
from users.permissions import IsManager
from django.utils import timezone
from django.utils.timezone import now
from users.models import CustomUser
from django.core.mail import send_mail


class TaskListCreateAPIView(APIView):
    """
    GET: List tasks based on user role.
         - Managers see tasks they assigned.
         - Users see tasks assigned to them.
    POST: Allows managers to create new tasks.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Filter tasks based on role
        if user.role == 'manager':
            tasks = Task.objects.filter(assigned_by=user)
        elif user.role == 'user':
            tasks = Task.objects.filter(assigned_to=user)
        else:
            tasks = Task.objects.none()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Only managers are allowed to create tasks
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
    """
    Lists all tasks assigned to the currently authenticated user.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only tasks assigned to the requesting user
        return Task.objects.filter(assigned_to=self.request.user)


class UserTaskUpdateAPIView(generics.UpdateAPIView):
    """
    Allows an authenticated user to update their own task.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow the user to update their own assigned tasks
        return Task.objects.filter(assigned_to=self.request.user)


class TaskUpdateAPIView(APIView):
    """
    PATCH: Updates the completion status of a task.
           Tracks missed deadlines, updates timestamps,
           notifies the manager, and auto-deactivates users
           after 5 missed tasks.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, task_id):
        # Get task that belongs to the user
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

        # Store the original completion status
        original_completed = task.completed

        # Update the 'completed' status from request
        task.completed = request.data.get('completed', task.completed)

        # If the status changed, record the timestamp
        if task.completed != original_completed:
            task.completion_status_updated_at = timezone.now()

        # Deadline handling and missed task detection
        if task.deadline < timezone.now():
            if not task.completed:
                # Task was not completed and deadline is over
                task.missed = True
                self._notify_manager(task)
            elif task.completed and task.completion_status_updated_at > task.deadline:
                # Task was completed late
                task.missed = True
                self._notify_manager(task)

        # Save task changes
        task.save()

        # If user misses 5 tasks, deactivate their account
        missed_count = Task.objects.filter(assigned_to=request.user, missed=True).count()
        if missed_count >= 5:
            request.user.is_active = False
            request.user.save()

        return Response(TaskSerializer(task).data)

    def _notify_manager(self, task):
        """
        Sends an email to the manager if a task is missed.
        """
        manager = task.assigned_by
        send_mail(
            subject='User missed deadline!',
            message=f"{task.assigned_to.username} missed task: {task.title}",
            from_email='noreply@example.com',
            recipient_list=[manager.email],
        )


