# Generated by Django 5.0 on 2024-01-03 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0066_alter_grading_options_alter_gradingresult_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gradinginvite',
            options={'ordering': ['grading__grading_datetime', '-forbelt', 'grading__grading_type', 'member__idnumber']},
        ),
        migrations.AlterModelOptions(
            name='gradingresult',
            options={'ordering': ['-grading__grading_datetime', '-forbelt', 'grading__grading_type', 'member__idnumber']},
        ),
    ]
