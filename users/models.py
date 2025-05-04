from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """ Кастомная модель пользователя """
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.jpg", blank=True, null=True)
    skills = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    PROFESSION_CHOICES = [
        ('backend', 'Backend-разработчик'),
        ('frontend', 'Frontend-разработчик'),
        ('fullstack', 'Fullstack-разработчик'),
        ('uiux', 'Дизайнер UI/UX'),
        ('pm', 'Менеджер продукта'),
        ('marketing', 'Маркетолог'),
        ('copywriter', 'Копирайтер'),
        ('data_analyst', 'Аналитик данных'),
        ('devops', 'Инженер DevOps'),
        ('qa', 'Тестировщик QA'),
        ('ba', 'Бизнес-аналитик'),
        ('project_manager', 'Проджект-менеджер'),
        ('finance', 'Финансист'),
        ('hr', 'HR-специалист'),
    ]

    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username
