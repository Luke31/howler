from django import template
from django.utils.safestring import mark_safe
import bleach


register = template.Library()


@register.filter
def strip_except_tags(text, valid_tags=None):
    """
    Escape all HTML tags in string except provided valid tags and return partly-escaped HTML string.

    :param text: ``str`` unsafe html string
    :param valid_tags: ``list()`` Valid tags e.g. ['p', 'a', 'strong', 'em', 'ol', 'ul', 'li']
    :return: ``str`` partly-escaped HTML string
    """
    if valid_tags is None:
        valid_tags = ['em']
    if not isinstance(valid_tags, list):
        valid_tags = valid_tags.split(',')
    text = bleach.clean(text, valid_tags)
    return mark_safe(text)
