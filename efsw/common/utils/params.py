import re


class WrongCriteriaException(Exception):
    pass


class RequiredParameterIsMissing(Exception):
    pass


class WrongParameterValue(Exception):
    pass


def parse_params(params_dict: dict, **params_criteria):
    result = []
    for n, c in params_criteria.items():
        if c is None:
            # Значит, этот параметр может быть, а может и не быть, но если он есть, его значение нужно получить
            result.append(params_dict.get(n, None))
        elif type(c) is str:
            # Значит, там строка, которая будет рассматриваться как регулярное выражение
            value = params_dict.get(n, '')
            if not value:
                raise RequiredParameterIsMissing('Required parameter {0} is missing.'.format(n))
            if re.match(c, value) is None:
                raise WrongParameterValue('Parameter {0} has wrong value: {1}.'.format(n, value))
            result.append(value)
        elif callable(c):
            # Значит, там какая-то функция, True - значение параметра верное, False - нет
            value = params_dict.get(n, None)
            if c(value):
                result.append(value)
            else:
                raise WrongParameterValue('Parameter {0} has wrong value: {1}.'.format(n, value))
        else:
            raise WrongCriteriaException(
                'Wrong criterion type: {0} is a {1}. None, str or callable expected.'.format(n, type(c))
            )
    return result
