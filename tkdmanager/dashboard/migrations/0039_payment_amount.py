# Generated by Django 4.1.4 on 2023-12-27 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0038_paymenttype_alter_assessmentunit_grading_result_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Amount to be paid, in $', max_digits=7),
        ),
    ]
