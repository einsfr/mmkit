

def collect_dict(request_data: dict, prefix: str='extra__', key_name: str='extra_data'):
    """
    Преобразует входные данные из GET- и POST-словарей для сбора отдельных полей в словарь:
    {                                               {
        'extra__param1': 'value1',                      'extra_data': {
        'extra__param2': 'value2',                          'param1': 'value1',
        'non-extra': 'value3',            ====>             'param2': 'value2',
        'another-non-extra': 'value4',                  },
    }                                                   'non-extra': 'value3',
                                                        'another-non-extra': 'value4',
                                                    }
    """
    result = {
        key_name: {}
    }
    for key, value in request_data.items():
        if prefix in key:
            result[key_name][key[len(prefix):]] = value
        else:
            result[key] = value
    return result