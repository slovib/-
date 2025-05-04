from django.db import models
from django.conf import settings
from startup.models import Startup

class News(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="news")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Сортировка по дате публикации

    def __str__(self):
        return self.title
