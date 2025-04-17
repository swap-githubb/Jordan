from django import template

register = template.Library()

@register.filter(name='absval')
def absval(value):
    """Return the absolute value of the argument."""
    try:
        return abs(value)
    except Exception:
        return value
