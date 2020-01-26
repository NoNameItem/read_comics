from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django_magnificent_messages import notifications
from django.contrib.messages.constants import DEFAULT_LEVELS as DJANGO_DEFAULT_LEVELS
from django_magnificent_messages.constants import DEFAULT_LEVELS as DMM_DEFAULT_LEVELS


class AccountAdapter(DefaultAccountAdapter):
    MESSAGE_LEVEL_MAPPING = {
        DJANGO_DEFAULT_LEVELS["DEBUG"]: DMM_DEFAULT_LEVELS["SECONDARY"],
        DJANGO_DEFAULT_LEVELS["INFO"]: DMM_DEFAULT_LEVELS["INFO"],
        DJANGO_DEFAULT_LEVELS["SUCCESS"]: DMM_DEFAULT_LEVELS["SUCCESS"],
        DJANGO_DEFAULT_LEVELS["WARNING"]: DMM_DEFAULT_LEVELS["WARNING"],
        DJANGO_DEFAULT_LEVELS["ERROR"]: DMM_DEFAULT_LEVELS["ERROR"]
    }

    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        """
        Using django magnificent messages instead of boring standart messages
        """
        if 'django_magnificent_messages' in settings.INSTALLED_APPS or \
                'django_magnificent_messages.apps.DjangoMagnificentMessagesConfig' in settings.INSTALLED_APPS:
            try:
                if message_context is None:
                    message_context = {}
                message = render_to_string(message_template,
                                           message_context).strip()
                if message:
                    notifications.add(request, self.MESSAGE_LEVEL_MAPPING.get(level, level), message, extra=extra_tags)
            except TemplateDoesNotExist:
                pass


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
