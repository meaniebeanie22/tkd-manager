# Generated by Django 4.2.5 on 2023-09-18 00:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0020_remove_award_grading_result_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gradingresult',
            old_name='grading_result',
            new_name='award',
        ),
    ]