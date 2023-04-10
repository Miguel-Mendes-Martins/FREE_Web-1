# Generated by Django 3.2.13 on 2023-03-05 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_mc', '0002_sitting_decimal_precision'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='rounding',
            field=models.BooleanField(default=False, help_text='Will this question be rounded to a decimal case', verbose_name='Rounding'),
        ),
    ]
