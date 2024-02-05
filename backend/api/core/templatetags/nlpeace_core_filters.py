from django import template

register = template.Library()

@register.filter
def render_post(post):
    return ' '.join([f'<a href="hashtag_search/{word[1:]}">{word}</a>' if word.startswith('#') else word for word in post.get_words()])
    