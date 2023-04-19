from django.core.exceptions import ValidationError


def validate_nonzero(value):
    if value == 0:
        raise ValidationError(
            ('Время приготовления равное %(value) не возможно'),
            params={'value': value},
        )