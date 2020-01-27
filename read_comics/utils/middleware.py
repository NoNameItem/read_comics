import datetime

from django.conf import settings
from django.utils import timezone


class LastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user
        if user.is_authenticated:
            if not user.last_active or \
                    timezone.now() - user.last_active > datetime.timedelta(seconds=settings.LAST_ACTIVE_TIMEOUT):
                user.last_active = timezone.now()
                user.save()

        return response
