from django import forms

from users.models import CustomUser
from .models import Application, Startup, Role
from django.contrib.auth import get_user_model
from django import forms
from .models import Role, Startup
from django import forms
from .models import Role
from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
User = get_user_model()


class StartupForm(forms.ModelForm):
    class Meta:
        model = Startup
        fields = ['name', 'description', 'logo']
    

class AddUserToStartupForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Startup
        fields = ['users']


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['user', 'role_name']  # Исправили 'role' на 'role_name'

    def __init__(self, *args, **kwargs):
        startup = kwargs.pop('startup', None)
        super().__init__(*args, **kwargs)
        if startup:
            self.fields['user'].queryset = startup.users.all()  # Фильтруем пользователей, связанных со стартапом



class UserSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label="Поиск по имени")
    profession = forms.ChoiceField(
        choices=[('', 'Все профессии')] + CustomUser.PROFESSION_CHOICES,
        required=False,
        label="Профессия"
    )