# Generated by Django 4.2.16 on 2024-09-23 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='measure_unit',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='cook_duration',
        ),
        migrations.AddField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(default=None, verbose_name='Время приготовления'),
            preserve_default=False,
        ),
    ]
