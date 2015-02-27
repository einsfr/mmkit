from django import template

register = template.Library()


@register.inclusion_tag('common/templatetags/account_menu.html', takes_context=True)
def accountmenu(context):
    user = context.get('user')
    if not user:
        return {'tag_not_supported': True}
    return {'user': user}