# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Message
from startup.models import Startup
from .forms import MessageForm

@login_required
def startup_chat(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    # Получаем все сообщения стартапа
    messages = startup.messages.all()

    # Обработка отправки сообщений
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.startup = startup
            message.save()
            return redirect('startup_chat', startup_id=startup.id)
    else:
        form = MessageForm()

    return render(request, 'chat/startup_chat.html', {
        'startup': startup,
        'messages': messages,
        'form': form
    })
