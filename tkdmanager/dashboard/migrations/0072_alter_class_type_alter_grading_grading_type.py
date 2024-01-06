# Generated by Django 5.0 on 2024-01-05 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0071_rename_grading_invite_gradingresult_gradinginvite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='type',
            field=models.CharField(choices=[('MS', 'Musketeers'), ('JR', 'Juniors'), ('SN', 'Seniors'), ('JS', 'Juniors/Seniors All'), ('JD', 'Juniors/Seniors Beginner-Blue'), ('JF', 'Juniors/Seniors Red-Black'), ('PA', 'TKD Patterns/Grading'), ('BB', 'Black Belts'), ('BJ', 'BJJ/MMA'), ('BO', 'Boxing'), ('BK', 'BJJ for Kids'), ('WE', 'Weapons'), ('FC', 'Fight Class')], max_length=2),
        ),
        migrations.AlterField(
            model_name='grading',
            name='grading_type',
            field=models.CharField(choices=[('MS', 'Musketeers'), ('JR', 'Juniors'), ('SN', 'Seniors'), ('JS', 'Juniors/Seniors All'), ('JD', 'Juniors/Seniors Beginner-Blue'), ('JF', 'Juniors/Seniors Red-Black'), ('PA', 'TKD Patterns/Grading'), ('BB', 'Black Belts'), ('BJ', 'BJJ/MMA'), ('BO', 'Boxing'), ('BK', 'BJJ for Kids'), ('WE', 'Weapons'), ('FC', 'Fight Class')], max_length=2),
        ),
    ]