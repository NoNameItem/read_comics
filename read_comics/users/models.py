from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from utils.fields import ThumbnailImageField


def get_user_image_name(instance, filename):
    return "publisher_logo/{0}_logo.{1}".format(instance.name, filename.split('.')[-1])


class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        UNICORN = 'U', _('Unicorn')
        OTHER = 'O', _('Other')

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Full Name"), blank=True, max_length=255)
    gender = models.CharField(_("Gender"), max_length=1, choices=Gender.choices, default=Gender.UNICORN)
    user_image = ThumbnailImageField(null=True, upload_to=get_user_image_name,
                                     thumb_width=40)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def image_url(self):
        if self.user_image:
            return self.user_image.url
        else:
            return "/static/images/avatars/{0}.png".format(self.gender)

    @property
    def image_thumb_url(self):
        if self.user_image:
            return self.user_image.thumb_url
        else:
            return "/static/images/avatars/{0}_thumb.png".format(self.gender)

    def __str__(self):
        return self.name or self.username
