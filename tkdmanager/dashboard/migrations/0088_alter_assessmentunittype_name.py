# Generated by Django 5.0.1 on 2024-02-14 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0087_assessmentunittype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentunittype',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
