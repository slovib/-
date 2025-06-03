from django.db import models
from django.conf import settings
from startup.models import Startup

from django.contrib.auth import get_user_model
User = get_user_model()


class Team(models.Model):
    name = models.CharField(max_length=100)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="teams")
    members = models.ManyToManyField(User, through="TeamMembership")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.startup.name})"

class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_captain = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.team.name} (Captain: {self.is_captain})"

from django.utils import timezone

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)  # ⏰ дедлайн
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')  # 🎯 приоритет
    is_completed = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def is_overdue(self):
        return self.due_date and not self.is_completed and self.due_date < timezone.now()

    def __str__(self):
        return f"{self.title} for {self.team.name}"


class TaskComment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    file = models.FileField(upload_to='task_comments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.author.username} к задаче "{self.task.title}"'


class TaskActivity(models.Model):
    ACTION_CHOICES = [
    ('created', 'Создание'),
    ('completed', 'Завершение'),
    ('reopened', 'Возобновление'),
    ('edited', 'Редактирование'),
    ('commented', 'Комментарий'),
    ('created_subtask', 'Создание подзадачи'),
    ('edited_subtask', 'Редактирование подзадачи'),
    ('deleted_subtask', 'Удаление подзадачи'),
    ('completed_subtask', 'Завершение подзадачи'),
    ('reopened_subtask', 'Возобновление подзадачи'),
]




    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)  # Опционально
    subtask = models.ForeignKey('SubTask', on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')

    class Meta:
        ordering = ['-timestamp']

from django.db import models

class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    description = models.TextField(blank=True)
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="subtasks")
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)  # Добавленное поле для дедлайна

    def __str__(self):
        return f"Подзадача: {self.title}"



