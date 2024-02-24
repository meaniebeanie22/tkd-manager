# Generated by Django 5.0.2 on 2024-02-21 05:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0095_remove_grading_style_remove_gradinginvite_style_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberpropertytype',
            name='style',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dashboard.style'),
        ),
        migrations.AddField(
            model_name='memberpropertytype',
            name='teacher_property',
            field=models.BooleanField(default=False),
        ),
    ]