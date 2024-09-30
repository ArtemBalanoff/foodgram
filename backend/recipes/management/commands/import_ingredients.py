import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из файла ingredients.json'

    def handle(self, *args, **kwargs):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
        file_path = os.path.join(BASE_DIR, 'data', 'ingredients.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            measurement_unit_choices = Ingredient.MeasurementUnits.choices
            measurement_unit_dict = {
                choice[1]: choice[0] for choice in measurement_unit_choices}
            for item in data:
                Ingredient.objects.bulk_create(
                    [Ingredient(name=item['name'].capitalize(),
                                measurement_unit=measurement_unit_dict[
                                    item['measurement_unit']])])
            self.stdout.write('Импорт ингредиентов прошел успешно.')
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                'Файл ingredients.json не найден'))
