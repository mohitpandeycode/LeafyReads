import re
from django import template

register = template.Library()

CLOUDINARY_PATTERN = re.compile(
    r'(https://res\.cloudinary\.com/[^/]+/image/upload/)([^"]+)'
)

TRANSFORMATION = "w_800,q_auto,f_auto,fl_progressive/"

@register.filter
def optimize_cloudinary_images(html):
    if not html:
        return html

    def replacer(match):
        base = match.group(1)
        rest = match.group(2)

        # ✅ Skip ONLY if our exact transformation already exists
        if rest.startswith(TRANSFORMATION):
            return match.group(0)

        return f"{base}{TRANSFORMATION}{rest}"

    return CLOUDINARY_PATTERN.sub(replacer, html)
