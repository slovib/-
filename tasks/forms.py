from django import forms
from .models import Team, Task, TaskComment

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

from django import forms
from .models import Task
from django.utils import timezone

PRIORITY_CHOICES = [
    ('low', 'Низкий'),
    ('medium', 'Средний'),
    ('high', 'Высокий'),
]

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Дедлайн"
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        label="Приоритет"
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'due_date']

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            raise forms.ValidationError("Дедлайн не может быть в прошлом.")
        return due_date


from django import forms
from .models import TaskComment

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['text', 'file']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Оставьте комментарий...'}),
        }

class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'Все'), ('done', 'Выполненные'), ('active', 'В процессе')],
        required=False,
        label='Статус'
    )
    priority = forms.ChoiceField(
        choices=[('', 'Все')] + list(Task.PRIORITY_CHOICES),
        required=False,
        label='Приоритет'
    )
    assigned_to = forms.ChoiceField(
        required=False,
        label='Назначено',
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        team = kwargs.pop('team')
        is_manager = kwargs.pop('is_manager', False)

        super().__init__(*args, **kwargs)

        if is_manager:
            members = team.members.all()
            self.fields['assigned_to'].choices = [('', 'Все')] + [(m.id, m.username) for m in members]
        else:
            self.fields['assigned_to'].choices = [
                ('', 'Все'),
                ('me', 'Мне назначено')
            ]


from django import forms
from .models import SubTask

from django import forms
from .models import SubTask

from django import forms
from django.utils import timezone
from .models import SubTask

class SubTaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Дедлайн"
    )

    class Meta:
        model = SubTask
        fields = ['title', 'description', 'assigned_to', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Описание подзадачи...'}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            raise forms.ValidationError("Дедлайн не может быть в прошлом.")
        return due_date

from django import forms
from .models import TeamMembership

from django import forms
from .models import TeamMembership, Role

class TeamMembershipForm(forms.ModelForm):
    class Meta:
        model = TeamMembership
        fields = ['user', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roles = Role.objects.all()
        self.fields['role'].choices = [('', 'Выберите роль')] + [(role.id, role.name) for role in roles]


