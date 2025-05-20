import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .models import Startup, Invite, Role
from .forms import AddUserToStartupForm, StartupForm, RoleForm, UserSearchForm
from .utils import send_invite_email
from users.models import CustomUser
from django.http import JsonResponse
from users.models import CustomUser
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Startup, Role

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
User = get_user_model()


def home(request):
    return render(request, 'home.html')

@login_required
def create_startup(request):
    if not Startup.objects.filter(founder=request.user).exists():  # Проверка, что у пользователя нет стартапа
        if request.method == 'POST':
            startup_form = StartupForm(request.POST, request.FILES)
            if startup_form.is_valid():
                startup = startup_form.save(commit=False)  # Не сохраняем сразу
                startup.founder = request.user  # Устанавливаем основателя вручную
                startup.save()  # Сохраняем
                return redirect('startup:startup_list')
        else:
            startup_form = StartupForm()

        return render(request, 'startup/create_startup.html', {'form': startup_form})

    else:
        messages.info(request, "Вы уже создали стартап. Вы не можете создать новый.")
        return redirect('startup:startup_list')



# Функция для назначения роли пользователю
@login_required
def assign_role(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    if startup.founder != request.user:
        messages.error(request, "Вы не можете изменять роли в этом стартапе.")
        return redirect('startup:startup_detail', startup_id=startup.id)

    if request.method == 'POST':
        role_form = RoleForm(request.POST, startup=startup)  # Передаем startup
        if role_form.is_valid():
            role = role_form.save(commit=False)
            role.startup = startup
            role.save()
            messages.success(request, "Роль успешно назначена!")
            return redirect('startup:startup_detail', startup_id=startup.id)
    else:
        role_form = RoleForm(startup=startup)  # Передаем startup

    return render(request, 'startup/assign_role.html', {'form': role_form, 'startup': startup})


@login_required
def remove_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    startup = role.startup

    if role.user != request.user and startup.founder != request.user:
        messages.error(request, "Вы не можете удалить эту роль.")
        return redirect('startup:startup_detail', startup.id)  # ← Здесь передаем id без именованного аргумента

    role.delete()
    messages.success(request, "Роль успешно удалена!")

    return redirect('startup:startup_detail', startup.id)  # ← Исправленный вызов




# Список стартапов
def startup_list(request):
    startups = Startup.objects.all()
    return render(request, 'startup/startup_list.html', {'startups': startups})

# Детали стартапа
from tasks.models import Team  # Не забудь импортировать Team, если ещё не импортировал

from tasks.models import TeamMembership

@login_required
def startup_detail(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    is_founder = startup.founder == request.user
    
    users = startup.users.all()

    # Получаем команды стартапа
    startup_teams = Team.objects.filter(startup=startup)

    # Присваиваем капитана каждой команде
    for team in startup_teams:
        captain_membership = TeamMembership.objects.filter(team=team, is_captain=True).first()
        team.captain = captain_membership.user if captain_membership else None

    # Присваиваем роли пользователям
    for user in users:
        all_roles = user.role_set.all()
        unique_roles = []
        for role in all_roles:
            if role not in unique_roles:
                unique_roles.append(role)
        user.roles = unique_roles
    
    context = {
        'startup': startup,
        'is_founder': is_founder,
        'users': users,
        'startup_teams': startup_teams,
    }
    
    return render(request, 'startup/startup_detail.html', context)





# Редактирование стартапа


@login_required
def edit_startup(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    # Проверка, что текущий пользователь — основатель стартапа
    if startup.founder != request.user:
        messages.error(request, "У вас нет прав редактировать этот стартап.")
        return redirect('startup:startup_list')

    if request.method == 'POST':
        startup_form = StartupForm(request.POST, request.FILES, instance=startup)
        if startup_form.is_valid():
            startup_form.save()  # Поле founder не меняем, оно уже установлено
            messages.success(request, "Стартап успешно обновлен!")
            return redirect('startup:startup_detail', startup_id=startup.id)
    else:
        startup_form = StartupForm(instance=startup)

    return render(request, 'startup/edit_startup.html', {'form': startup_form, 'startup': startup})





@login_required
def delete_startup(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    if startup.founder != request.user:
        messages.error(request, "У вас нет прав удалить этот стартап.")
        return redirect('startup_list')
    
    startup.delete()
    messages.success(request, "Стартап был успешно удален.")
    return redirect('startup:startup_list')



@login_required
def add_user_to_startup(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    # Проверяем, что текущий пользователь является основателем стартапа
    if startup.founder != request.user:
        messages.error(request, "У вас нет прав добавлять участников в этот стартап.")
        return redirect('startup:startup_list')

    if request.method == 'POST':
        form = AddUserToStartupForm(request.POST, instance=startup)
        if form.is_valid():
            form.save()
            messages.success(request, "Участники успешно добавлены!")
            return redirect('startup_detail', startup_id=startup.id)
    else:
        form = AddUserToStartupForm(instance=startup)

    return render(request, 'startup/add_user_to_startup.html', {'form': form, 'startup': startup})



@login_required
def search_users(request, startup_id):
    form = UserSearchForm(request.GET)
    users = CustomUser.objects.exclude(id=request.user.id)  # Исключаем текущего пользователя

    if form.is_valid():
        query = form.cleaned_data.get('query')
        profession = form.cleaned_data.get('profession')

        if query:
            users = users.filter(username__icontains=query)  # Поиск по имени
        if profession:
            users = users.filter(profession=profession)  # Поиск по профессии

    return render(request, 'startup/user_search.html', {'form': form, 'users': users, 'startup_id': startup_id})



@login_required
def invite_user(request, user_id, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    invited_user = get_object_or_404(User, id=user_id)

    # Проверяем, является ли текущий пользователь основателем стартапа
    if startup.founder != request.user:
        messages.error(request, "Вы не можете приглашать участников в этот стартап.")
        return redirect('startup:search_users', startup_id=startup.id)

    # Создаём приглашение
    token = get_random_string(length=32)
    invite = Invite.objects.create(startup=startup, user=invited_user, token=token)

    # Отправляем приглашение
    send_invite_email(invite)  # Передаем только один объект invite

    messages.success(request, f'Приглашение отправлено пользователю {invited_user.username}')
    
    # Оставляем пользователя на странице поиска
    return redirect('startup:search_users', startup_id=startup.id)


@login_required
def accept_invite(request, token):
    # Получаем приглашение по токену
    invite = get_object_or_404(Invite, token=token)

    # Проверяем, было ли уже принято это приглашение
    if invite.accepted:
        messages.info(request, "Это приглашение уже было принято.")
        return redirect('startup:startup_list')  # Перенаправление на страницу стартапов

    # Принятие приглашения
    invite.accepted = True
    invite.save()

    # Добавляем пользователя в стартап
    startup = invite.startup
    startup.users.add(invite.user)
    startup.save()

    messages.success(request, f"Вы успешно присоединились к стартапу {startup.name}")
    
    # Перенаправляем на страницу стартапа
    return redirect('startup:startup_detail', startup_id=startup.id)



def autocomplete_profession(request):
    if 'term' in request.GET:
        professions = CustomUser.objects.filter(profession__icontains=request.GET.get('term')).values_list('profession', flat=True).distinct()
        return JsonResponse(list(professions), safe=False)
    return JsonResponse([], safe=False)

@login_required
def remove_user_from_startup(request, startup_id, user_id):
    startup = get_object_or_404(Startup, id=startup_id)

    if startup.founder != request.user:
        return redirect('startup:startup_detail', startup.id)

    user = get_object_or_404(User, id=user_id)

    # Удаляем все роли пользователя в этом стартапе
    Role.objects.filter(startup=startup, user=user).delete()

    # Если у тебя есть связь ManyToMany, можно удалить пользователя так:
    startup.users.remove(user)

    return redirect('startup:startup_detail', startup.id)




