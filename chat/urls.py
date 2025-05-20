from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('startup/<int:startup_id>/chat/', views.startup_chat, name='startup_chat'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]
