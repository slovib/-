from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileUpdateForm
from django.db.models import Q
from startup.models import Startup
from startup.models import Role

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


from django.db.models import Q

@login_required
def profile_view(request):
    user = request.user

    # Стартапы, где у пользователя есть роль
    roles = Role.objects.filter(user=user).select_related('startup')
    startups_with_roles = []

    for role in roles:
        startups_with_roles.append({
            "startup": role.startup,
            "role": role.role_name
        })

    # Стартапы, где пользователь основатель, но у него нет роли
    founded_startups = Startup.objects.filter(founder=user).exclude(id__in=[r["startup"].id for r in startups_with_roles])

    for startup in founded_startups:
        startups_with_roles.append({
            "startup": startup,
            "role": "Основатель"
        })

    return render(request, "users/profile.html", {
        "user": user,
        "startups_with_roles": startups_with_roles,
    })




@login_required
def profile_update(request):
    """Обновление профиля пользователя"""
    user = request.user

    if request.method == "POST":
        if 'remove_avatar' in request.POST:
            user.avatar.delete(save=True)
            messages.success(request, "Аватарка удалена.")
            return redirect("users:profile_edit")

        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш профиль успешно обновлён!")
            return redirect("users:profile")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, "users/profile_edit.html", {"form": form, "user": user})

