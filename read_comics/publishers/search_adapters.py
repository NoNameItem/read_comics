from watson import search as watson
from django.utils.html import strip_tags


class PublisherSearchAdapter(watson.SearchAdapter):

    def get_title(self, obj):
        return obj.name + "\n" + obj.aliases

    def get_description(self, obj):
        return obj.short_description

    def get_content(self, obj):
        return strip_tags(obj.html_description)
