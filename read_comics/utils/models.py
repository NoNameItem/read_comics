from django.db import models
from django.utils import timezone
from model_utils import FieldTracker
from slugify import slugify


def slugify_function(content):
    return slugify(content, lowercase=False)


class ComicvineSyncModel(models.Model):
    comicvine_id = models.IntegerField(unique=True)
    comicvine_url = models.URLField(max_length=1000)
    comicvine_matched = models.BooleanField(default=False)

    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now_add=True)

    tracker = FieldTracker()

    class Meta:
        abstract = True

    def pre_save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.pre_save(force_insert, force_update, using, update_fields)
        if self.tracker.changed():
            self.modified_dt = timezone.now()
        self.save(force_insert, force_update, using, update_fields)
