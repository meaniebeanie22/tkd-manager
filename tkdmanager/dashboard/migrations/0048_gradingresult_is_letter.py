# Generated by Django 4.1.4 on 2023-12-30 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0047_rename_date_paid_payment_date_paid_in_full'),
    ]

    operations = [
        migrations.AddField(
            model_name='gradingresult',
            name='is_letter',
            field=models.BooleanField(default=False),
        ),
    ]
