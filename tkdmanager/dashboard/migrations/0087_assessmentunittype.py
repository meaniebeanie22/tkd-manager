# Generated by Django 5.0.1 on 2024-02-14 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0086_alter_member_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentUnitType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
    ]
