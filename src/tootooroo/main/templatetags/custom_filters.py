import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

GYAZO_REGEX = re.compile(r'(https://i.gyazo.com/[a-z0-9]+)')

@register.filter
def gyazo_to_img(value):
    def replace_gyazo(match):
        url = match.group(1)
        # img_url = url + '.png'
        return f'<img src="{url}" alt="Gyazo Image" style="max-width: 100%;">'

    
    return mark_safe(GYAZO_REGEX.sub(replace_gyazo, value))
