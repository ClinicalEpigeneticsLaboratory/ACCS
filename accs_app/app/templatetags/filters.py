import json
from pathlib import Path
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary:
        dictionary = json.loads(dictionary)
        return dictionary.get(key, "Unknown")
    return ""


@register.filter
def filename(value):
    return Path(value.name).name
