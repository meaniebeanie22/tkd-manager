# Generated by Django 5.0 on 2024-01-02 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0065_alter_gradinginvite_grading_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grading',
            options={'ordering': ['-grading_datetime', 'grading_type']},
        ),
        migrations.AlterModelOptions(
            name='gradingresult',
            options={'ordering': ['grading__grading_datetime', '-forbelt', 'grading__grading_type', 'member__idnumber']},
        ),
    ]
