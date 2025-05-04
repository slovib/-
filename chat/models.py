# chat/models.py
from django.db import models
from django.conf import settings
from startup.models import Startup

class Message(models.Model):
    startup = models.ForeignKey(Startup, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username} on {self.created_at}"

    class Meta:
        ordering = ['created_at']
