import re

from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()

pattern = r'(#[^#\s]+)'

@register.filter
@stringfilter
def render_post(content):
    return ' '.join([f'<a href="hashtag_search/{word[1:]}">{word}</a>' if word.startswith('#') else word for word in re.split(pattern, content) ])
    