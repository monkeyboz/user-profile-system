from django import template

register = template.Library()

@register.simple_tag
def getclassname(obj):
    return obj.__class__.__name__