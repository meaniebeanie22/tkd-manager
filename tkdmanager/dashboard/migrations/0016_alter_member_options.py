# Generated by Django 4.2.4 on 2023-09-12 00:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_rename_id_number_member_idnumber'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['idnumber']},
        ),
    ]
