from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    

    class Meta:
        model = CustomUser
        fields = ("username", "email",  "password1", "password2")

from django import forms
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    """Форма для редактирования профиля"""
    class Meta:
        model = CustomUser
        fields = ["avatar", "bio", "skills", 'profession']
