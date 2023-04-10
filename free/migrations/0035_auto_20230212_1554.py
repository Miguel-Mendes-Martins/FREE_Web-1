# Generated by Django 3.2.13 on 2023-02-12 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('free', '0034_auto_20230212_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apparatus',
            name='parameters',
            field=models.JSONField(blank=True, default=dict, verbose_name='Parameters'),
        ),
        migrations.AlterField(
            model_name='result',
            name='result_type',
            field=models.CharField(choices=[('p', 'Partial'), ('f', 'Final')], max_length=1, verbose_name='Result type'),
        ),
    ]
