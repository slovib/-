from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Startup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to="startups/logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Здесь используем auto_now_add
    founder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="founder_of")
    users = models.ManyToManyField(User, related_name='startups', blank=True)

    def __str__(self):
        return self.name

class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    startup = models.ForeignKey(Startup, related_name="vacancies", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    vacancy = models.ForeignKey("Vacancy", on_delete=models.CASCADE)
    resume = models.TextField()  # Или загруженный файл
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.vacancy.title}"




class Invite(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="invites")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invitations")
    token = models.CharField(max_length=50, unique=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.user.username} - {self.role_name} в {self.startup.name}'

