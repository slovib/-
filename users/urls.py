from django.urls import path, reverse_lazy
from .views import register, profile_view, profile_update
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

app_name = 'users'

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("password_reset/", PasswordResetView.as_view(
    template_name="users/password_reset.html",
    email_template_name="users/password_reset_email.txt",  # текстовая версия
    html_email_template_name="users/password_reset_email.html",  # HTML-версия
    success_url=reverse_lazy('users:password_reset_done')
), name="password_reset"),


    path("password_reset/done/", PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html"
    ), name="password_reset_confirm"),

    path("reset/done/", PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"
    ), name="password_reset_complete"),

    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_update, name="profile_edit"),
]
