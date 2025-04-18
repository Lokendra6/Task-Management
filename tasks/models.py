# Create your models here.

from django.db import models
from users.models import CustomUser

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks')
    deadline = models.DateTimeField()
    completed = models.BooleanField(default=False)
    missed = models.BooleanField(default=False)
    completion_status_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)     