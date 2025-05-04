from django.urls import path
from .views import create_news, news_list, startup_detail

app_name = 'news'

urlpatterns = [
    path("", news_list, name="news_list"),
    path("<int:startup_id>/create/", create_news, name="create_news"),
    path('startup/<int:startup_id>/', startup_detail, name='startup_detail'),
]
