from django.apps import AppConfig
from watson import search as watson

from . import search_adapters


class PublishersConfig(AppConfig):
    name = 'read_comics.publishers'

    def ready(self):
        publisher_model = self.get_model('Publisher')
        watson.register(
            publisher_model,
            search_adapters.PublisherSearchAdapter,
            store=('name', 'short_description', 'thumb_url')
        )
