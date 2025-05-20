# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Message
from startup.models import Startup
from .forms import MessageForm

@login_required
def startup_chat(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    # Проверка, что пользователь в стартапе
    if request.user != startup.founder and request.user not in startup.users.all():
        return HttpResponseForbidden("Вы не являетесь участником этого стартапа.")

    messages = startup.messages.all().order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.startup = startup
            message.save()
            return redirect('chat:startup_chat', startup_id=startup.id)
    else:
        form = MessageForm()

    return render(request, 'chat/startup_chat.html', {
        'startup': startup,
        'messages': messages,
        'form': form,
    })

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    startup = message.startup

    # Проверяем, что пользователь автор сообщения или основатель стартапа
    if request.user != message.user and request.user != startup.founder:
        return HttpResponseForbidden("Вы не можете удалять это сообщение.")

    if request.method == 'POST':
        message.delete()
        return redirect('chat:startup_chat', startup_id=startup.id)
    
    # На GET можно просто редиректить назад
    return redirect('chat:startup_chat', startup_id=startup.id)
