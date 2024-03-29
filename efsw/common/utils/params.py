import re

from efsw.common.http.response import JsonWithStatusResponse
from efsw.common import errors


class WrongCriteriaException(Exception):
    pass


class RequiredParameterIsMissingException(Exception):

    def __init__(self, *args, param_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_name = param_name


class UnexpectedParameterValueException(Exception):

    def __init__(self, *args, param_name=None, param_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_name = param_name
        self.param_value = param_value


def parse_params(params_dict: dict, **params_criteria):
    """
    Function for parsing request parameters in request.GET or request.POST dictionaries.
    :param params_dict: Request parameters dictionary
    :param params_criteria: Parsing rules
    :raise RequiredParameterIsMissingException: If a required parameter is missing
    :raise UnexpectedParameterValueException: If a parameter has invalid value

    The parsing rules are passed via keyword arguments - request parameter as an argument's name and a parsing rule
    as its value. A value could be:

        - *None* is used for optional parameters. Default value for absent parameters: '' (an empty string).
        - *String* is used as a regular expression for required parameters.
        - *Callable* is used for complex rules. If parameter is missing - default value ('') will be used. If returned
          value is False - exception will be raised; if True - parameter's value will be passed to the result dict.

    Values in the result dictionary are always strings, as in request.GET and request.POST dictionaries.
    """
    result = {}
    for n, c in params_criteria.items():
        if c is None:
            # Значит, этот параметр может быть, а может и не быть, но если он есть, его значение нужно получить
            result[n] = params_dict.get(n, '')
        elif type(c) is str:
            # Значит, там строка, которая будет рассматриваться как регулярное выражение
            if n not in params_dict:
                raise RequiredParameterIsMissingException('Required parameter {0} is missing.'.format(n), param_name=n)
            if re.match(c, params_dict[n]) is None:
                raise UnexpectedParameterValueException(
                    'Parameter {0} has unexpected value: {1}.'.format(n, params_dict[n]), param_name=n,
                    param_value=params_dict[n]
                )
            result[n] = params_dict[n]
        elif callable(c):
            # Значит, там какая-то функция, True - значение параметра верное, False - нет
            value = params_dict.get(n, '')
            if c(value):
                result[n] = value
            else:
                raise UnexpectedParameterValueException('Parameter {0} has unexpected value: {1}.'.format(n, value),
                                                        param_name=n, param_value=value)
        else:
            raise WrongCriteriaException(
                'Wrong criterion type: {0} is a {1}. None, str or callable expected.'.format(n, type(c))
            )
    return result


def parse_params_or_get_json_error(params_dict, **kwargs):
    try:
        return parse_params(params_dict, **kwargs)
    except RequiredParameterIsMissingException as e:
        return JsonWithStatusResponse.error(errors.REQUIRED_REQUEST_PARAMETER_IS_MISSING.format(e.param_name),
                                            'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
    except UnexpectedParameterValueException as e:
        return JsonWithStatusResponse.error(
            errors.UNEXPECTED_REQUEST_PARAMETER_VALUE.format(e.param_name, e.param_value),
            'UNEXPECTED_REQUEST_PARAMETER_VALUE'
        )
