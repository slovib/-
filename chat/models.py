# chat/models.py
from django.db import models
from django.contrib.auth import get_user_model
from startup.models import Startup

User = get_user_model()

class Message(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        preview = self.content[:20] if self.content else "Файл"
        return f'{self.user.username} в {self.startup.name}: {preview}'
