# Generated by Django 4.1.4 on 2023-12-31 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0050_alter_gradingresult_is_letter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradingresult',
            name='is_letter',
            field=models.BooleanField(default=False),
        ),
    ]
