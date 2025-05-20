from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from startup.views import home


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home, name='home'),
    path("users/", include("users.urls")),
    path('startup/', include("startup.urls")),
    path('news/', include("news.urls")),
    path('chat/', include('chat.urls')),
    path('tasks/', include('tasks.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)