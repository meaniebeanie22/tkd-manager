# Generated by Django 5.0.2 on 2024-02-11 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0085_add_belts'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['-belt__degree', 'last_name']},
        ),
    ]
