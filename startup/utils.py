from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator

# В файле utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_invite_email(invite):
    # URL для перехода по ссылке
    accept_url = f"{settings.SITE_URL}/startup/accept_invite/{invite.token}/"

    subject = f"Приглашение в стартап {invite.startup.name}"
    message = f"Привет, {invite.user.username}!\n\nВы были приглашены в стартап {invite.startup.name}. Перейдите по следующей ссылке, чтобы присоединиться:\n\n{accept_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [invite.user.email])



