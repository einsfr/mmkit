from django import template

from efsw.accounts.utils import format_username

register = template.Library()


@register.inclusion_tag('accounts/templatetags/account_menu.html', takes_context=True)
def accountmenu(context):
    user = context.get('user')
    if not user:
        return {'tag_not_supported': True}
    return {
        'user': user,
        'user_repr': format_username(user)
    }
