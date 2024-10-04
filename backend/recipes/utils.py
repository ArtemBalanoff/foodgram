from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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
