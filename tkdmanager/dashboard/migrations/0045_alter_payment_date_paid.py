# Generated by Django 4.1.4 on 2023-12-27 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0044_paymenttype_standard_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date_paid',
            field=models.DateTimeField(null=True),
        ),
    ]
