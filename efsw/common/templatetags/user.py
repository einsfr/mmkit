from django import template

register = template.Library()


@register.inclusion_tag('common/templatetags/user_menu.html', takes_context=True)
def usermenu(context):
    user = context.get('user')
    if not user:
        return {'tag_not_supported': True}
    return {'user': user}