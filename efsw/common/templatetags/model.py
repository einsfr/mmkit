from django import template

register = template.Library()

# http://stackoverflow.com/questions/14496978/fields-verbose-name-in-templates


@register.simple_tag()
def verbose_name(instance, plural=False):
    if plural:
        try:
            result = instance._meta.verbose_name_plural
        except:
            result = ''
    else:
        try:
            result = instance._meta.verbose_name
        except:
            result = ''
    return result


@register.simple_tag()
def field_verbose_name(instance, field_name):
    #try:
    result = instance._meta.get_field(field_name).verbose_name
    #except:
    #    result = ''
    return result