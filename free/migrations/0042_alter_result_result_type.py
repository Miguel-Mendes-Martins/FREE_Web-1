# Generated by Django 3.2.13 on 2023-04-17 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('free', '0041_alter_result_result_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='result_type',
            field=models.CharField(choices=[('f', 'Final'), ('p', 'Partial')], max_length=1, verbose_name='Result type'),
        ),
    ]