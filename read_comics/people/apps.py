from django.apps import AppConfig
from watson import search as watson

from . import search_adapters


class PeopleConfig(AppConfig):
    name = 'read_comics.people'

    def ready(self):
        person_model = self.get_model('Person')
        watson.register(
            person_model,
            search_adapters.PersonSearchAdapter,
            store=('name', 'short_description', 'thumb_url', 'birth_date', 'death_date', 'hometown', 'country')
        )
