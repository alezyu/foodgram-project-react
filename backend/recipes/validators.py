import re
from django.core.exceptions import ValidationError


def validate_hex(value):
    pattern = r'^#[0-9a-fA-F]{6}$'
    if not re.match(pattern, value):
        raise ValidationError('Введите цвет в hex-формате, например #FFFFFF')
