# Generated by Django 4.2.5 on 2023-09-18 01:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_alter_assessmentunit_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['-belt', 'idnumber']},
        ),
    ]
