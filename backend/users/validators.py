from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(f'Имя "{str(username)}" запрещено.')
    regex_validator = RegexValidator(
        regex='^[a-zA-Z0-9/.+-]+$',
        message='Разрешены буквы, цифры и символы ., @, +, - ',
    )