from django.db.models import CharField
from django.core.exceptions import ValidationError


class ColorField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value[0] != '#':
            raise ValidationError('Значение цвета должно начинаться с символа "#".')
        if len(value) != 7:
            raise ValidationError('Значение цвета должно иметь в длину ровно 7 символов.')
        for c in value[1:8]:
            if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
                raise ValidationError('В значении цвета допустимы только цифры от 0 до 9 и буквы от "a" до "f".')

