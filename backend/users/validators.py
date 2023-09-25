from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(f'Использовать имя "{str(username)}" запрещено.')