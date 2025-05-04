from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import News
from .forms import NewsForm
from startup.models import Startup
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, timedelta
from .models import News
from startup.models import Startup
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, timedelta
from .models import News
from startup.models import Startup


@login_required
def create_news(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    # Проверяем, что пользователь — основатель или контент-менеджер
    if request.user != startup.founder and not request.user.role_set.filter(startup=startup, role_name="Контент-менеджер").exists():
        return redirect("news:news_list")

    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.startup = startup
            news.author = request.user
            news.save()
            return redirect("news:news_list")
    else:
        form = NewsForm()

    return render(request, "news/create_news.html", {"form": form, "startup": startup})

def news_list(request):
    news = News.objects.all()
    startups = Startup.objects.all()

    startup_id = request.GET.get("startup")
    title_query = request.GET.get("title")
    date_filter = request.GET.get("date_filter")

    if startup_id:
        news = news.filter(startup_id=startup_id)

    if title_query:
        news = news.filter(title__icontains=title_query)

    if date_filter:
        days = int(date_filter)
        date_threshold = now() - timedelta(days=days)
        news = news.filter(created_at__gte=date_threshold)

    return render(request, "news/news_list.html", {"news": news, "startups": startups})


def startup_detail(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    news = News.objects.filter(startup=startup)

    title_query = request.GET.get("title")
    date_filter = request.GET.get("date_filter")

    if title_query:
        news = news.filter(title__icontains=title_query)

    if date_filter:
        days = int(date_filter)
        date_threshold = now() - timedelta(days=days)
        news = news.filter(created_at__gte=date_threshold)

    return render(request, "news/startup_detail.html", {"startup": startup, "news": news})


