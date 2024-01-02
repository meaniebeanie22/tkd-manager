# Generated by Django 5.0 on 2024-01-02 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0063_grading_alter_gradinginvite_grading_datetime_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gradingresult',
            options={'ordering': ['grading__grading_datetime', 'grading__grading_type', '-forbelt', 'member__idnumber']},
        ),
        migrations.RemoveField(
            model_name='gradinginvite',
            name='grading_datetime',
        ),
        migrations.RemoveField(
            model_name='gradinginvite',
            name='grading_type',
        ),
        migrations.RemoveField(
            model_name='gradingresult',
            name='date',
        ),
        migrations.RemoveField(
            model_name='gradingresult',
            name='type',
        ),
        migrations.AlterField(
            model_name='gradingresult',
            name='comments',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
