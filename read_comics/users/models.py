from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from utils import logging
from utils.fields import ThumbnailImageField


logger = logging.getLogger(__name__)


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
    name = models.CharField(_("Full name"), blank=True, max_length=255)
    gender = models.CharField(_("Gender"), max_length=1, choices=Gender.choices, default=Gender.UNICORN)
    _user_image = ThumbnailImageField(null=True, upload_to=get_user_image_name,
                                      thumb_width=40)
    bio = models.CharField(_("Bio"), blank=True, max_length=1000)
    birth_date = models.DateField(_("Birth date"), null=True, blank=True)
    show_email = models.BooleanField(_("Show email in profile"), default=False)
    last_active = models.DateTimeField(_("Last active"), null=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def image_url(self):
        if self._user_image:
            return self._user_image.url
        else:
            return "/static/images/avatars/{0}.png".format(self.gender)

    @property
    def image_thumb_url(self):
        if self._user_image:
            return self._user_image.thumb_url
        else:
            return "/static/images/avatars/{0}_thumb.png".format(self.gender)

    def __str__(self):
        return self.name or self.username.title()

    @logging.logged(logger)
    def save(self, *args, **kwargs):
        if not self.name:
            if self.first_name and self.last_name:
                self.name = "%s %s" % (self.first_name, self.last_name)
            elif self.first_name:
                self.name = self.first_name
            elif self.last_name:
                self.name = self.last_name
        super(User, self).save(*args, **kwargs)
