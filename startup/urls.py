# startup/urls.py
from django.urls import path
from . import views

app_name = 'startup'

urlpatterns = [
    path('create/', views.create_startup, name='create_startup'),
    path('assign_role/<int:startup_id>/', views.assign_role, name='assign_role'),
    path('list/', views.startup_list, name='startup_list'),
    path('detail/<int:startup_id>/', views.startup_detail, name='startup_detail'),  # Исправляем на startup_id
    path('edit/<int:startup_id>/', views.edit_startup, name='edit_startup'),  # Исправляем на startup_id
    path('startup/<int:startup_id>/delete/', views.delete_startup, name='delete_startup'),
    path('add_user/<int:start_id>/', views.add_user_to_startup, name='add_user_to_startup'),
    path('search_users/<int:startup_id>/', views.search_users, name='search_users'),
    path('invite_user/<int:user_id>/<int:startup_id>/', views.invite_user, name='invite_user'),
    path('accept_invite/<str:token>/', views.accept_invite, name='accept_invite'),
    path('remove_role/<int:role_id>/', views.remove_role, name='remove_role'),
    path('startup/<int:startup_id>/remove_role/<int:role_id>/', views.remove_role, name='remove_role'),
    path('autocomplete-profession/', views.autocomplete_profession, name='autocomplete_profession'),
    path('startup/<int:startup_id>/remove-user/<int:user_id>/', views.remove_user_from_startup, name='remove_user_from_startup'),
]
