# Generated by Django 3.2.13 on 2023-03-05 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('free', '0035_auto_20230212_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='result_type',
            field=models.CharField(choices=[('f', 'Final'), ('p', 'Partial')], max_length=1, verbose_name='Result type'),
        ),
    ]
