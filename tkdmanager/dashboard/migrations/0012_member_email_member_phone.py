# Generated by Django 4.1.4 on 2023-09-10 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_rename_gradingresult_assessmentunit_grading_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='email',
            field=models.EmailField(default='example@example.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='phone',
            field=models.CharField(default='0400 000 000', max_length=100),
            preserve_default=False,
        ),
    ]
