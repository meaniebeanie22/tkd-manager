# Generated by Django 4.2.4 on 2023-12-05 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0032_class_date_alter_class_end_alter_class_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='address_line_1',
            field=models.CharField(blank=True, help_text='Unit, Street Number and Name', max_length=200),
        ),
    ]
