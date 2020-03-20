from django.db import models
from utils.models import ComicvineSyncModel


class Character(ComicvineSyncModel):
    name = models.TextField()
    aliases = models.TextField()
    short_description = models.TextField()
    html_description = models.TextField()

    thumb_url = models.URLField(max_length=1000)
    image_url = models.URLField(max_length=1000)
