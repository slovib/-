# Миграция для создания поля created_at
# Пример миграции в файле startup/0002_startup_created_at.py

from django.db import migrations, models
from django.utils import timezone

def set_default_created_at(apps, schema_editor):
    Startup = apps.get_model('startup', 'Startup')
    for startup in Startup.objects.all():
        if startup.created_at is None:
            startup.created_at = startup.created_at or timezone.now()  # Устанавливаем текущее время
            startup.save()

class Migration(migrations.Migration):

    dependencies = [
        ('startup', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='startup',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.RunPython(set_default_created_at),
    ]
