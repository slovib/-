from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileUpdateForm

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

@login_required
def profile_view(request):
    """Страница профиля пользователя"""
    return render(request, "users/profile.html")

@login_required
def profile_update(request):
    """Обновление профиля пользователя"""
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш профиль успешно обновлён!")
            return redirect("users:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, "users/profile_edit.html", {"form": form})
