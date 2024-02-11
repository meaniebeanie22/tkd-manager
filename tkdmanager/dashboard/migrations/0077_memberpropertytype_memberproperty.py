# Generated by Django 5.0.1 on 2024-02-11 10:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0076_remove_paymenttype_recurring_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberPropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('searchable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MemberProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('member', models.ManyToManyField(related_name='properties', to='dashboard.member')),
                ('propertytype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.memberpropertytype', verbose_name='Property Type')),
            ],
        ),
    ]
