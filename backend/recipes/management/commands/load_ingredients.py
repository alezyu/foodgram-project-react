import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Выгружаю ингредиенты...')
        ingredients = json.loads(
            (settings.BASE_DIR / 'data' / 'ingredients.json').read_text()
        )
        for ingredient in ingredients:
            if Ingredients.objects.filter(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
            ).exists():
                print(f'Найден дубликат {ingredient["name"]}...')
                continue
            Ingredients.objects.create(**ingredient)

        print('Данные выгружены.')
