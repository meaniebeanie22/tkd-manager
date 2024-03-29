# Generated by Django 5.0.1 on 2024-02-11 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0079_merge_20240211_1134'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'ordering': ['-date', '-start'], 'verbose_name_plural': 'classes'},
        ),
        migrations.AlterModelOptions(
            name='memberproperty',
            options={'verbose_name_plural': 'member properties'},
        ),
        migrations.AlterField(
            model_name='memberproperty',
            name='member',
            field=models.ManyToManyField(blank=True, related_name='properties', to='dashboard.member'),
        ),
    ]
