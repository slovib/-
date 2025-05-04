# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:startup_id>/chat/', views.startup_chat, name='startup_chat'),
]
