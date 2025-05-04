from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path('startup/', include("startup.urls")),
    path('news/', include("news.urls")),
    path('chat/', include('chat.urls')),
    path('tasks/', include('tasks.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)