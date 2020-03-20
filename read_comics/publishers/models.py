from django.db import models
from django_extensions.db.fields import AutoSlugField

from utils.models import ComicvineSyncModel, slugify_function


class Publisher(ComicvineSyncModel):
    name = models.TextField()
    aliases = models.TextField(null=True)
    short_description = models.TextField(null=True)
    html_description = models.TextField(null=True)

    thumb_url = models.URLField(max_length=1000, null=True)
    image_url = models.URLField(max_length=1000, null=True)

    slug = AutoSlugField(populate_from=["name"], slugify_function=slugify_function)

    class Meta:
        ordering = ("name", )

    def __str__(self):
        return "[Publisher] %s (%d)" % (self.name, self.pk)
