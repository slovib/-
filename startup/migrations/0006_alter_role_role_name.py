# Generated by Django 5.1.7 on 2025-03-26 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('startup', '0005_remove_invite_email_alter_invite_startup_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role_name',
            field=models.CharField(max_length=100),
        ),
    ]
