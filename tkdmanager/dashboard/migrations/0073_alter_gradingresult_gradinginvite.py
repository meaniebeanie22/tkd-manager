# Generated by Django 5.0 on 2024-01-08 17:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0072_alter_class_type_alter_grading_grading_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradingresult',
            name='gradinginvite',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.gradinginvite', verbose_name='Grading Invite'),
        ),
    ]
