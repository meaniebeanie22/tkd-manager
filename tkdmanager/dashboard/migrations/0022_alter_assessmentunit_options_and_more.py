# Generated by Django 4.2.5 on 2023-09-18 01:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_rename_grading_result_gradingresult_award'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assessmentunit',
            options={'ordering': ['unit']},
        ),
        migrations.AlterModelOptions(
            name='gradingresult',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['belt', 'idnumber']},
        ),
    ]
