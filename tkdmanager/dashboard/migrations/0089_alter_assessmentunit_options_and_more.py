# Generated by Django 5.0.1 on 2024-02-14 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0088_alter_assessmentunittype_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assessmentunit',
            options={'ordering': ['unitOLD']},
        ),
        migrations.RenameField(
            model_name='assessmentunit',
            old_name='unit',
            new_name='unitOLD',
        ),
    ]
