# Generated by Django 5.0.1 on 2024-02-11 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0081_member_properties_alter_memberproperty_member'),
    ]

    operations = [
        migrations.CreateModel(
            name='Belt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.PositiveSmallIntegerField(unique=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
    ]
