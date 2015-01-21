from django import template
from django.db import models

register = template.Library()

# http://stackoverflow.com/questions/14496978/fields-verbose-name-in-templates


def _prepare_instance(instance):
    if isinstance(instance, models.Model):
        obj = instance
    elif hasattr(instance, '__iter__') and len(instance) > 0 and isinstance(instance[0], models.Model):
        obj = instance[0]
    else:
        obj = None
    return obj


@register.simple_tag()
def verbose_name(instance, plural=False, capitalize=True):
    obj = _prepare_instance(instance)
    if obj is not None:
        if plural:
            try:
                result = obj._meta.verbose_name_plural
            except:
                result = ''
        else:
            try:
                result = obj._meta.verbose_name
            except:
                result = ''
    else:
        result = ''
    if result and capitalize:
        result = result.capitalize()
    return result


@register.simple_tag()
def field_verbose_name(instance, field_name, capitalize=True):
    obj = _prepare_instance(instance)
    if obj is not None:
        try:
            result = obj._meta.get_field(field_name).verbose_name
        except:
            result = ''
    else:
        result = ''
    if result and capitalize:
        result = result.capitalize()
    return result