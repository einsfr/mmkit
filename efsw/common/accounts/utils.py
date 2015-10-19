from django.contrib.auth.models import User, AnonymousUser


def format_username(user: User=None, username: str=None, first_name: str=None, last_name: str=None):
    """
    Function for formatting user representation on pages
    :param user: Instance of django.contrib.auth.models.User (if given - overrides all other arguments)
    :param username: User's login
    :param first_name: User's first name
    :param last_name: User's last name
    :rtype: str

    Possible formats:

    - <first_name> <last_name>, if first_name and last_name are not None
    - <first_name> (<username>), if first_name and username are not None
    - <last_name> (<username>), if last_name and username are not None
    - <username>, if username only is not None

    """
    if user is not None:
        if isinstance(user, User):
            username = user.username
            first_name = user.first_name
            last_name = user.last_name
        elif isinstance(user, AnonymousUser):
            username = 'anonymous'
            first_name = None
            last_name = None
        else:
            raise ValueError('<user> must be an instance of django.contrib.auth.models.User or '
                             'django.contrib.auth.models.AnonymousUser.')
    if username is None:
        raise ValueError('<username> or <user.username> must not be None.')
    if first_name and last_name:
        return "{0} {1}".format(first_name, last_name)
    elif first_name:
        return "{0} ({1})".format(first_name, username)
    elif last_name:
        return "{0} ({1})".format(last_name, username)
    else:
        return str(username)
