# Generated by Django 4.2.4 on 2023-12-06 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0034_alter_class_instructors_alter_class_students'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='type',
            field=models.CharField(choices=[('MS', 'Musketeers'), ('JR', 'Juniors'), ('SN', 'Seniors'), ('BB', 'Black Belt'), ('BJ', 'BJJ/MMA'), ('BO', 'Boxing'), ('BK', 'BJJ for Kids'), ('WE', 'Weapons'), ('FC', 'Fight Class')], max_length=2),
        ),
        migrations.AlterField(
            model_name='gradingresult',
            name='type',
            field=models.CharField(choices=[('MS', 'Musketeers'), ('JR', 'Juniors'), ('SN', 'Seniors'), ('BB', 'Black Belt'), ('BJ', 'BJJ/MMA'), ('BO', 'Boxing'), ('BK', 'BJJ for Kids'), ('WE', 'Weapons'), ('FC', 'Fight Class')], max_length=2),
        ),
    ]