# Generated by Django 5.0 on 2024-01-01 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0057_alter_gradinginvite_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gradinginvite',
            name='grading_date',
        ),
        migrations.AddField(
            model_name='gradinginvite',
            name='grading_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
