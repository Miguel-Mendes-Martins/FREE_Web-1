# Generated by Django 3.2.13 on 2023-01-03 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lti_provider', '0007_alter_lticoursecontext_lms_course_context'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lticoursecontext',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
