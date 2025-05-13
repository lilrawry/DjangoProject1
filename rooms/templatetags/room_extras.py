from django import template
import json

register = template.Library()

@register.filter
def parse_json(value):
    """Parse a JSON string into a Python object."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return value 