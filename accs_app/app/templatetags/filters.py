import json
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary:
        dictionary = json.loads(dictionary)
        return dictionary.get(key, "Unknown")
    return ""
