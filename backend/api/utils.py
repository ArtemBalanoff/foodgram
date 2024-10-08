from io import BytesIO

from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from recipes.models import Ingredient


def generate_pdf_in_memory(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    pdfmetrics.registerFont(TTFont('MainFont',
                                   'foodgram_backend/fonts/Duality.otf'))
    c.setFont("MainFont", 12)
    width, height = letter
    text_object = c.beginText(50, height - 50)
    text_object.textLines(text)
    c.drawText(text_object)
    c.save()
    buffer.seek(0)
    return buffer


def convert_dict_to_text(dict):
    text = ''
    for name, (amount, unit) in dict.items():
        text += f'{name} - {amount} {unit}\n'
    return text


def create_shopping_cart_list(request):
    measurement_unit_name_dict = {
        choice[0]: choice[1] for choice
        in Ingredient.MeasurementUnits.choices}
    aggregated_ingredients = request.user.shopping_cart.values(
        'ingredients__ingredient__name',
        'ingredients__ingredient__measurement_unit',
    ).annotate(total_amount=Sum('ingredients__amount'))
    ingredients_dict = {
        item['ingredients__ingredient__name']:
        (item['total_amount'],
            measurement_unit_name_dict.get(
                item['ingredients__ingredient__measurement_unit']))
        for item in aggregated_ingredients}
    text = convert_dict_to_text(ingredients_dict)
    pdf = generate_pdf_in_memory(text)
    return HttpResponse(pdf, content_type='application/pdf')
