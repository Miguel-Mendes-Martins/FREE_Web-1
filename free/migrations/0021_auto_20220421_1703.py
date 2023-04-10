# Generated by Django 3.2.9 on 2022-04-21 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('free', '0020_alter_apparatustype_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='apparatus',
            name='last_online',
            field=models.DateTimeField(auto_now=True, verbose_name='Last ping'),
        ),
        migrations.AlterField(
            model_name='result',
            name='result_type',
            field=models.CharField(choices=[('f', 'Final'), ('p', 'Partial')], max_length=1, verbose_name='Result type'),
        ),
    ]
