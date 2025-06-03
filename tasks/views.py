from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils import timezone

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
import json
from .forms import TaskFilterForm
from .models import TaskActivity, Team, TeamMembership, Task, TaskComment, SubTask
from .forms import TaskForm, TaskFilterForm, TaskCommentForm, SubTaskForm
from startup.models import Startup

# Получаем модель пользователя
User = get_user_model()



# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ==========
def log_activity(task, user, action, comment=None, subtask=None):
    TaskActivity.objects.create(
        task=task,
        user=user,
        action=action,
        comment=comment,
        subtask=subtask
    )



@login_required
def clear_activity(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    team = task.team
    user = request.user

    # Проверка: основатель или капитан команды
    is_founder = team.startup.founder == user
    is_captain = TeamMembership.objects.filter(team=team, user=user, is_captain=True).exists()

    if not (is_founder or is_captain):
        return HttpResponseForbidden("У вас нет прав для очистки истории.")

    if request.method == 'POST':
        TaskActivity.objects.filter(task=task).delete()
        return redirect('tasks:task_detail', task_id=task_id)

    # Можно добавить подтверждение перед удалением
    return redirect('tasks:task_detail', task_id=task_id)




# ========== КОМАНДЫ ==========

@login_required
def create_team(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    if not request.user == startup.founder:
        return HttpResponseForbidden("Вы не основатель стартапа.")

    if request.method == "POST":
        team_name = request.POST.get('name')
        member_ids = request.POST.getlist('members')
        captain_id = request.POST.get('captain')

        if team_name and member_ids and captain_id:
            team = Team.objects.create(name=team_name, startup=startup)

            for uid in member_ids:
                is_captain = str(uid) == captain_id
                TeamMembership.objects.create(
                    user_id=uid,
                    team=team,
                    is_captain=is_captain
                )

            if str(request.user.id) != captain_id and str(request.user.id) not in member_ids:
                TeamMembership.objects.create(user=request.user, team=team, is_captain=True)

            messages.success(request, "Команда успешно создана!")
            return redirect('startup:startup_detail', startup_id=startup.id)

    return render(request, 'tasks/create_team.html', {
        'startup': startup,
        'all_users': startup.users.exclude(id=request.user.id)
    })


@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user != team.startup.founder:
        return HttpResponseForbidden("Только основатель может удалить команду.")
    team.delete()
    messages.success(request, "Команда удалена.")
    return redirect("startup:startup_detail", startup_id=team.startup.id)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import TeamMembership, Role, User

@login_required
def add_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if not is_team_captain_or_founder(request.user, team):
        return HttpResponseForbidden("У вас нет прав для добавления участника.")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role_name = request.POST.get("role_name").strip()
        
        user = get_object_or_404(User, id=user_id)

        # Создаем роль, если её не существует
        role, _ = Role.objects.get_or_create(name=role_name)

        # Проверка на существующее членство
        membership, created = TeamMembership.objects.get_or_create(user=user, team=team)
        
        if not created:
            messages.warning(request, f"{user.username} уже является участником этой команды.")
        else:
            membership.role = role
            membership.save()
            messages.success(request, f"{user.username} добавлен в команду с ролью «{role.name}».")
        
        return redirect("tasks:team_detail", team_id=team.id)

    else:
        all_users = team.startup.users.all()
        current_users = TeamMembership.objects.filter(team=team).values_list('user', flat=True)
        
        return render(request, 'tasks/add_member.html', {
            'team': team,
            'all_users': all_users,
            'current_users': current_users,
        })





@login_required
def remove_member(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(User, id=user_id)
    if not is_team_captain_or_founder(request.user, team):
        return HttpResponseForbidden()

    membership = get_object_or_404(TeamMembership, user=member, team=team)
    membership.delete()
    messages.success(request, f"{member.username} удалён из команды.")
    return redirect("tasks:team_detail", team_id=team.id)


@login_required
def leave_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    membership = TeamMembership.objects.filter(user=request.user, team=team).first()
    if membership:
        membership.delete()
        messages.success(request, "Вы покинули команду.")
    return redirect("startup:startup_detail", startup_id=team.startup.id)


def is_team_captain_or_founder(user, team):
    return user == team.startup.founder or TeamMembership.objects.filter(user=user, team=team, is_captain=True).exists()


# ========== ЗАДАЧИ ==========

@login_required
def create_task(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if not is_team_captain_or_founder(request.user, team):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.team = team
            task.created_by = request.user
            task.save()
            log_activity(task, request.user, 'created')
            messages.success(request, "Задача создана.")
            return redirect("tasks:team_detail", team_id=team.id)
    else:
        form = TaskForm()

    form.fields['assigned_to'].queryset = team.members.all()
    return render(request, "tasks/create_task.html", {"form": form, "team": team})


@login_required
def create_subtask(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    team = task.team
    user = request.user

    # Проверка, является ли пользователь участником команды или основателем
    is_member = TeamMembership.objects.filter(user=user, team=team).exists()
    is_founder = user == team.startup.founder
    if not (is_member or is_founder):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = SubTaskForm(request.POST)
        if form.is_valid():
            subtask = form.save(commit=False)
            subtask.task = task
            subtask.save()

            # Логируем создание подзадачи
            log_activity(task, user, 'created_subtask', subtask=subtask)

            return redirect('tasks:task_detail', task_id=task.id)
    else:
        form = SubTaskForm()

    return render(request, 'tasks/create_subtask.html', {
        'subtask_form': form,
        'task': task
    })


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    team = task.team
    if request.user != task.created_by and not is_team_captain_or_founder(request.user, team):
        return HttpResponseForbidden()

    if request.method == "POST":
        task.title = request.POST.get("title", task.title)
        task.description = request.POST.get("description", task.description)
        assigned_to_id = request.POST.get("assigned_to")
        task.assigned_to = User.objects.filter(id=assigned_to_id).first() if assigned_to_id else None
        task.save()
        log_activity(task, request.user, 'edited')
        messages.success(request, "Задача обновлена.")
        return redirect("tasks:team_detail", team_id=team.id)

    members = team.members.all()
    return render(request, "tasks/edit_task.html", {"task": task, "members": members})


@login_required
def toggle_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user != task.assigned_to and not is_team_captain_or_founder(request.user, task.team):
        return HttpResponseForbidden()

    task.is_completed = not task.is_completed
    task.save()
    log_activity(task, request.user, 'completed' if task.is_completed else 'reopened')
    return redirect("tasks:team_detail", team_id=task.team.id)

@login_required
def toggle_subtask_complete(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    task = subtask.task
    team = task.team

    is_captain = TeamMembership.objects.filter(user=request.user, team=team, is_captain=True).exists()
    is_founder = request.user == team.startup.founder
    is_authorized = request.user == subtask.assigned_to or is_captain or is_founder

    if not is_authorized:
        return HttpResponseForbidden("Нет доступа к этой подзадаче.")

    subtask.is_completed = not subtask.is_completed
    subtask.save()

    action = 'completed_subtask' if subtask.is_completed else 'reopened_subtask'
    log_activity(task, request.user, action, subtask=subtask)

    return redirect("tasks:task_detail", task_id=task.id)


@login_required
def delete_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    task = subtask.task
    team = task.team

    is_captain = TeamMembership.objects.filter(user=request.user, team=team, is_captain=True).exists()
    is_founder = request.user == team.startup.founder
    if not (is_captain or is_founder or request.user == subtask.assigned_to):
        return HttpResponseForbidden()

    subtask.delete()
    log_activity(task, request.user, 'deleted_subtask')
    messages.success(request, "Подзадача удалена.")
    return redirect('tasks:task_detail', task_id=task.id)

@login_required
def edit_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    task = subtask.task
    team = task.team

    is_captain = TeamMembership.objects.filter(user=request.user, team=team, is_captain=True).exists()
    is_founder = request.user == team.startup.founder

    if not (request.user == subtask.assigned_to or is_captain or is_founder):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = SubTaskForm(request.POST, instance=subtask)
        form.fields['assigned_to'].queryset = team.members.all()
        if form.is_valid():
            form.save()
            log_activity(task, request.user, 'edited_subtask', subtask=subtask)
            messages.success(request, "Подзадача обновлена.")
            return redirect('tasks:task_detail', task_id=task.id)
    else:
        form = SubTaskForm(instance=subtask)
        form.fields['assigned_to'].queryset = team.members.all()

    return render(request, "tasks/edit_subtask.html", {"form": form, "task": task, "subtask": subtask})



@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user != task.created_by and not is_team_captain_or_founder(request.user, task.team):
        return HttpResponseForbidden()

    # Сохраняем нужные данные
    task_id = task.id
    team_id = task.team.id
    task_title = task.title

    # Логируем до удаления
    TaskActivity.objects.create(
        task=task,
        user=request.user,
        action='deleted_subtask',  # Если ты добавишь 'deleted' в ACTION_CHOICES — используй 'deleted'
        comment=f'Задача «{task_title}» была удалена.'
    )

    # Удаляем задачу
    task.delete()

    messages.success(request, "Задача удалена.")
    return redirect("tasks:team_detail", team_id=team_id)



@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    membership = TeamMembership.objects.filter(user=request.user, team=team).first()

    if not (membership or request.user == team.startup.founder):
        return HttpResponseForbidden("У вас нет доступа к этой команде.")

    is_founder = request.user == team.startup.founder
    is_captain = membership.is_captain if membership else False
    members = TeamMembership.objects.filter(team=team).select_related("user")
    all_users = team.startup.users.all()
    current_users = User.objects.filter(teammembership__team=team).distinct()
    tasks = team.tasks.filter(is_archived=False).select_related("assigned_to", "created_by")

    form = TaskFilterForm(request.GET, user=request.user, team=team, is_manager=is_founder or is_captain)

    if form.is_valid():
        status = form.cleaned_data.get("status")
        priority = form.cleaned_data.get("priority")
        assigned_to = form.cleaned_data.get("assigned_to")

        if status == "done":
            tasks = tasks.filter(is_completed=True)
        elif status == "active":
            tasks = tasks.filter(is_completed=False)

        if priority:
            tasks = tasks.filter(priority=priority)

        if assigned_to == "me":
            tasks = tasks.filter(assigned_to=request.user)
        elif assigned_to:
            tasks = tasks.filter(assigned_to__id=assigned_to)

    roles = Role.objects.all()

    # Статистика
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    overdue_tasks = tasks.filter(is_completed=False, due_date__lt=timezone.now()).count()
    completed_percent = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    # Календарные задачи (для FullCalendar)
    calendar_tasks = []
    for task in tasks:
        if task.due_date:
            calendar_tasks.append({
                "title": task.title,
                "start": task.due_date.isoformat(),
                "url": reverse('tasks:task_detail', args=[task.id]),
                "color": "#F44336" if task.due_date < timezone.now() and not task.is_completed
                         else "#4CAF50" if task.is_completed
                         else "#FFC107"
            })

    return render(request, 'tasks/team_detail.html', {
        'team': team,
        'members': members,
        'tasks': tasks,
        'is_captain': is_captain,
        'is_founder': is_founder,
        'all_users': all_users,
        'current_users': current_users,
        'form': form,
        'user': request.user,
        'roles': roles,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'completed_percent': completed_percent,
        'calendar_tasks_json': json.dumps(calendar_tasks, cls=DjangoJSONEncoder),  # 👈 добавлено
    })

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    team = task.team
    user = request.user

    is_member = TeamMembership.objects.filter(user=user, team=team).exists()
    is_founder = user == team.startup.founder
    if not (is_member or is_founder):
        return HttpResponseForbidden()

    comments = task.comments.select_related('author').order_by('-created_at')
    activities = task.activities.select_related('user').order_by('-timestamp')
    subtasks = task.subtasks.select_related('assigned_to').order_by('-created_at')

    form = TaskCommentForm()
    subtask_form = SubTaskForm()
    subtask_form.fields['assigned_to'].queryset = team.members.all()
   

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            form = TaskCommentForm(request.POST, request.FILES)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.task = task
                comment.author = user
                comment.save()
                log_activity(task, user, 'commented')
                return redirect('tasks:task_detail', task_id=task.id)

        elif 'add_subtask' in request.POST:
            subtask_form = SubTaskForm(request.POST)
            subtask_form.fields['assigned_to'].queryset = team.members.all()
            if subtask_form.is_valid():
                subtask = subtask_form.save(commit=False)
                subtask.task = task
                subtask.save()
                log_activity(task, user, 'added_subtask', subtask=subtask)
                return redirect('tasks:task_detail', task_id=task.id)

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'form': form,
        'comments': comments,
        'activities': activities,
        'team': team,
        'subtasks': subtasks,
        'subtask_form': subtask_form,
        'now': timezone.now(), 
    })

@login_required
def archive_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user != task.created_by and not is_team_captain_or_founder(request.user, task.team):
        return HttpResponseForbidden()

    task.is_archived = True
    task.save()

    log_activity(task, request.user, 'archived')
    messages.success(request, "Задача архивирована.")
    return redirect('tasks:team_detail', team_id=task.team.id)

@login_required
def archived_tasks(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not (TeamMembership.objects.filter(user=request.user, team=team).exists() or request.user == team.startup.founder):
        return HttpResponseForbidden()

    tasks = team.tasks.filter(is_archived=True)

    return render(request, 'tasks/archived_tasks.html', {
        'team': team,
        'tasks': tasks
    })

@login_required
def unarchive_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user != task.created_by and not is_team_captain_or_founder(request.user, task.team):
        return HttpResponseForbidden()

    task.is_archived = False
    task.save()

    log_activity(task, request.user, 'unarchived')
    messages.success(request, "Задача восстановлена из архива.")
    return redirect('tasks:archived_tasks', team_id=task.team.id)

@login_required
def archive_completed_tasks(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not is_team_captain_or_founder(request.user, team):
        return HttpResponseForbidden("Нет доступа.")

    completed_tasks = team.tasks.filter(is_completed=True, is_archived=False)
    for task in completed_tasks:
        task.is_archived = True
        task.save()
        log_activity(task, request.user, 'archived (bulk)')

    messages.success(request, f"Архивировано {completed_tasks.count()} выполненных задач.")
    return redirect('tasks:team_detail', team_id=team.id)
