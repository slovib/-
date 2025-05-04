from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("team/create/<int:startup_id>/", views.create_team, name="create_team"),
    path("team/<int:team_id>/delete/", views.delete_team, name="delete_team"),
    path("team/<int:team_id>/add-member/", views.add_member, name="add_member"),
    path("team/<int:team_id>/remove-member/<int:user_id>/", views.remove_member, name="remove_member"),
    path("team/<int:team_id>/leave/", views.leave_team, name="leave_team"),

    path("task/create/<int:team_id>/", views.create_task, name="create_task"),
    path("task/<int:task_id>/edit/", views.edit_task, name="edit_task"),
    path("task/<int:task_id>/complete-toggle/", views.toggle_task_complete, name="toggle_task_complete"),
    path("task/<int:task_id>/delete/", views.delete_task, name="delete_task"),

    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('task/<int:task_id>/', views.task_detail, name="task_detail"),
    path('subtask/<int:subtask_id>/toggle/', views.toggle_subtask_complete, name='toggle_subtask'),
    path("subtask/<int:subtask_id>/edit/", views.edit_subtask, name="edit_subtask"),
    path("subtask/<int:subtask_id>/delete/", views.delete_subtask, name="delete_subtask"),

    path('task/<int:task_id>/clear_activity/', views.clear_activity, name='clear_activity'),

    path('task/<int:task_id>/archive/', views.archive_task, name='archive_task'),
    path('team/<int:team_id>/archived/', views.archived_tasks, name='archived_tasks'),
    path('task/<int:task_id>/unarchive/', views.unarchive_task, name='unarchive_task'),
    path('team/<int:team_id>/archive_completed/', views.archive_completed_tasks, name='archive_completed'),


]
